"""
Organize attachments/ into per-project subfolders (e.g. attachments/AD-PenTest-Images/)
and rewrite Markdown paths in each project's notes.
"""
from __future__ import annotations

import os
import re
import shutil
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATTACHMENTS = ROOT / "attachments"
SKIP_TOP = {".obsidian", "tools", "attachments", ".git"}

PROJECTS = [
    "AD-PenTest",
    "AI-LLM-Security",
    "HTB",
    "Practical-Ethical-Hacking",
    "VAPT",
]

MD_IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
ATTACHMENT_REF_RE = re.compile(
    r"(?<![\w/-])(?:\.\./)*attachments/([^)\s\"']+)",
    re.I,
)
COVER_LINE_RE = re.compile(r"^(cover:\s*)(.+)$", re.M)
HREF_ATTACH_RE = re.compile(
    r'(href=["\'])((?:\.\./)*attachments/([^"\']+))(["\'])',
    re.I,
)

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


def project_for_md(md: Path) -> str | None:
    try:
        rel = md.relative_to(ROOT)
    except ValueError:
        return None
    if not rel.parts:
        return None
    top = rel.parts[0]
    return top if top in PROJECTS else None


def win_extended(path: Path) -> str:
    s = str(path.resolve())
    return s if s.startswith("\\\\?\\") else "\\\\?\\" + s


def iter_markdown_files() -> list[Path]:
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(win_extended(ROOT)):
        normal_dir = dirpath[4:] if dirpath.startswith("\\\\?\\") else dirpath
        dirnames[:] = [
            d
            for d in dirnames
            if d not in SKIP_TOP and not d.startswith(".")
        ]
        if "\\tools\\" in normal_dir.replace("/", "\\") or "\\.obsidian\\" in normal_dir.replace(
            "/", "\\"
        ):
            continue
        for name in filenames:
            if name.endswith(".md"):
                found.append(Path(normal_dir) / name)
    return found


def read_text(path: Path) -> str:
    with open(win_extended(path), "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def write_text(path: Path, text: str) -> None:
    with open(win_extended(path), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def filename_from_ref(ref: str) -> str | None:
    ref = ref.strip().split(" ")[0]
    if ref.startswith("http"):
        return None
    ref = ref.replace("\\", "/")
    if "/attachments/" in ref:
        return ref.split("/attachments/")[-1].split("/")[-1]
    if ref.startswith("attachments/"):
        parts = ref[len("attachments/") :].split("/")
        return parts[-1] if parts else None
    return None


def project_images_dir(project: str) -> Path:
    return ATTACHMENTS / f"{project}-Images"


def rel_to_project_image(md_path: Path, project: str, filename: str) -> str:
    target = project_images_dir(project) / filename
    rel = os.path.relpath(target, md_path.parent).replace("\\", "/")
    return rel


def collect_references() -> tuple[
    dict[str, set[str]], dict[Path, list[tuple[str, str]]]
]:
    """filename -> projects using it; md -> list of (filename, full_ref_match context)."""
    file_to_projects: dict[str, set[str]] = defaultdict(set)
    md_refs: dict[Path, set[str]] = defaultdict(set)

    for md in iter_markdown_files():
        project = project_for_md(md)
        if not project:
            continue
        text = read_text(md)
        for m in MD_IMG_RE.finditer(text):
            fn = filename_from_ref(m.group(2))
            if fn:
                file_to_projects[fn].add(project)
                md_refs[md].add(fn)
        for m in ATTACHMENT_REF_RE.finditer(text):
            fn = m.group(1).split("/")[-1]
            file_to_projects[fn].add(project)
            md_refs[md].add(fn)
        for m in COVER_LINE_RE.finditer(text):
            fn = filename_from_ref(m.group(2).strip())
            if fn:
                file_to_projects[fn].add(project)
                md_refs[md].add(fn)

    return file_to_projects, md_refs


def locate_source_file(filename: str) -> Path | None:
    direct = ATTACHMENTS / filename
    if direct.is_file():
        return direct
    for sub in ATTACHMENTS.iterdir():
        if sub.is_dir() and sub.name.endswith("-Images"):
            candidate = sub / filename
            if candidate.is_file():
                return candidate
    return None


def move_images(file_to_projects: dict[str, set[str]]) -> dict[tuple[str, str], Path]:
    """Map (project, filename) -> destination path."""
    placed: dict[tuple[str, str], Path] = {}
    for filename, projects in sorted(file_to_projects.items()):
        source = locate_source_file(filename)
        if not source:
            continue
        for project in projects:
            dest_dir = project_images_dir(project)
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / filename
            placed[(project, filename)] = dest
            if dest.resolve() == source.resolve():
                continue
            if dest.exists():
                if dest.read_bytes() == source.read_bytes():
                    continue
            shutil.copy2(source, dest)

    # Remove loose files from attachments root (only image types)
    for item in list(ATTACHMENTS.iterdir()):
        if item.is_file() and item.suffix.lower() in IMAGE_EXT:
            item.unlink()

    return placed


def rewrite_markdown(md_refs: dict[Path, set[str]]) -> int:
    changed = 0
    for md, filenames in md_refs.items():
        project = project_for_md(md)
        if not project:
            continue
        text = read_text(md)
        original = text

        def sub_md(m: re.Match[str]) -> str:
            alt, ref = m.group(1), m.group(2).strip()
            fn = filename_from_ref(ref)
            if not fn or fn not in filenames:
                return m.group(0)
            if not (project_images_dir(project) / fn).is_file():
                return m.group(0)
            new_ref = rel_to_project_image(md, project, fn)
            if ref == new_ref:
                return m.group(0)
            return f"![{alt}]({new_ref})"

        text = MD_IMG_RE.sub(sub_md, text)

        def sub_cover(m: re.Match[str]) -> str:
            prefix, val = m.group(1), m.group(2).strip()
            fn = filename_from_ref(val)
            if not fn or fn not in filenames:
                return m.group(0)
            if not (project_images_dir(project) / fn).is_file():
                return m.group(0)
            new_ref = rel_to_project_image(md, project, fn)
            if val.strip() == new_ref:
                return m.group(0)
            return f"{prefix}{new_ref}"

        text = COVER_LINE_RE.sub(sub_cover, text)

        def sub_href(m: re.Match[str]) -> str:
            p1, _old, fn, p4 = m.group(1), m.group(2), m.group(3), m.group(4)
            if fn not in filenames:
                return m.group(0)
            if not (project_images_dir(project) / fn).is_file():
                return m.group(0)
            new_ref = rel_to_project_image(md, project, fn)
            return f"{p1}{new_ref}{p4}"

        text = HREF_ATTACH_RE.sub(sub_href, text)

        # Plain attachment paths in YAML or tables not caught above
        for fn in filenames:
            dest = project_images_dir(project) / fn
            if not dest.is_file():
                copy_gitbook_asset_to_project(fn, project)
            if not dest.is_file():
                continue
            new_ref = rel_to_project_image(md, project, fn)
            legacy = [
                re.compile(rf"(?<![\w/-])(?:\.\./)*attachments/{re.escape(fn)}(?!\S)"),
            ]
            for pat in legacy:
                text = pat.sub(new_ref, text)

        if text != original:
            write_text(md, text)
            changed += 1
    return changed


def copy_gitbook_asset_to_project(name: str, project: str) -> None:
    dest = project_images_dir(project) / name
    if dest.is_file():
        return
    for assets_dir in ROOT.rglob(".gitbook/assets"):
        if not assets_dir.is_dir():
            continue
        try:
            rel = assets_dir.relative_to(ROOT)
        except ValueError:
            continue
        if not rel.parts or rel.parts[0] != project:
            continue
        candidate = assets_dir / name
        if candidate.is_file():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(candidate, dest)
            return


def validate() -> dict:
    broken = []
    legacy_flat = []
    for md in iter_markdown_files():
        project = project_for_md(md)
        if not project:
            continue
        text = read_text(md)
        for m in MD_IMG_RE.finditer(text):
            ref = m.group(2).strip().split(" ")[0]
            if ref.startswith("http"):
                continue
            if "/attachments/" in ref.replace("\\", "/"):
                parts = ref.replace("\\", "/").split("/attachments/", 1)[-1]
                if "-Images/" not in parts and project in PROJECTS:
                    legacy_flat.append(f"{md.relative_to(ROOT)}: {ref}")
            target = (md.parent / ref).resolve()
            if not target.is_file():
                broken.append(f"{md.relative_to(ROOT)}: {ref}")
    return {
        "broken_count": len(broken),
        "broken_sample": broken[:20],
        "legacy_flat_count": len(legacy_flat),
        "legacy_flat_sample": legacy_flat[:20],
    }


def main() -> None:
    file_to_projects, md_refs = collect_references()
    move_images(file_to_projects)
    n = rewrite_markdown(md_refs)
    report = validate()
    print(f"Markdown files updated: {n}")
    print(f"Project image folders: {[p.name for p in ATTACHMENTS.iterdir() if p.is_dir()]}")
    for proj in PROJECTS:
        d = project_images_dir(proj)
        if d.is_dir():
            print(f"  {d.name}: {len(list(d.iterdir()))} files")
    print("Validation:", report)


if __name__ == "__main__":
    main()
