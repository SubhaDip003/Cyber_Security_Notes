"""Generate INDEX.md navigation files per topic (wikilinks only; no note body edits)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

TOPICS = [
    "AD-PenTest",
    "AI-LLM-Security",
    "Cloud Security",
    "HTB",
    "Practical-Ethical-Hacking",
    "tools",
    "VAPT",
    "WAPT",
]

SKIP_DIRS = {
    ".gitbook",
    "__pycache__",
    "_vault-scripts",
    ".obsidian",
    "attachments",
    "vault-sessions",
}
SKIP_FILES = {"INDEX.md"}

VAULT_LINK = "- [[../README|Cyber_Security_Notes]]"

TOPIC_TITLES = {
    "AD-PenTest": "AD-PenTest",
    "AI-LLM-Security": "AI-LLM-Security",
    "Cloud Security": "Cloud Security",
    "HTB": "HTB",
    "Practical-Ethical-Hacking": "Practical-Ethical-Hacking",
    "tools": "tools",
    "VAPT": "VAPT",
    "WAPT": "WAPT",
}

TOPIC_ENTRY = {
    "AD-PenTest": [
        "- [[README|Landing (README)]]",
        "- [[AD PenTesting|GitBook-style table of contents]]",
    ],
    "AI-LLM-Security": [
        "- [[AI LLM Security|Map of content]]",
        "- [[CWL/README|CWL — index]]",
    ],
    "Cloud Security": [
        "- [[CWL/Cloud Security Fundamentals/1. Intro/1.1 Introduction to Cloud Computing & Cloud Security Fundamentals|1.1 Cloud Security Fundamentals]]",
    ],
    "HTB": [
        "- [[README|HTB landing]]",
        "- [[WEB PENETRATION TESTER/WEB PENETRATION TESTER|Web Penetration Tester — TOC]]",
    ],
    "Practical-Ethical-Hacking": [
        "- [[README|Landing (README)]]",
        "- [[SUMMARY|GitBook-style SUMMARY]]",
    ],
    "VAPT": [
        "- [[README|Landing (README)]]",
        "- [[SUMMARY|GitBook-style SUMMARY]]",
    ],
    "tools": ["- [[README|About this folder]]"],
    "WAPT": [],
}


def vault_rel_link(md: Path, topic_root: Path) -> str:
    rel = md.relative_to(topic_root).with_suffix("")
    parts = rel.parts
    if len(parts) == 1:
        name = parts[0]
        return f"- [[{name}]]"
    path = "/".join(parts)
    display = parts[-1]
    return f"- [[{path}|{display}]]"


def section_heading(path: Path, topic_root: Path) -> str:
    rel = path.relative_to(topic_root)
    if rel.parent == Path("."):
        return "## Top level"
    return "## " + " / ".join(rel.parent.parts)


def build_index(topic: str) -> str:
    topic_root = ROOT / topic
    title = TOPIC_TITLES[topic]
    lines = [
        f"# {title} — Index",
        "",
        "Navigation only — note bodies are not modified.",
        "",
        "## Vault",
        VAULT_LINK,
        "",
        "## Entry points",
    ]
    entry = TOPIC_ENTRY.get(topic, [])
    if entry:
        lines.extend(entry)
    else:
        lines.append("- _(none yet)_")

    if topic == "WAPT":
        lines.extend(
            [
                "",
                "## Status",
                "",
                "Placeholder for future **Web Application Penetration Testing** notes.",
                "Related material today lives under [[../HTB/WEB PENETRATION TESTER/WEB PENETRATION TESTER|HTB — Web Penetration Tester]].",
            ]
        )
        lines.extend(
            [
                "",
                "## Vault maintenance",
                "",
                "- [[../vault-sessions/README|vault-sessions — structural scripts]]",
                "",
                "## Other topics",
                "",
            ]
        )
        for other in TOPICS:
            if other != topic:
                lines.append(f"- [[../{other}/INDEX|{other}]]")
        lines.append("")
        return "\n".join(lines)

    if topic == "tools":
        lines.extend(
            [
                "",
                "## Security tool notes",
                "",
                "_Add per-tool or cheat-sheet notes here as you create them._",
                "",
                "Vault automation: [[../vault-sessions/README|vault-sessions]]",
            ]
        )
        lines.extend(
            [
                "",
                "## Vault maintenance",
                "",
                "- [[../vault-sessions/README|vault-sessions — structural scripts]]",
                "",
                "## Other topics",
                "",
            ]
        )
        for other in TOPICS:
            if other != topic:
                lines.append(f"- [[../{other}/INDEX|{other}]]")
        lines.append("")
        return "\n".join(lines)

    import os

    md_files: list[Path] = []

    def walk_md(base: Path) -> None:
        try:
            with os.scandir(base) as it:
                for entry in it:
                    if entry.is_dir(follow_symlinks=False):
                        if entry.name in SKIP_DIRS:
                            continue
                        walk_md(Path(entry.path))
                    elif entry.name.endswith(".md") and entry.name not in SKIP_FILES:
                        if entry.name == "README.md":
                            continue
                        md_files.append(Path(entry.path))
        except OSError:
            pass

    if topic == "AD-PenTest":
        walk_md(topic_root)
        md_files = sorted(set(md_files))
    else:
        for p in sorted(topic_root.rglob("*.md")):
            if p.name in SKIP_FILES or p.name == "README.md":
                continue
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            md_files.append(p)

    by_section: dict[str, list[str]] = {}
    for md in md_files:
        head = section_heading(md, topic_root)
        by_section.setdefault(head, []).append(vault_rel_link(md, topic_root))

    if by_section:
        lines.append("")
        lines.append("## All notes")
        for head in sorted(by_section.keys()):
            lines.append("")
            lines.append(head)
            lines.extend(by_section[head])

    if topic == "AD-PenTest":
        lines.extend(
            [
                "",
                "## Windows path note",
                "",
                "Some very deep AD folders may be omitted from this auto-generated list. "
                "Use [[AD PenTesting]] for the complete GitBook-style table of contents.",
            ]
        )

    lines.extend(
        [
            "",
            "## Vault maintenance",
            "",
            "- [[../vault-sessions/README|vault-sessions — structural scripts]]",
            "",
            "## Other topics",
            "",
        ]
    )
    for other in TOPICS:
        if other != topic:
            lines.append(f"- [[../{other}/INDEX|{other}]]")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    for topic in TOPICS:
        topic_root = ROOT / topic
        if not topic_root.is_dir() and topic != "WAPT":
            continue
        topic_root.mkdir(parents=True, exist_ok=True)
        out = topic_root / "INDEX.md"
        out.write_text(build_index(topic), encoding="utf-8")
        print(f"Wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()