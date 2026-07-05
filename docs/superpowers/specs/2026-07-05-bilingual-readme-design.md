# Bilingual README Design

## Goal

Turn the minimal repository README into a professional bilingual landing page that helps Chinese and English Codex users understand, install, evaluate, and share `game-ui-redraw`.

## Structure

Use one `README.md` with a language navigation bar. Present the complete Chinese version first and the complete English version second so each audience can read continuously without alternating languages paragraph by paragraph.

Both language sections must cover the same facts:

1. Product positioning and the key distinction: source screenshots are references only; delivered assets are newly generated rather than cropped.
2. Supported asset types and the three-stage review, generation, and correction workflow.
3. Installation from ZIP and Git clone.
4. Invocation examples and expected output files.
5. Repository structure, runtime requirements, tests, limitations, and contribution guidance.

## Tone and Accuracy

Use confident product language, concrete examples, compact tables, and copyable commands. Avoid unsupported claims such as pixel-perfect reconstruction, fully automatic segmentation, guaranteed font recovery, or perfect reconstruction of occluded details.

Do not add badges that depend on nonexistent CI, releases, package registries, or external services. Do not add a license because the owner has not selected one.

## Acceptance

- Chinese and English sections are meaningfully equivalent.
- Installation commands use the real repository URL and current folder layout.
- Output names match the implemented Skill.
- The README prominently states the review gate and no-source-cropping rule.
- Markdown links and headings render correctly.
