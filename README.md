<div align="center">

# Game UI Redraw

### 一张游戏截图，拆解整套 UI，并用 AI 重新绘制为可交付素材

**Screenshot → Structure Review → Brand-new AI Assets → PNG / JSON / ZIP**

[简体中文](#简体中文) · [English](#english) · [下载 ZIP](https://github.com/zcxikingstar-ship-it/game-ui-redraw-skill/raw/main/game-ui-redraw-skill.zip)

</div>

---

# 简体中文

## 这是什么？

`game-ui-redraw` 是一个面向 Codex 的游戏 UI 资产重绘 Skill。

上传一张游戏主页、活动页或功能页截图后，它会识别画面中的背景、面板、按钮、图标、装饰和文字，先生成带编号的审核图；等你确认后，再调用 Codex 内置生图能力重新绘制无字素材，并输出透明 PNG、布局坐标、文字数据、素材总览和 ZIP。

> **核心原则：不是抠图。**
>
> 原截图只用于识别结构和参考美术风格。最终交付的视觉素材全部由 AI 重新生成，不把原图裁切像素伪装成新素材。

## 为什么值得用？

| 传统处理方式 | Game UI Redraw |
|---|---|
| 手动标记几十个元素 | 自动整理元素清单与坐标 |
| 抠图后残留文字、遮挡和背景 | 重新生成无字底图 |
| 设计师逐个命名、分类 | 自动按背景、面板、按钮、图标、装饰归档 |
| 一次性图片，缺少结构信息 | 同时输出 PNG、布局 JSON 和文字 JSON |
| 批量重做成本高 | 首轮分组生成，差项按编号单独重绘 |

## 能做什么？

- 识别 `background`、`panel`、`button`、`icon`、`decoration` 和独立文字。
- 生成带编号的 `review-numbered.png`，确认后才开始消耗生图次数。
- 分组生成全新 AI 素材表，再自动分离、去背景、裁透明边缘并适配原显示尺寸。
- 将文字与底图分离，保留文字内容、坐标、对齐方式和近似颜色。
- 输出 `layout.json` 和 `style-guide.json`，保留素材结构、坐标、风格规则和提示词。
- 为价格、倒计时、数量、玩家名、等级等动态文字保留结构化角色。
- 在用户明确要求时，为按钮、图标和面板补生成常见状态。
- 生成 `contact-sheet.png`，快速浏览整批结果。
- 指定编号单独重绘，不必整批重新开始。
- 打包为 `output.zip`，自动排除原截图、草稿清单、AI 素材表和测试文件。

## 工作流程

```text
上传截图
   ↓
Codex 识别 UI 元素与文字
   ↓
生成编号审核图 + assets-draft.json
   ↓
你确认、删除、改名或修正分类
   ↓
按类别生成全新 AI 素材表
   ↓
分离透明 PNG + 生成坐标数据
   ↓
总览复检 → 指定差项单独重绘
   ↓
输出 layout.json / texts.json / style-guide.json / contact-sheet.png / output.zip
```

人工确认不是多余步骤：它能在批量生图前拦住漏识别、错误分类和不需要的元素，避免浪费时间和生成次数。

## 安装

### 方法一：直接下载

1. [下载 `game-ui-redraw-skill.zip`](https://github.com/zcxikingstar-ship-it/game-ui-redraw-skill/raw/main/game-ui-redraw-skill.zip)。
2. 解压后，将 `game-ui-redraw` 文件夹复制到：

```text
~/.codex/skills/
```

3. 重启 Codex。

### 方法二：Git 克隆

```bash
git clone https://github.com/zcxikingstar-ship-it/game-ui-redraw-skill.git
cp -R game-ui-redraw-skill/game-ui-redraw ~/.codex/skills/
```

## 使用

在 Codex 中上传一张游戏截图，然后输入：

```text
使用 $game-ui-redraw 识别并重新生成这张截图里的 UI 素材
```

也可以自然地描述需求：

```text
分析这张游戏主页，先给我编号审核图，确认后生成无字按钮、图标和面板。
```

Skill 会先停在审核阶段。你可以回复：

```text
确认
```

或者按编号修正：

```text
删除 07；把 12 改成按钮；03 的范围向右扩大 20 像素。
```

首轮生成后，可以继续说：

```text
重绘 04，让金属边框更接近原图；其他素材保持不变。
```

## 输出内容

```text
game-ui-redraw-YYYYMMDD-HHMMSS/
├── background/
├── panels/
├── buttons/
├── icons/
├── decorations/
├── assets-draft.json
├── review-numbered.png
├── layout.json
├── texts.json
├── style-guide.json
├── contact-sheet.png
└── output.zip
```

### `layout.json`

每个非文字元素包含：

| 字段 | 说明 |
|---|---|
| `id` | 审核和重绘使用的稳定编号 |
| `type` | 背景、面板、按钮、图标或装饰 |
| `filename` | 生成素材的相对路径 |
| `x / y` | 元素在原截图中的左上角坐标 |
| `width / height` | 原显示尺寸 |
| `zIndex` | 建议层级 |
| `prompt` | 当前素材使用的重绘提示词 |
| `status` | 待确认、已确认或已生成 |

### `texts.json`

文字独立记录 `text`、矩形坐标、对齐方式、近似颜色和 `role`，方便后续换文案、做多语言或在游戏引擎中重新排版。`role` 可标记价格、倒计时、数量、玩家名、等级等动态字段。

### `style-guide.json`

记录主色、材质、边框、圆角、光效、UI 密度和整体美术描述，方便同一产品后续继续生成一致风格的页面或组件。

## 运行要求

- Codex，且当前环境可以使用内置图片生成能力。
- Python 3.9 或更高版本。
- [Pillow](https://python-pillow.org/)。

本地验证前可安装依赖：

```bash
python3 -m pip install pillow pyyaml
```

本项目不需要部署 Web 服务，也不需要下载本地分割模型。

## 能力边界

- 单张截图无法提供被遮挡区域的真实设计，缺失部分只能由 AI 合理补全。
- 输出目标是视觉高度接近，不承诺逐像素复刻。
- 第一版不恢复原字体文件、不生成 PSD/Figma、不推断按钮按下态或截图中不存在的页面。
- 人物、武器、建筑和复杂场景物件默认不作为独立 UI 元素拆分。
- 透明背景依赖生成素材使用纯色隔离背景；复杂半透明光效可能需要单项重绘。
- 请确保你有权使用输入截图及其视觉风格。

## 仓库结构

```text
.
├── README.md
├── game-ui-redraw-skill.zip
├── game-ui-redraw/
    ├── SKILL.md
    ├── agents/
    │   └── openai.yaml
    ├── references/
    │   ├── export-targets.md
    │   └── page-types.md
    ├── scripts/
    │   └── asset_pipeline.py
└── tests/
    └── test_asset_pipeline.py
```

确定性的图片处理由一个小型 Pillow 脚本完成；识别、判断和重绘仍由 Codex 负责，没有额外服务层。

## 测试

```bash
python3 -m unittest discover -s tests -v
python3 /path/to/skill-creator/scripts/quick_validate.py game-ui-redraw
```

测试覆盖审核框图、AI 素材表分离、透明通道、尺寸校验、状态跳过、风格文件、坐标打包，以及 ZIP 排除原图和中间文件。

## 参与改进

欢迎提交 Issue 或 Pull Request。报告问题时，建议附上：

- 输入截图尺寸和页面类型；
- 出错的素材编号；
- `assets-draft.json` 中对应元素；
- 期望结果与实际结果；
- 是否发生在识别、生成、分离还是打包阶段。

---

# English

## What is it?

`game-ui-redraw` is a Codex Skill for reconstructing game UI assets from screenshots.

Give it a game lobby, event screen, or feature-page screenshot. It identifies backgrounds, panels, buttons, icons, decorations, and text, then produces a numbered review image. After you approve the structure, it uses Codex image generation to redraw clean text-free assets and exports transparent PNGs, layout coordinates, text metadata, a contact sheet, and a ZIP archive.

> **The key distinction: this is AI redraw, not source-image cropping.**
>
> The screenshot is used only for structure recognition and visual style reference. Delivered visual assets are newly generated instead of repackaged source pixels.

## Why use it?

| Traditional workflow | Game UI Redraw |
|---|---|
| Manually mark dozens of elements | Produce a structured element list and coordinates |
| Crops retain text, occlusion, and background noise | Regenerate clean text-free artwork |
| Rename and sort every file by hand | Organize backgrounds, panels, buttons, icons, and decorations |
| Receive images without layout context | Export PNG assets plus layout and text JSON |
| Restart an expensive batch after one bad result | Regenerate only the asset IDs that need correction |

## Features

- Recognizes `background`, `panel`, `button`, `icon`, `decoration`, and separate text layers.
- Creates `review-numbered.png` and waits for approval before image generation.
- Generates brand-new grouped AI sprite sheets, then separates assets, removes the flat background, trims transparency, and fits each asset to its original display size.
- Keeps text separate from artwork while preserving content, coordinates, alignment, and approximate color.
- Writes `layout.json` and `style-guide.json` with structure, coordinates, visual rules, and prompts.
- Keeps structured roles for dynamic text such as prices, countdowns, quantities, player names, and levels.
- Generates common button, icon, or panel states only when the user explicitly asks for state extensions.
- Builds `contact-sheet.png` for fast visual inspection.
- Regenerates a single numbered asset without restarting the full batch.
- Packages `output.zip` without the source screenshot, draft manifest, AI sprite sheets, or test files.

## Workflow

```text
Upload screenshot
   ↓
Codex identifies UI assets and text
   ↓
Create numbered review image + assets-draft.json
   ↓
Approve, delete, rename, or reclassify elements
   ↓
Generate brand-new AI sprite sheets by category
   ↓
Separate transparent PNGs + write layout metadata
   ↓
Review contact sheet → regenerate selected asset IDs
   ↓
Export layout.json / texts.json / style-guide.json / contact-sheet.png / output.zip
```

The review gate prevents missing, misclassified, or unwanted elements from consuming generation time.

## Installation

### Option 1: Download the ZIP

1. [Download `game-ui-redraw-skill.zip`](https://github.com/zcxikingstar-ship-it/game-ui-redraw-skill/raw/main/game-ui-redraw-skill.zip).
2. Extract it and copy the `game-ui-redraw` folder into:

```text
~/.codex/skills/
```

3. Restart Codex.

### Option 2: Clone with Git

```bash
git clone https://github.com/zcxikingstar-ship-it/game-ui-redraw-skill.git
cp -R game-ui-redraw-skill/game-ui-redraw ~/.codex/skills/
```

## Usage

Attach a game screenshot in Codex and enter:

```text
Use $game-ui-redraw to identify and redraw the UI assets in this screenshot.
```

You can also describe the workflow naturally:

```text
Analyze this game lobby. Show me the numbered review image first, then generate text-free buttons, icons, and panels after I approve it.
```

At the review gate, reply:

```text
Confirm all assets.
```

Or correct specific IDs:

```text
Remove 07, classify 12 as a button, and extend the box for 03 by 20 pixels to the right.
```

After the first generation pass:

```text
Regenerate 04 with a border closer to the reference. Keep every other asset unchanged.
```

## Output

```text
game-ui-redraw-YYYYMMDD-HHMMSS/
├── background/
├── panels/
├── buttons/
├── icons/
├── decorations/
├── assets-draft.json
├── review-numbered.png
├── layout.json
├── texts.json
├── style-guide.json
├── contact-sheet.png
└── output.zip
```

### `layout.json`

Each non-text asset includes:

| Field | Meaning |
|---|---|
| `id` | Stable ID used for review and regeneration |
| `type` | Background, panel, button, icon, or decoration |
| `filename` | Relative generated-asset path |
| `x / y` | Top-left position in source-image coordinates |
| `width / height` | Original display size |
| `zIndex` | Suggested layer order |
| `prompt` | Redraw prompt used for the current asset |
| `status` | Pending, confirmed, or generated |

### `texts.json`

Text stays separate and retains its content, bounding box, alignment, approximate color, and `role`, making localization and runtime rendering easier. Roles can mark prices, countdowns, quantities, player names, levels, and other dynamic fields.

### `style-guide.json`

Captures palette, materials, borders, corner radius, lighting, UI density, and overall art direction so later screens or components can stay visually consistent with the same product.

## Requirements

- Codex with image generation available in the current environment.
- Python 3.9 or newer.
- [Pillow](https://python-pillow.org/).

Install local validation dependencies with:

```bash
python3 -m pip install pillow pyyaml
```

No web service or local segmentation model is required.

## Limitations

- A single screenshot cannot reveal the true design of occluded areas; missing details are AI estimates.
- The target is strong visual similarity, not pixel-perfect reconstruction.
- The first version does not recover font files, export PSD/Figma documents, infer pressed states, or invent unseen pages.
- Characters, weapons, buildings, and complex scene objects are not separated as standalone UI assets by default.
- Transparency extraction relies on a flat generated background; complex translucent effects may need individual regeneration.
- Make sure you have the right to use the source screenshot and its visual style.

## Repository layout

```text
.
├── README.md
├── game-ui-redraw-skill.zip
├── game-ui-redraw/
    ├── SKILL.md
    ├── agents/
    │   └── openai.yaml
    ├── references/
    │   ├── export-targets.md
    │   └── page-types.md
    ├── scripts/
    │   └── asset_pipeline.py
└── tests/
    └── test_asset_pipeline.py
```

One small Pillow script handles deterministic image processing. Codex remains responsible for recognition, judgment, and image generation; there is no extra service layer.

## Tests

```bash
python3 -m unittest discover -s tests -v
python3 /path/to/skill-creator/scripts/quick_validate.py game-ui-redraw
```

Tests cover numbered review overlays, generated-sheet separation, transparency, dimension validation, skipped statuses, style metadata, packaging, and exclusion of source or intermediate files from the ZIP.

## Contributing

Issues and pull requests are welcome. A useful report includes:

- Source-image dimensions and screen type;
- The affected asset ID;
- The matching entry from `assets-draft.json`;
- Expected and actual output;
- Whether the problem occurred during recognition, generation, separation, or packaging.
