"""Process markdown files that exceed Windows MAX_PATH using extended-length paths."""
from __future__ import annotations

import os
import sys
from pathlib import Path, PureWindowsPath

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from gitbook_fix_paths import (  # noqa: E402
    fix_attachment_path_refs,
    fix_cover_blocks,
    fix_external_images,
    fix_inline_gitbook_covers,
)
from gitbook_migrate_images import AssetMigrator


def win_extended(path: Path) -> str:
    s = str(path.resolve())
    if s.startswith("\\\\?\\"):
        return s
    return "\\\\?\\" + s


def iter_all_md(root: Path) -> list[Path]:
    found: list[Path] = []
    for dirpath, _dirnames, filenames in os.walk(win_extended(root)):
        normal_dir = dirpath[4:] if dirpath.startswith("\\\\?\\") else dirpath
        for name in filenames:
            if not name.endswith(".md"):
                continue
            if ".obsidian" in normal_dir or "\\tools\\" in normal_dir.replace("/", "\\"):
                continue
            found.append(Path(normal_dir) / name)
    return found


def read_text(path: Path) -> str:
    with open(win_extended(path), "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def write_text(path: Path, text: str) -> None:
    with open(win_extended(path), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def main() -> None:
    migrator = AssetMigrator()
    modified = 0
    for md in iter_all_md(ROOT):
        text = read_text(md)
        original = text
        updated, changed = migrator.process_content(md, text)
        if changed:
            text = updated
        text, c1 = fix_cover_blocks(text, md, migrator)
        text, c2 = fix_inline_gitbook_covers(text, md, migrator)
        text, c3 = fix_external_images(text, md, migrator)
        text, c4 = fix_attachment_path_refs(text, md)
        if text != original:
            write_text(md, text)
            modified += 1
            print(f"updated: {md.relative_to(ROOT)}")
    print(f"long-path files modified: {modified}")


if __name__ == "__main__":
    main()
