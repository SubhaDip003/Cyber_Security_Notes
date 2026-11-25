"""Fix relative attachment paths and remaining GitBook / external image references."""
from __future__ import annotations

import os
import re
import shutil
import urllib.request
from pathlib import Path

from gitbook_migrate_images import (
    ATTACHMENTS,
    AssetMigrator,
    ROOT,
    iter_markdown_files,
    rel_to_attachments,
    sanitize_filename,
)

MD_IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
IMG_TAG_RE = re.compile(
    r"<figure>\s*<img\s+src=[\"']([^\"']+)[\"']\s*alt=[\"']([^\"']*)[\"']\s*>\s*<figcaption>.*?</figcaption>\s*</figure>",
    re.I | re.S,
)
COVER_BLOCK_RE = re.compile(
    r"(cover:\s*>-\s*\n(?:  .+\n)+?)(?=^[A-Za-z])",
    re.M,
)
GITBOOK_ASSET_LINE_RE = re.compile(r"\.gitbook/assets/[^\n]+")


def fix_attachment_path_refs(text: str, md_path: Path) -> tuple[str, bool]:
    changed = False

    def sub_md(m: re.Match[str]) -> str:
        nonlocal changed
        alt, ref = m.group(1), m.group(2).strip().split(" ")[0]
        if ref.startswith("http"):
            return m.group(0)
        name = Path(ref.replace("\\", "/")).name
        candidate = ATTACHMENTS / name
        if not candidate.is_file():
            if ref.startswith("attachments/") or ref.startswith("../attachments/"):
                name = ref.split("/")[-1]
                candidate = ATTACHMENTS / name
            if not candidate.is_file():
                return m.group(0)
        correct = rel_to_attachments(md_path, candidate.name)
        if ref != correct:
            changed = True
            return f"![{alt}]({correct})"
        return m.group(0)

    text = MD_IMG_RE.sub(sub_md, text)
    return text, changed


def fix_cover_blocks(text: str, md_path: Path, migrator: AssetMigrator) -> tuple[str, bool]:
    changed = False

    def sub_block(m: re.Match[str]) -> str:
        nonlocal changed
        block = m.group(1)
        if ".gitbook/assets" not in block:
            return block
        joined = " ".join(line.strip() for line in block.splitlines()[1:])
        joined = joined.replace(".gitbook/assets/", "").strip()
        # re-add prefix for resolver
        ref = f"../../.gitbook/assets/{joined}"
        name, rel = migrator.attachment_for_ref(md_path, ref)
        if not rel:
            return block
        changed = True
        return f"cover: {rel}\n"

    return COVER_BLOCK_RE.sub(sub_block, text), changed


def fix_inline_gitbook_covers(text: str, md_path: Path, migrator: AssetMigrator) -> tuple[str, bool]:
    changed = False
    if ".gitbook/assets" not in text:
        return text, False

    def sub_line(match: re.Match[str]) -> str:
        nonlocal changed
        fragment = match.group(0)
        path_part = fragment.split(".gitbook/assets/", 1)[-1].strip()
        ref = f".gitbook/assets/{path_part}"
        _name, rel = migrator.attachment_for_ref(md_path, ref)
        if not rel:
            return fragment
        changed = True
        if fragment.startswith("cover:"):
            return f"cover: {rel}"
        return rel

    new_text = GITBOOK_ASSET_LINE_RE.sub(sub_line, text)
    return new_text, changed


def download_external(url: str, migrator: AssetMigrator) -> str | None:
    name = sanitize_filename(Path(url).name or "external-image.png")
    dest = ATTACHMENTS / name
    if not dest.exists():
        try:
            urllib.request.urlretrieve(url, dest)
            migrator.stats.images_copied += 1
        except Exception:
            return None
    return name


def fix_external_images(text: str, md_path: Path, migrator: AssetMigrator) -> tuple[str, bool]:
    changed = False

    def replace_url(url: str, alt: str = "") -> str | None:
        name = download_external(url, migrator)
        if not name:
            return None
        return f"![{alt or os.path.splitext(name)[0]}]({rel_to_attachments(md_path, name)})"

    def sub_figure(m: re.Match[str]) -> str:
        nonlocal changed
        url, alt = m.group(1), m.group(2)
        if not url.startswith("http"):
            return m.group(0)
        rep = replace_url(url, alt)
        if not rep:
            return m.group(0)
        changed = True
        return f"\n{rep}\n"

    text = IMG_TAG_RE.sub(sub_figure, text)

    def sub_md(m: re.Match[str]) -> str:
        nonlocal changed
        alt, ref = m.group(1), m.group(2).strip()
        if not ref.startswith("http"):
            return m.group(0)
        rep = replace_url(ref, alt)
        if not rep:
            return m.group(0)
        changed = True
        return rep

    text = MD_IMG_RE.sub(sub_md, text)
    return text, changed


def main() -> None:
    migrator = AssetMigrator()
    modified = 0
    for md in iter_markdown_files():
        text = md.read_text(encoding="utf-8", errors="replace")
        original = text
        text, _ = fix_attachment_path_refs(text, md)
        text, _ = fix_cover_blocks(text, md, migrator)
        text, _ = fix_inline_gitbook_covers(text, md, migrator)
        text, _ = fix_external_images(text, md, migrator)
        text, _ = fix_attachment_path_refs(text, md)
        if text != original:
            md.write_text(text, encoding="utf-8", newline="\n")
            modified += 1
    print(f"Fixed {modified} markdown files")


if __name__ == "__main__":
    main()
