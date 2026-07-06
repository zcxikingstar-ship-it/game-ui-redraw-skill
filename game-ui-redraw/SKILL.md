---
name: game-ui-redraw
description: Identify a game UI from an attached homepage or screen screenshot, review numbered elements with the user, then use Codex image generation to redraw brand-new text-free backgrounds, panels, buttons, icons, and decorations. Use when the user asks to recognize, recreate, redraw, regenerate, or export game UI assets from a screenshot. Never deliver crops from the source screenshot.
---

# Game UI Redraw

Turn one screenshot into newly generated, text-free UI assets plus layout and text metadata. Treat the screenshot only as visual reference. Never use pixels cropped from the source as delivered assets.

## Requirements

- Use `view_image` to inspect a local screenshot before analysis.
- Use `image_gen` for every delivered visual asset.
- Use `scripts/asset_pipeline.py` for review overlays, generated-sheet separation, validation, contact sheets, and ZIP creation.
- Keep the original display size for every asset. Do not create `@2x` variants.
- Do not infer unseen pages, interaction states, fonts, characters, weapons, buildings, or scene objects.
- Deliver non-background UI elements as RGBA PNG with real alpha transparency, never JPG, WebP, or flat-color fake transparency.
- Read `references/page-types.md` when classifying a lobby, event, shop, popup, or battle HUD screenshot. Read `references/export-targets.md` when the user asks for Unity, Cocos, web, or engine-ready metadata.

## 1. Identify and review

Create a new task directory outside this skill, named `game-ui-redraw-YYYYMMDD-HHMMSS`. Analyze:

- page type, if recognizable
- `background`
- `panel`
- `button`
- `icon`
- `decoration`
- text, stored separately and never baked into generated UI assets
- style guide: palette, materials, borders, corner radius, lighting, density, and overall art style

Write `assets-draft.json`:

```json
{
  "canvas": {"width": 1170, "height": 2532},
  "pageType": "lobby",
  "assets": [
    {
      "id": "01",
      "type": "button",
      "name": "start",
      "filename": "buttons/start-01.png",
      "bbox": [420, 2100, 330, 120],
      "zIndex": 10,
      "prompt": "ornate gold and red start button, no letters, transparent background",
      "status": "pending"
    }
  ],
  "texts": [
    {
      "id": "t01",
      "text": "开始游戏",
      "bbox": [485, 2135, 200, 48],
      "align": "center",
      "color": "#fff4c2",
      "role": "static"
    }
  ],
  "styleGuide": {
    "palette": ["#7a1620", "#f2c35a"],
    "materials": ["polished gold", "red lacquer"],
    "borders": "thick beveled gold outlines",
    "cornerRadius": "large rounded button corners",
    "lighting": "top-left highlights with soft inner glow",
    "density": "ornate fantasy lobby",
    "notes": "high-contrast primary actions, text kept separate"
  }
}
```

`bbox` is `[x, y, width, height]` in source-image pixels. Use directories `background/`, `panels/`, `buttons/`, `icons/`, and `decorations/`. For text `role`, use `static`, `price`, `countdown`, `quantity`, `playerName`, `level`, or `unknown`.

Generate the numbered review image:

```bash
python3 <skill-dir>/scripts/asset_pipeline.py review \
  --source <screenshot> \
  --manifest <task-dir>/assets-draft.json \
  --output <task-dir>/review-numbered.png
```

Show `review-numbered.png` and summarize uncertain items. Stop for user confirmation. Apply additions, deletions, renames, category changes, and box corrections to the manifest. Mark accepted assets `confirmed`; leave uncertain assets pending and do not generate them.

## 2. Generate brand-new assets

Group 2–6 confirmed assets of the same type. For each group:

1. Call `image_gen` with the full screenshot as style reference.
2. Explicitly request a clean, newly drawn sprite sheet; no copied pixels, letters, numbers, labels, watermarks, shadows outside cells, or source-image background.
3. Place each requested asset in a separate non-overlapping cell on a flat chroma background whose color does not appear in the assets.
4. Preserve each element's shape, palette, material, border treatment, lighting, and game-art style.
5. Write a batch JSON using the actual generated sheet cell bounds:

```json
{
  "assets": [
    {
      "id": "01",
      "type": "button",
      "filename": "buttons/start-01.png",
      "cell": [0, 0, 512, 512],
      "width": 330,
      "height": 120,
      "keyColor": "#00ff00",
      "tolerance": 24,
      "padding": 2
    }
  ]
}
```

Split only the AI-generated sheet:

```bash
python3 <skill-dir>/scripts/asset_pipeline.py split \
  --sheet <generated-sheet.png> \
  --batch <batch.json> \
  --task-dir <task-dir>
```

Never pass the source screenshot to `split`. Change each successful asset status to `generated`. If one group fails, retry only that group.

Optional states: only when the user explicitly asks to extend component states, generate extra assets for confirmed buttons, icons, or panels. Use suffixes such as `-normal`, `-pressed`, `-disabled`, `-selected`, or `-highlighted`; keep coordinates for the original screenshot asset unchanged and add state assets as separate generated files.

## 3. Package and correct

Package after all confirmed assets exist:

```bash
python3 <skill-dir>/scripts/asset_pipeline.py package \
  --manifest <task-dir>/assets-draft.json \
  --task-dir <task-dir>
```

This validates bounds, dimensions, paths, and transparency, then writes `layout.json`, `texts.json`, `style-guide.json`, `contact-sheet.png`, and `output.zip`. The ZIP excludes the source screenshot, source crops, draft manifests, generated sheets, and tests.

Show `contact-sheet.png` for visual review. When the user names a bad ID, regenerate only that asset, replace its file without changing coordinates, rerun `package`, and show the updated contact sheet.

## Acceptance

- Every confirmed non-text element has one newly generated file.
- Non-background UI elements are RGBA PNG; backgrounds are opaque.
- Files exactly match confirmed display dimensions.
- Text-free assets contain no original labels.
- JSON references resolve and all boxes fit the source canvas.
- `texts.json` keeps dynamic text roles without translating or baking text into images.
- `style-guide.json` captures enough visual rules to guide later same-product UI work.
- Report occluded details as AI estimates, never as exact reconstruction.
