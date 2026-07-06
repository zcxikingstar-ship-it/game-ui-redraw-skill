# Export Targets

Use this reference when the user asks for engine-ready metadata. The default output remains `layout.json`, `texts.json`, `style-guide.json`, PNG files, and `output.zip`.

## Generic

Keep source-image pixel coordinates with top-left origin. Each asset has `id`, `type`, `filename`, `x`, `y`, `width`, `height`, `zIndex`, `prompt`, and `status`. Text entries keep `text`, `bbox`, `align`, `color`, and `role`.

## Unity UGUI

Add a separate mapping note or metadata section only when requested. Use top-left screenshot coordinates as the source of truth, recommend `RectTransform` size from `width` and `height`, and record anchor or pivot assumptions explicitly. For stretchable buttons or panels, add suggested `slice` values as left, right, top, and bottom pixel insets.

## Cocos Creator

Use node-style metadata when requested: asset path, position converted from the chosen canvas origin, size, z order, and optional nine-slice insets. Keep text nodes separate from sprites and preserve dynamic text roles for later localization.

## Web, Pixi, Or Phaser

Use absolute pixel layout or a sprite manifest when requested. Keep the original canvas size, asset rectangles, z order, and text roles. Do not emit CSS, JavaScript, or scene code unless the user explicitly asks for runnable integration.

## Slice Hints

For reusable panels and buttons, suggest a `slice` object only when the border and center area are clear:

```json
"slice": {"left": 24, "right": 24, "top": 18, "bottom": 18}
```

Do not guess slice values for irregular icons, decorative objects, full backgrounds, or heavily occluded elements.
