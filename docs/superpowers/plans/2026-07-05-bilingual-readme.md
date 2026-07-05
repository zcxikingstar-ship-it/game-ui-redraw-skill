# Bilingual README Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the minimal README with a professional Chinese-English project landing page.

**Architecture:** Keep one README with top language links, a complete Chinese section, and an equivalent English section. Document only behavior implemented by the Skill and its Pillow helper.

**Tech Stack:** GitHub-flavored Markdown, Codex Skills, Python 3.9+, Pillow

---

### Task 1: Write the bilingual README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Replace the minimal document**

Write these sections in both languages:

```text
Hero and positioning
Why it is different
Feature matrix
Three-stage workflow
Installation by ZIP and Git
Usage examples
Output directory and JSON fields
Requirements
Limitations
Repository structure
Tests
Contributing
```

Use the exact repository URL `https://github.com/zcxikingstar-ship-it/game-ui-redraw-skill`. State prominently that screenshots are references only and delivered assets are newly generated.

- [ ] **Step 2: Verify factual coverage**

Run:

```bash
rg -n '不是抠图|not source-image cropping|assets-draft.json|layout.json|texts.json|output.zip|python3 -m unittest' README.md
```

Expected: every required claim, output, and test command appears.

- [ ] **Step 3: Verify repository checks**

Run:

```bash
python3 -m unittest discover -s game-ui-redraw/tests -v
python3 /Users/galaxy/.codex/skills/.system/skill-creator/scripts/quick_validate.py game-ui-redraw
```

Expected: four tests pass and validation prints `Skill is valid!`.

- [ ] **Step 4: Commit and push**

```bash
git add README.md docs/superpowers/plans/2026-07-05-bilingual-readme.md
git commit -m "expand bilingual documentation"
git push origin main
```
