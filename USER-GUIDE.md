# Cyber Security Notes — User Guide

How to add notes, images, and navigation in this vault without breaking structure. **Study content lives in topic folders; automation lives in `vault-sessions`.**

Quick links: [Vault hub](README.md) · [Regenerate indexes](#regenerate-index-files) · [Images](#images-and-attachments)

---

## 1. How the vault is organized

```
Cyber_Security/
├── README.md              ← Start here (all topics)
├── USER-GUIDE.md          ← This file
├── INDEX.md               ← (per topic, below)
├── attachments/           ← All images, grouped by topic
├── vault-sessions/        ← Scripts only (not study notes)
└── <Topic>/               ← Your actual notes
    ├── INDEX.md           ← Auto-generated link map (GitHub + Obsidian)
    ├── README.md          ← Human-written topic landing page
    └── … notes …
```

### Study topics (8)

| Folder | Use for |
| --- | --- |
| [AD-PenTest](AD-PenTest/INDEX.md) | Active Directory pentest / red team |
| [AI-LLM-Security](AI-LLM-Security/INDEX.md) | AI & LLM security (incl. CWL) |
| [Cloud Security](Cloud%20Security/INDEX.md) | Cloud security (CWL) |
| [HTB](HTB/INDEX.md) | Hack The Box academy tracks |
| [Practical-Ethical-Hacking](Practical-Ethical-Hacking/INDEX.md) | Practical ethical hacking labs |
| [tools](tools/INDEX.md) | Security **tool** cheat sheets (nmap, Burp, …) |
| [VAPT](VAPT/INDEX.md) | Vulnerability assessment & pentest notes |
| [WAPT](WAPT/INDEX.md) | Future web-app pentest notes (placeholder) |

### Not a study topic

| Folder | Use for |
| --- | --- |
| [vault-sessions](vault-sessions/README.md) | `generate_topic_indexes.py`, GitBook migration, attachment helpers |

**Rule:** Never put lab/course notes inside `vault-sessions/` or `.obsidian/`.

---

## 2. Where to put a new note

1. Pick the **topic folder** (table above).
2. Mirror **existing layout** in that topic:
   - **HTB:** `HTB/WEB PENETRATION TESTER/<module-folder>/<note>.md`
   - **CWL courses:** `AI-LLM-Security/CWL/…` or `Cloud Security/CWL/…`
   - **GitBook-style:** nested folders under the topic (like AD-PenTest) — follow numbering if the section already uses it.
3. Create a **`.md` file** only; do not rename existing folders unless you are deliberately restructuring (and then fix links).

**New top-level topic?** Add a folder at vault root, add rows to [README.md](README.md), extend `TOPICS` in `vault-sessions/_vault-scripts/generate_topic_indexes.py`, then regenerate indexes.

---

## 3. README vs INDEX vs SUMMARY

| File | Who maintains | Purpose |
| --- | --- | --- |
| **README.md** (per topic) | **You** | Short intro, “what this section is”, curated links, cards/tables. |
| **INDEX.md** (per topic) | **Script** | Full link map for GitHub + Obsidian. **Do not edit by hand** — regenerate. |
| **SUMMARY.md** / **AD PenTesting.md** etc. | Legacy GitBook | Old table of contents; keep if you still use them; optional to update. |
| **[README.md](README.md)** (vault root) | **You** | Links to all topics; update when you add a topic or change main entry points. |

### When you add or move notes

1. Write or edit the **note body** (content is the source of truth).
2. Optionally update the topic **README** if it’s a major new track or landing-page worthy.
3. **Regenerate** that topic’s **INDEX** (see below) so GitHub and Obsidian navigation stay current.
4. You do **not** need to edit SUMMARY unless you still rely on GitBook-style TOCs.

---

## 4. Links (GitHub + Obsidian)

| Where | Recommended format | Why |
| --- | --- | --- |
| **INDEX.md** (generated) | `[Label](relative/path/to-note.md)` | Works on GitHub and in Obsidian |
| **Inside study notes** | Relative Markdown `[text](../other.md)` **or** Obsidian `[[Note name]]` | Wikilinks are fine in Obsidian; relative `.md` links work everywhere |
| **Vault root README** | Markdown links with `%20` for spaces | GitHub-friendly |

**Relative path tip:** From a note, count folders up to `Cyber_Security`, then down into `attachments/…` or sibling notes. Example from a deep AD lab note:

```markdown
![diagram](../../../attachments/AD-PenTest-Images/my-diagram.png)
```

In Obsidian, clicking a relative `.md` link opens the note; wikilinks also work if you prefer them in personal notes.

---

## 5. Images and attachments

All images live under **`attachments/`**, in one subfolder per topic:

| Topic folder | Image directory |
| --- | --- |
| AD-PenTest | `attachments/AD-PenTest-Images/` |
| AI-LLM-Security | `attachments/AI-LLM-Security-Images/` |
| HTB | `attachments/HTB-Images/` |
| Practical-Ethical-Hacking | `attachments/Practical-Ethical-Hacking-Images/` |
| VAPT | `attachments/VAPT-Images/` |
| Cloud Security (new images) | Create `attachments/Cloud Security-Images/` or `Cloud-Security-Images/` and use consistently |
| tools / WAPT | Create `{Topic}-Images` when you add screenshots |

### Adding an image to a note

1. Save the file into the correct **`attachments/<Topic>-Images/`** folder (clear filename, e.g. `kerberoast-netexec-flow.png`).
2. In the note, reference it with a **relative** path from the note’s folder to that file.
3. Markdown image syntax:

```markdown
![short description](../../../attachments/AD-PenTest-Images/kerberoast-netexec-flow.png)
```

4. GitBook-style frontmatter cover (if you use it):

```yaml
cover: ../../../attachments/AD-PenTest-Images/my-cover.png
```

### Fix or reorganize many images

After bulk moves or bad paths, you can run (optional):

```powershell
python "D:\R00T\Cyber_Security\vault-sessions\_vault-scripts\organize_attachments_by_project.py"
```

That script knows these projects: `AD-PenTest`, `AI-LLM-Security`, `HTB`, `Practical-Ethical-Hacking`, `VAPT`. For **Cloud Security**, keep paths manual or extend the `PROJECTS` list in that script later.

**Do not** store images inside topic folders (keeps repo size and linking consistent).

---

## 6. Regenerate INDEX files

After **adding**, **renaming**, or **moving** any `.md` note (except `INDEX.md` itself):

```powershell
python "D:\R00T\Cyber_Security\vault-sessions\_vault-scripts\generate_topic_indexes.py"
```

This rewrites every topic’s `INDEX.md` with:

- Short section titles (e.g. `Complete guide → 1. Reconnaissance & access`)
- Clickable Markdown links for GitHub
- Cross-links to other topics and `vault-sessions`

To tune how headings read (without moving files), edit **`SEGMENT_LABEL`** and **`MODULE_SHORT`** in `generate_topic_indexes.py`, then run the command again.

### AD-PenTest and Windows long paths

Some very deep AD paths may be missing from INDEX on Windows. Use [AD PenTesting.md](AD-PenTest/AD%20PenTesting.md) as the complete GitBook TOC, or run `gitbook_fix_longpaths.py` only when you intentionally shorten folder names.

---

## 7. Day-to-day workflows

### A. New lesson / one-off note

1. Create `Topic/.../my-new-lesson.md`.
2. Add images under `attachments/<Topic>-Images/`.
3. Link images with relative paths.
4. Run `generate_topic_indexes.py`.
5. Commit/sync (Obsidian Git or git) when ready.

### B. New HTB module section

1. Add folder under `HTB/WEB PENETRATION TESTER/` matching existing naming (`N.-module-name/`).
2. Add `README.md` in that module folder if other modules have one.
3. Add lesson `.md` files.
4. Regenerate indexes.
5. Optional: add one line to [HTB/README.md](HTB/README.md) if it’s a new track (not just another lesson).

### C. New CWL / course chapter (AI or Cloud)

1. Follow existing `CWL/<Course name>/<section>/` pattern.
2. Use `attachments/AI-LLM-Security-Images/` or a dedicated Cloud images folder.
3. Regenerate indexes.
4. Optional: extend [AI LLM Security.md](AI-LLM-Security/AI%20LLM%20Security.md) map-of-content if you use it in Obsidian.

### D. New security tool cheat sheet

1. Create `tools/<tool-name>.md` (e.g. `tools/bloodhound.md`).
2. Put screenshots in `attachments/tools-Images/` if you create that folder (or a subfolder you define).
3. Regenerate indexes — `tools/INDEX.md` will list the new file.

### E. WAPT content (future)

1. Add notes under `WAPT/` (not under HTB) when you want a separate web-app corpus.
2. Until then, HTB Web Pentester stays the reference; [WAPT/INDEX.md](WAPT/INDEX.md) explains that.

---

## 8. What not to change casually

| Item | Reason |
| --- | --- |
| Note **bodies** (except links/images you add) | Your learning content |
| Deep **folder renames** in AD-PenTest | Breaks links and Windows path limits |
| Hand-editing **INDEX.md** | Overwritten on next generate |
| Committing **`.obsidian/workspace.json`** | Personal UI state (often gitignored) |

---

## 9. Obsidian vs GitHub

| Feature | Obsidian | GitHub |
| --- | --- | --- |
| Open vault | Folder `Cyber_Security` | Repo browser |
| Navigation | Graph, `INDEX`, wikilinks | `README.md` → topic `INDEX.md` |
| Images | Relative paths | Same relative paths in repo |
| Sync | Obsidian Git plugin (if enabled) | `git push` |

Use **relative Markdown links** in anything you want readable on GitHub (INDEX, root README, this guide). Wikilinks inside personal notes are optional.

---

## 10. Checklist (print-friendly)

**New note**

- [ ] File under correct **topic** folder  
- [ ] Images in `attachments/<Topic>-Images/`  
- [ ] Relative image paths in note  
- [ ] Ran `generate_topic_indexes.py`  
- [ ] Updated topic **README** only if it’s a major addition  

**New topic (rare)**

- [ ] New folder at vault root  
- [ ] `README.md` + empty or generated `INDEX.md`  
- [ ] Row in vault [README.md](README.md)  
- [ ] `TOPICS` in `generate_topic_indexes.py`  
- [ ] `attachments/<Topic>-Images/` if you use images  

**Maintenance scripts**

- [ ] Only in `vault-sessions/_vault-scripts/`  
- [ ] Tool notes only in `tools/`  

---

## 11. Help

| Need | Action |
| --- | --- |
| Regenerate navigation | `python vault-sessions\_vault-scripts\generate_topic_indexes.py` |
| Script list | [vault-sessions/_vault-scripts/README.md](vault-sessions/_vault-scripts/README.md) |
| Vault hub | [README.md](README.md) |

If INDEX labels feel too long or too short, adjust `generate_topic_indexes.py` maps and regenerate — **paths and note text stay unchanged.**