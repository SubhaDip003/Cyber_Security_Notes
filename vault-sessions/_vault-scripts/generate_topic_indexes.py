"""Generate INDEX.md navigation files (Markdown links for GitHub + Obsidian)."""
from __future__ import annotations

import os
import re
from pathlib import Path
from urllib.parse import quote

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

# Folder segments omitted or shortened in INDEX headings (paths unchanged on disk).
SEGMENT_SKIP = frozenset(
    {
        "active-directory-penetration-testing-and-redteaming",
        "practical-ethical-hacking",
    }
)

SEGMENT_LABEL = {
    "active-directory-penetration-testing-complete-guide": "Complete guide",
    "active-directory-penetration-testing-lab-setup": "Lab setup",
    "windows-authentication-methods": "Authentication methods",
    "WEB PENETRATION TESTER": "Web Penetration Tester",
    "CWL": "CWL",
    "AI Security Fundamentals": "AI Security Fundamentals",
    "Cloud Security Fundamentals": "Cloud Security Fundamentals",
    "1. Modern AI Fundamentals": "1 — Modern AI",
    "2. AI Security Fundamentals": "2 — AI security",
    "1. Intro": "1 — Intro",
}

MODULE_SHORT = {
    "reconnaissance-techniques-in-active-directory-and-gaining-access": "Reconnaissance & access",
    "credential-harvesting-in-active-directory": "Credential harvesting",
    "privilege-escalation-in-active-directory": "Privilege escalation",
    "local-privilege-escalation-techniques": "Local privilege escalation",
    "linux-abuse": "Linux — DACL abuse",
    "windows-abuse": "Windows — DACL abuse",
    "llmnr-nbt-ns-poisoning": "LLMNR / NBT-NS poisoning",
    "kerberos-pre-authentication-not-required-asreproasting": "AS-REP roasting",
    "1.5-kerberoasting": "Kerberoasting",
    "1.6-bloodhound": "BloodHound",
    "1.-web-request": "1 — HTTP & web requests",
    "2.-introduction-to-web-applications": "2 — Web applications",
    "3.-using-web-proxies": "3 — Web proxies",
    "4.-information-gathering-web-edition": "4 — Information gathering",
    "5.-web-fuzzing": "5 — Web fuzzing",
    "6.-javascript-deobfuscation": "6 — JavaScript deobfuscation",
    "8.-sql-injection-fundamentals": "8 — SQL injection",
}

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

TOPIC_ENTRY: dict[str, list[tuple[str, str]]] = {
    "AD-PenTest": [
        ("README.md", "Landing (README)"),
        ("AD PenTesting.md", "Full table of contents (GitBook style)"),
    ],
    "AI-LLM-Security": [
        ("AI LLM Security.md", "Map of content"),
        ("CWL/README.md", "CWL index"),
    ],
    "Cloud Security": [
        (
            "CWL/Cloud Security Fundamentals/1. Intro/1.1 Introduction to Cloud Computing & Cloud Security Fundamentals.md",
            "1.1 Cloud security fundamentals",
        ),
    ],
    "HTB": [
        ("README.md", "HTB landing"),
        ("WEB PENETRATION TESTER/WEB PENETRATION TESTER.md", "Web Penetration Tester — TOC"),
    ],
    "Practical-Ethical-Hacking": [
        ("README.md", "Landing (README)"),
        ("SUMMARY.md", "GitBook SUMMARY"),
    ],
    "VAPT": [
        ("README.md", "Landing (README)"),
        ("SUMMARY.md", "GitBook SUMMARY"),
    ],
    "tools": [("README.md", "About this folder")],
    "WAPT": [],
}


def md_link(index_file: Path, target: Path, label: str) -> str:
    rel = os.path.relpath(target, index_file.parent).replace("\\", "/")
    href = quote(rel, safe="/:")
    return f"- [{label}]({href})"


def humanize_words(text: str) -> str:
    text = text.replace("_", "-")
    text = re.sub(r"[.\-]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return text
    small = {"and", "or", "with", "in", "on", "to", "of", "for", "vs", "using", "over"}
    words = text.split()
    out: list[str] = []
    for i, w in enumerate(words):
        lw = w.lower()
        if lw in {
            "uac", "llmnr", "nbt", "ns", "ntlm", "dacl", "dc", "api", "http", "https", "sql", "xss", "csrf",
            "vmware", "netexec", "powershell", "powersploit",
        }:
            if lw == "vmware":
                out.append("VMware")
                continue
            if lw == "netexec":
                out.append("NetExec")
                continue
            if lw in {"powershell", "powersploit"}:
                out.append(lw.capitalize())
                continue
            out.append(lw.upper() if len(lw) <= 4 else lw.capitalize())
        elif i > 0 and lw in small:
            out.append(lw)
        else:
            out.append(lw.capitalize())
    return " ".join(out)


def humanize_stem(stem: str) -> str:
    if stem in MODULE_SHORT:
        return MODULE_SHORT[stem]
    if " " in stem and "-" not in stem:
        return stem
    m = re.match(r"^(\d+(?:\.\d+)*)\s*[-.]?\s*(.+)$", stem)
    if m:
        num, rest = m.group(1), m.group(2).strip()
        short = MODULE_SHORT.get(rest, humanize_words(rest))
        return f"{num} {short}"
    return humanize_words(stem)


def stem_sort_key(stem: str) -> tuple:
    parts: list = []
    for chunk in re.split(r"(\d+)", stem):
        if not chunk:
            continue
        parts.append(int(chunk) if chunk.isdigit() else chunk.lower())
    return tuple(parts)


def folder_label(segment: str) -> str | None:
    if segment in SEGMENT_SKIP:
        return None
    if segment in SEGMENT_LABEL:
        return SEGMENT_LABEL[segment]
    if segment in MODULE_SHORT:
        return MODULE_SHORT[segment]
    m = re.match(r"^(\d+)\.-(.+)$", segment)
    if m:
        num, rest = m.group(1), m.group(2)
        short = MODULE_SHORT.get(rest, humanize_words(rest))
        return f"{num}. {short}"
    m = re.match(r"^(\d+(?:\.\d+)*)\s*[-.]?\s*(.+)$", segment)
    if m:
        return humanize_stem(segment)
    return humanize_words(segment)


def section_heading(path: Path, topic_root: Path) -> tuple[str, tuple[int, ...]]:
    rel = path.relative_to(topic_root)
    if rel.parent == Path("."):
        return ("## Top level", (0,))

    labels: list[str] = []
    for part in rel.parent.parts:
        label = folder_label(part)
        if label:
            labels.append(label)

    if not labels:
        return ("## Top level", (0,))

    title = "## " + " → ".join(labels)
    sort_key = section_sort_key(rel.parent.parts)
    return (title, sort_key)


def section_sort_key(parts: tuple[str, ...]) -> tuple[int, ...]:
    key: list[int] = []
    for part in parts:
        m = re.match(r"^(\d+)", part)
        key.append(int(m.group(1)) if m else 999)
    return tuple(key)


def build_index(topic: str) -> str:
    topic_root = ROOT / topic
    index_file = topic_root / "INDEX.md"
    title = TOPIC_TITLES[topic]
    lines = [
        f"# {title} — Index",
        "",
        "Navigation only — note bodies are not modified.",
        "",
        "## Vault",
        md_link(index_file, ROOT / "README.md", "Cyber_Security_Notes"),
        "",
        "## Entry points",
    ]

    entry = TOPIC_ENTRY.get(topic, [])
    if entry:
        for rel_path, label in entry:
            target = topic_root / rel_path
            if target.exists() or topic == "WAPT":
                lines.append(md_link(index_file, target, label))
    else:
        lines.append("- _(none yet)_")

    if topic == "WAPT":
        htb = ROOT / "HTB" / "WEB PENETRATION TESTER" / "WEB PENETRATION TESTER.md"
        lines.extend(
            [
                "",
                "## Status",
                "",
                "Placeholder for future **Web Application Penetration Testing** notes.",
                "",
                md_link(index_file, htb, "HTB — Web Penetration Tester (current material)"),
            ]
        )
        lines.extend(vault_footer(index_file, topic))
        return "\n".join(lines)

    if topic == "tools":
        lines.extend(
            [
                "",
                "## Security tool notes",
                "",
                "_Add per-tool or cheat-sheet notes here as you create them._",
                "",
            ]
        )
        lines.append(md_link(index_file, ROOT / "vault-sessions" / "README.md", "vault-sessions"))
        lines.extend(vault_footer(index_file, topic))
        return "\n".join(lines)

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

    by_section: dict[tuple[str, tuple[int, ...]], list[tuple[tuple, str]]] = {}
    for md in md_files:
        head, sort_key = section_heading(md, topic_root)
        label = humanize_stem(md.stem)
        line = md_link(index_file, md, label)
        by_section.setdefault((head, sort_key), []).append((stem_sort_key(md.stem), line))

    if by_section:
        lines.append("")
        lines.append("## All notes")
        for (head, _sk), items in sorted(by_section.items(), key=lambda x: x[0][1]):
            lines.append("")
            lines.append(head)
            for _, line in sorted(items, key=lambda x: x[0]):
                lines.append(line)

    if topic == "AD-PenTest":
        lines.extend(
            [
                "",
                "## Windows path note",
                "",
                "Some very deep AD folders may be omitted from this auto-generated list.",
                md_link(
                    index_file,
                    topic_root / "AD PenTesting.md",
                    "Open full GitBook table of contents",
                ),
            ]
        )

    lines.extend(vault_footer(index_file, topic))
    return "\n".join(lines)


def vault_footer(index_file: Path, topic: str) -> list[str]:
    out = [
        "",
        "## Vault maintenance",
        "",
        md_link(index_file, ROOT / "vault-sessions" / "README.md", "vault-sessions — structural scripts"),
        "",
        "## Other topics",
        "",
    ]
    for other in TOPICS:
        if other != topic:
            out.append(
                md_link(index_file, ROOT / other / "INDEX.md", other)
            )
    out.append("")
    return out


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