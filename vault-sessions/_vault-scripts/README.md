# Vault maintenance scripts

Python utilities used when migrating and validating this Obsidian vault (GitBook → Markdown, images, paths). They do not change note bodies unless you run them explicitly.

| Script | Purpose |
| --- | --- |
| `generate_topic_indexes.py` | Regenerate per-topic `INDEX.md` wikilink maps |
| `organize_attachments_by_project.py` | Group `attachments/` by project and rewrite image paths |
| `gitbook_migrate_images.py` | Copy `.gitbook/assets` into `attachments/` |
| `gitbook_fix_paths.py` | Fix relative image paths in Markdown |
| `gitbook_fix_longpaths.py` | Shorten very long Windows paths (AD-PenTest) |
| `gitbook_migration_analyze.py` | Analyze migration state |
| `gitbook_validate_images.py` | Validate image references |

Run from anywhere, e.g.:

```powershell
python "D:\R00T\Cyber_Security\vault-sessions\_vault-scripts\generate_topic_indexes.py"
```

## Navigation

- [[../README|vault-sessions]]
- [[../../tools/INDEX|tools — study notes]]
- [[../../README|Cyber_Security_Notes]]