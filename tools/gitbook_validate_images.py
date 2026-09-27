"""Validate Markdown image paths and GitBook migration completeness."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATTACHMENTS = ROOT / "attachments"

MD_IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
WIKI_IMG_RE = re.compile(r"!\[\[[^\]]+\]\]")
GITBOOK_RE = re.compile(r"gitbook|\.gitbook/assets", re.I)
IMG_SRC_RE = re.compile(r"<img[^>]+src=[\"']([^\"']+)[\"']", re.I)


def iter_md() -> list[Path]:
    out: list[Path] = []
    for p in ROOT.rglob("*.md"):
        if not p.is_file():
            continue
        if ".obsidian" in p.parts or "tools" in p.parts:
            continue
        out.append(p)
    return out


def resolve_image(md: Path, ref: str) -> Path | None:
    ref = ref.strip().split(" ")[0]
    if ref.startswith("http://") or ref.startswith("https://"):
        return None
    target = (md.parent / ref).resolve()
    return target if target.is_file() else None


def main() -> None:
    broken: list[str] = []
    gitbook_refs: list[str] = []
    wiki_imgs: list[str] = []
    html_imgs: list[str] = []
    outside_attachments: list[str] = []
    bad_names: list[str] = []
    md_refs = 0

    attachment_files = {f.name for f in ATTACHMENTS.iterdir() if f.is_file()} if ATTACHMENTS.is_dir() else set()

    for md in iter_md():
        text = md.read_text(encoding="utf-8", errors="replace")
        rel = md.relative_to(ROOT)

        for m in WIKI_IMG_RE.finditer(text):
            wiki_imgs.append(f"{rel}: {m.group(0)}")

        for m in GITBOOK_RE.finditer(text):
            # allow false positives in prose? flag line context
            line_no = text[: m.start()].count("\n") + 1
            gitbook_refs.append(f"{rel}:{line_no}: {text.splitlines()[line_no - 1][:120]}")

        for m in MD_IMG_RE.finditer(text):
            ref = m.group(2).strip()
            if ref.startswith("http"):
                if "gitbook" in ref.lower():
                    gitbook_refs.append(f"{rel}: {ref}")
                continue
            md_refs += 1
            resolved = resolve_image(md, ref)
            if not resolved:
                broken.append(f"{rel}: {ref}")
                continue
            if ATTACHMENTS.resolve() not in resolved.parents and resolved.parent != ATTACHMENTS.resolve():
                outside_attachments.append(f"{rel}: {ref} -> {resolved}")

        for m in IMG_SRC_RE.finditer(text):
            html_imgs.append(f"{rel}: {m.group(1)}")

    # duplicate attachment content by hash
    dupes: list[str] = []
    if ATTACHMENTS.is_dir():
        import hashlib

        hashes: dict[str, str] = {}
        for f in ATTACHMENTS.iterdir():
            if not f.is_file():
                continue
            if re.search(r"[()\s]", f.name):
                bad_names.append(f.name)
            h = hashlib.sha256(f.read_bytes()).hexdigest()
            if h in hashes:
                dupes.append(f"{hashes[h]} <=> {f.name}")
            else:
                hashes[h] = f.name

    report = {
        "markdown_files_scanned": len(iter_md()),
        "markdown_image_references": md_refs,
        "broken_image_references": broken,
        "broken_count": len(broken),
        "remaining_gitbook_references": gitbook_refs[:100],
        "remaining_gitbook_count": len(gitbook_refs),
        "wikilink_images": wiki_imgs,
        "html_img_tags": html_imgs[:50],
        "html_img_count": len(html_imgs),
        "images_not_under_attachments": outside_attachments[:50],
        "duplicate_attachment_files": dupes[:50],
        "duplicate_count": len(dupes),
        "problematic_attachment_filenames": bad_names,
        "attachments_total": len(list(ATTACHMENTS.glob("*"))) if ATTACHMENTS.is_dir() else 0,
    }

    print("VALIDATION REPORT")
    print("=================")
    for k, v in report.items():
        if k.endswith("_count") or k in ("markdown_files_scanned", "markdown_image_references", "attachments_total"):
            print(f"{k}: {v}")
    print(f"broken_image_references (first 20): {broken[:20]}")
    print(f"remaining_gitbook (first 10): {gitbook_refs[:10]}")
    print(f"wikilink_images: {wiki_imgs}")
    print(f"html_img_remaining: {len(html_imgs)}")
    print(f"duplicate_attachment_files: {len(dupes)}")
    print(f"problematic_filenames: {bad_names[:20]}")
    print("---JSON---")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
