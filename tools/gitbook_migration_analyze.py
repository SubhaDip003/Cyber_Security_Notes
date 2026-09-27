"""Analyze GitBook image references in the vault."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ASSET_RE = re.compile(r"\.gitbook/assets/([^\"'>\s)]+)", re.I)
IMG_SRC_RE = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.I)
MD_IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
COVER_RE = re.compile(r"^cover:\s*(.+)$", re.I | re.M)
HREF_ASSET_RE = re.compile(r'href=["\']?\.gitbook/assets/([^"\']+)["\']?', re.I)


def main() -> None:
    md_files = [
        p
        for p in ROOT.rglob("*.md")
        if ".obsidian" not in p.parts and "tools" not in p.parts
    ]
    gitbook_refs: set[str] = set()
    external_gitbook: set[str] = set()
    files_with_refs: set[Path] = set()

    for p in md_files:
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        found = False
        for m in ASSET_RE.finditer(text):
            gitbook_refs.add(m.group(1))
            found = True
        for m in HREF_ASSET_RE.finditer(text):
            gitbook_refs.add(m.group(1))
            found = True
        for m in IMG_SRC_RE.finditer(text):
            u = m.group(1).strip()
            if ".gitbook/assets/" in u:
                gitbook_refs.add(u.split(".gitbook/assets/")[-1].lstrip("/"))
                found = True
            elif "gitbook" in u.lower():
                external_gitbook.add(u)
                found = True
        for m in MD_IMG_RE.finditer(text):
            u = m.group(1).strip()
            if "gitbook" in u.lower():
                external_gitbook.add(u)
                found = True
            elif ".gitbook/assets/" in u:
                gitbook_refs.add(u.split(".gitbook/assets/")[-1].lstrip("/"))
                found = True
        for m in COVER_RE.finditer(text):
            c = m.group(1).strip()
            if ".gitbook/assets/" in c:
                gitbook_refs.add(c.split(".gitbook/assets/")[-1].strip())
                found = True
        if found:
            files_with_refs.add(p)

    attachments = ROOT / "attachments"
    existing = set(attachments.iterdir()) if attachments.is_dir() else set()
    local_assets_dirs = list(ROOT.rglob(".gitbook/assets"))

    print(f"ROOT: {ROOT}")
    print(f"Markdown files: {len(md_files)}")
    print(f"Markdown files with gitbook image refs: {len(files_with_refs)}")
    print(f"Unique .gitbook/assets filenames referenced: {len(gitbook_refs)}")
    print(f"External gitbook URLs: {len(external_gitbook)}")
    print(f"Local .gitbook/assets directories: {len(local_assets_dirs)}")
    for d in local_assets_dirs[:5]:
        n = len(list(d.glob("*"))) if d.is_dir() else 0
        print(f"  {d} ({n} files)")
    print(f"Existing attachments/: {len(existing)}")


if __name__ == "__main__":
    main()
