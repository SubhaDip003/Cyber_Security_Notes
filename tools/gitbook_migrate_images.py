"""
Migrate GitBook .gitbook/assets references to vault-root attachments/ with relative Markdown paths.
Copies from local .gitbook/assets (no network required).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
ATTACHMENTS = ROOT / "attachments"
SKIP_PARTS = {".obsidian", "tools", ".git"}

FIGURE_IMG_RE = re.compile(
    r"<figure>\s*<img\s+src=[\"']([^\"']+)[\"']\s*alt=[\"']([^\"']*)[\"']\s*>\s*<figcaption>.*?</figcaption>\s*</figure>",
    re.I | re.S,
)
IMG_TAG_RE = re.compile(
    r"<img\s+[^>]*src=[\"']([^\"']+)[\"'][^>]*>",
    re.I,
)
MD_IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
COVER_RE = re.compile(r"^(cover:\s*)(.+)$", re.M)
HREF_GITBOOK_RE = re.compile(
    r"(href=[\"'])([^\"']*\.gitbook/assets/([^\"']+))([\"'])",
    re.I,
)
GITBOOK_IN_PATH_RE = re.compile(r"\.gitbook/assets/(.+)$", re.I)

ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sanitize_filename(name: str) -> str:
    name = unquote(name.replace("\\", "/").split("/")[-1].strip())
    stem, ext = os.path.splitext(name)
    ext = ext.lower() if ext else ".png"
    if ext not in ALLOWED_EXT:
        ext = ".png"
    stem = re.sub(r"\s*\(\s*(\d+)\s*\)\s*", r"-\1", stem)
    stem = stem.replace(" ", "-")
    stem = re.sub(r"[^A-Za-z0-9._-]+", "", stem)
    stem = re.sub(r"-+", "-", stem).strip("-._")
    if not stem:
        stem = "image"
    return f"{stem}{ext}"


def rel_to_attachments(md_path: Path, attachment_name: str) -> str:
    rel_dir = os.path.relpath(ATTACHMENTS, md_path.parent).replace("\\", "/")
    if rel_dir == ".":
        return attachment_name
    return f"{rel_dir}/{attachment_name}"


def iter_markdown_files() -> list[Path]:
    out: list[Path] = []
    for p in ROOT.rglob("*.md"):
        if not p.is_file():
            continue
        if any(part in SKIP_PARTS for part in p.parts):
            continue
        out.append(p)
    return out


def index_gitbook_assets() -> dict[str, list[Path]]:
    by_name: dict[str, list[Path]] = {}
    for assets_dir in ROOT.rglob(".gitbook/assets"):
        if not assets_dir.is_dir():
            continue
        for f in assets_dir.iterdir():
            if f.is_file():
                by_name.setdefault(f.name, []).append(f)
    return by_name


@dataclass
class Stats:
    md_processed: int = 0
    md_modified: int = 0
    refs_found: int = 0
    images_copied: int = 0
    images_reused_existing: int = 0
    images_reused_map: int = 0
    missing_sources: list[str] = field(default_factory=list)
    duplicate_basenames_skipped: int = 0


class AssetMigrator:
    def __init__(self) -> None:
        self.stats = Stats()
        ATTACHMENTS.mkdir(parents=True, exist_ok=True)
        self.by_name = index_gitbook_assets()
        self.hash_to_filename: dict[str, str] = {}
        self.source_to_filename: dict[str, str] = {}
        self.existing_hashes: dict[str, str] = {}
        for f in ATTACHMENTS.iterdir():
            if f.is_file():
                self.existing_hashes[file_hash(f)] = f.name
                self.hash_to_filename[file_hash(f)] = f.name

    def resolve_source(self, md_path: Path, ref: str) -> Path | None:
        ref = unquote(ref.strip())
        if ref.startswith("http://") or ref.startswith("https://"):
            return None
        candidate = (md_path.parent / ref).resolve()
        if candidate.is_file():
            return candidate
        m = GITBOOK_IN_PATH_RE.search(ref.replace("\\", "/"))
        if m:
            basename = m.group(1).split("/")[-1]
            # Prefer asset dir under same top-level section
            options = self.by_name.get(basename, [])
            if options:
                return options[0]
        basename = Path(ref).name
        options = self.by_name.get(basename, [])
        return options[0] if options else None

    def ensure_attachment(self, source: Path) -> str | None:
        key = str(source.resolve())
        if key in self.source_to_filename:
            return self.source_to_filename[key]

        digest = file_hash(source)
        if digest in self.hash_to_filename:
            name = self.hash_to_filename[digest]
            self.source_to_filename[key] = name
            return name

        base_name = sanitize_filename(source.name)
        dest = ATTACHMENTS / base_name
        if dest.exists():
            if file_hash(dest) == digest:
                name = dest.name
            else:
                stem, ext = os.path.splitext(base_name)
                name = f"{stem}-{digest[:8]}{ext}"
                dest = ATTACHMENTS / name
        else:
            name = base_name

        if not dest.exists():
            shutil.copy2(source, dest)
            self.stats.images_copied += 1
        else:
            self.stats.images_reused_existing += 1

        self.hash_to_filename[digest] = name
        self.source_to_filename[key] = name
        return name

    def attachment_for_ref(self, md_path: Path, ref: str) -> tuple[str | None, str | None]:
        """Returns (attachment_filename, markdown_relative_path) or (None, None)."""
        self.stats.refs_found += 1
        source = self.resolve_source(md_path, ref)
        if not source:
            self.stats.missing_sources.append(f"{md_path.relative_to(ROOT)} :: {ref}")
            return None, None
        if key := str(source.resolve()):
            if key in self.source_to_filename:
                self.stats.images_reused_map += 1
        name = self.ensure_attachment(source)
        if not name:
            return None, None
        rel = rel_to_attachments(md_path, name)
        return name, rel

    def alt_text(self, alt: str, attachment_name: str) -> str:
        if alt.strip():
            return alt.strip()
        stem = os.path.splitext(attachment_name)[0].replace("-", " ")
        return stem

    def process_content(self, md_path: Path, text: str) -> tuple[str, bool]:
        changed = False

        def sub_figure(m: re.Match[str]) -> str:
            nonlocal changed
            ref, alt = m.group(1), m.group(2)
            if ".gitbook/assets" not in ref and not ref.startswith("http"):
                return m.group(0)
            name, rel = self.attachment_for_ref(md_path, ref)
            if not rel:
                return m.group(0)
            changed = True
            label = self.alt_text(alt, name or "image")
            return f"\n![{label}]({rel})\n"

        text = FIGURE_IMG_RE.sub(sub_figure, text)

        def sub_loose_img(m: re.Match[str]) -> str:
            nonlocal changed
            ref = m.group(1)
            if ".gitbook/assets" not in ref:
                return m.group(0)
            name, rel = self.attachment_for_ref(md_path, ref)
            if not rel:
                return m.group(0)
            changed = True
            label = self.alt_text("", name or "image")
            return f"![{label}]({rel})"

        text = IMG_TAG_RE.sub(sub_loose_img, text)

        def sub_md_img(m: re.Match[str]) -> str:
            nonlocal changed
            alt, ref = m.group(1), m.group(2).strip()
            if ".gitbook/assets" not in ref and "gitbook" not in ref.lower():
                if ref.startswith("attachments/") or "/attachments/" in ref:
                    # Fix depth to vault attachments/
                    target = ref.split("/")[-1]
                    correct = rel_to_attachments(md_path, target)
                    if ref != correct and (ATTACHMENTS / target).is_file():
                        changed = True
                        return f"![{alt}]({correct})"
                return m.group(0)
            name, rel = self.attachment_for_ref(md_path, ref)
            if not rel:
                return m.group(0)
            changed = True
            label = self.alt_text(alt, name or "image")
            return f"![{label}]({rel})"

        text = MD_IMG_RE.sub(sub_md_img, text)

        def sub_cover(m: re.Match[str]) -> str:
            nonlocal changed
            prefix, val = m.group(1), m.group(2).strip()
            if ".gitbook/assets" not in val:
                return m.group(0)
            name, rel = self.attachment_for_ref(md_path, val)
            if not rel:
                return m.group(0)
            changed = True
            return f"{prefix}{rel}"

        text = COVER_RE.sub(sub_cover, text)

        def sub_href(m: re.Match[str]) -> str:
            nonlocal changed
            p1, _full, basename, p4 = m.group(1), m.group(2), m.group(3), m.group(4)
            ref = f".gitbook/assets/{basename}"
            name, rel = self.attachment_for_ref(md_path, ref)
            if not rel:
                return m.group(0)
            changed = True
            return f"{p1}{rel}{p4}"

        text = HREF_GITBOOK_RE.sub(sub_href, text)

        # Remaining plain .gitbook/assets path strings in markdown links (not caught above)
        def sub_plain_gitbook_path(m: re.Match[str]) -> str:
            nonlocal changed
            ref = m.group(0)
            name, rel = self.attachment_for_ref(md_path, ref)
            if not rel:
                return ref
            changed = True
            return rel

        if ".gitbook/assets/" in text:
            text2 = re.sub(
                r"(?<![(\[])(\.{1,2}/)+(?:[^/\s]+/)*\.gitbook/assets/[^\s)\]\"']+",
                sub_plain_gitbook_path,
                text,
            )
            if text2 != text:
                text = text2
                changed = True

        return text, changed


def validate(stats_path: Path) -> dict:
    import subprocess

    result = subprocess.run(
        [os.environ.get("PYTHON", "python"), str(ROOT / "tools" / "gitbook_validate_images.py")],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    report = result.stdout
    if result.stderr:
        report += "\n" + result.stderr
    stats_path.write_text(report, encoding="utf-8")
    try:
        return json.loads(result.stdout.split("---JSON---")[-1].strip())
    except Exception:
        return {"raw": report, "exit_code": result.returncode}


def main() -> None:
    migrator = AssetMigrator()

    for md in iter_markdown_files():
        migrator.stats.md_processed += 1
        original = md.read_text(encoding="utf-8", errors="replace")
        updated, changed = migrator.process_content(md, original)
        if changed:
            md.write_text(updated, encoding="utf-8", newline="\n")
            migrator.stats.md_modified += 1

    report_path = ROOT / "tools" / "migration_report.json"
    validation = validate(ROOT / "tools" / "validation_report.txt")

    summary = {
        "markdown_files_processed": migrator.stats.md_processed,
        "markdown_files_modified": migrator.stats.md_modified,
        "image_references_found": migrator.stats.refs_found,
        "images_copied_to_attachments": migrator.stats.images_copied,
        "existing_attachment_files_reused": migrator.stats.images_reused_existing,
        "duplicate_copy_avoided_via_map": migrator.stats.images_reused_map,
        "missing_source_files": migrator.stats.missing_sources[:50],
        "missing_source_count": len(migrator.stats.missing_sources),
        "attachments_file_count": len(list(ATTACHMENTS.glob("*"))),
        "validation": validation,
    }
    report_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
