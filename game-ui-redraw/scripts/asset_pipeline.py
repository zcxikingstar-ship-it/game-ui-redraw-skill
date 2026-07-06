#!/usr/bin/env python3
import argparse
import json
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw


TYPE_DIRS = {
    "background": "background",
    "panel": "panels",
    "button": "buttons",
    "icon": "icons",
    "decoration": "decorations",
}


def _box(value):
    x, y, width, height = map(int, value)
    if min(x, y) < 0 or min(width, height) <= 0:
        raise ValueError(f"invalid bbox: {value}")
    return x, y, width, height


def _asset_status(item):
    return item.get("status", "pending")


def _packaged_assets(manifest):
    return [item for item in manifest.get("assets", []) if _asset_status(item) == "generated"]


def create_review(source_path, manifest, output_path):
    image = Image.open(source_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    for item in manifest.get("assets", []):
        if item.get("status") == "rejected":
            continue
        x, y, width, height = _box(item["bbox"])
        if x + width > image.width or y + height > image.height:
            raise ValueError(f"asset {item['id']} bbox exceeds source image bounds")
        color = "#00e5ff" if item.get("status") == "confirmed" else "#ffcc00"
        draw.rectangle((x, y, x + width - 1, y + height - 1), outline=color, width=2)
        draw.rectangle((x, y, x + 24, min(y + 14, y + height)), fill=color)
        draw.text((x + 2, y + 1), str(item["id"]), fill="black")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def _parse_color(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        if value.startswith("#"):
            value = value[1:]
        if len(value) != 6:
            raise ValueError(f"invalid keyColor: {value}")
        return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))
    if len(value) != 3:
        raise ValueError(f"invalid keyColor: {value}")
    return tuple(map(int, value))


def _remove_background(image, key_color=None, tolerance=24):
    image = image.convert("RGBA")
    key = _parse_color(key_color) or image.getpixel((0, 0))[:3]
    tolerance = int(tolerance)
    pixels = []
    for red, green, blue, _ in image.getdata():
        distance = max(abs(red - key[0]), abs(green - key[1]), abs(blue - key[2]))
        alpha = 0 if distance <= tolerance else min(255, (distance - tolerance) * 8)
        pixels.append((red, green, blue, alpha))
    image.putdata(pixels)
    return image


def _padded_box(box, image_size, padding):
    if padding <= 0:
        return box
    left, top, right, bottom = box
    width, height = image_size
    return (
        max(0, left - padding),
        max(0, top - padding),
        min(width, right + padding),
        min(height, bottom + padding),
    )


def extract_generated_asset(
    sheet_path,
    cell,
    output_path,
    target_size,
    transparent=True,
    key_color=None,
    tolerance=24,
    padding=0,
):
    sheet = Image.open(sheet_path)
    x, y, width, height = _box(cell)
    if x + width > sheet.width or y + height > sheet.height:
        raise ValueError("cell exceeds generated sheet bounds")
    asset = sheet.crop((x, y, x + width, y + height))
    if transparent:
        asset = _remove_background(asset, key_color, tolerance)
        visible = asset.getbbox()
        if not visible:
            raise ValueError("generated cell contains no visible asset")
        asset = asset.crop(_padded_box(visible, asset.size, int(padding)))
        asset.thumbnail(tuple(map(int, target_size)), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", tuple(map(int, target_size)), (0, 0, 0, 0))
        canvas.alpha_composite(
            asset, ((canvas.width - asset.width) // 2, (canvas.height - asset.height) // 2)
        )
    else:
        canvas = asset.convert("RGB").resize(tuple(map(int, target_size)), Image.Resampling.LANCZOS)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)


def _has_transparent_pixels(image):
    if image.mode != "RGBA":
        return False
    return image.getchannel("A").getextrema()[0] < 255


def _validate_manifest(task_dir, manifest, assets):
    canvas_width = int(manifest["canvas"]["width"])
    canvas_height = int(manifest["canvas"]["height"])
    for item in assets:
        x, y, width, height = _box(item["bbox"])
        if x + width > canvas_width or y + height > canvas_height:
            raise ValueError(f"asset {item['id']} exceeds canvas bounds")
        relative = Path(item["filename"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"unsafe filename: {relative}")
        path = task_dir / relative
        if not path.is_file():
            raise ValueError(f"missing asset: {relative}")
        with Image.open(path) as image:
            if image.size != (width, height):
                raise ValueError(
                    f"{relative} expected {width}x{height}, got {image.width}x{image.height}"
                )
            is_background = item["type"] == "background"
            if not is_background and image.mode != "RGBA":
                raise ValueError(f"{relative} must use RGBA")
            if is_background and image.mode not in ("RGB", "RGBA"):
                raise ValueError(f"{relative} must be an RGB image")
            if is_background and _has_transparent_pixels(image):
                raise ValueError(f"{relative} background must be opaque")


def _write_metadata(task_dir, manifest, assets):
    layout = {"canvas": manifest["canvas"], "assets": []}
    for item in assets:
        x, y, width, height = _box(item["bbox"])
        layout["assets"].append(
            {
                "id": item["id"],
                "type": item["type"],
                "filename": item["filename"],
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "zIndex": item["zIndex"],
                "prompt": item["prompt"],
                "status": item["status"],
            }
        )
    (task_dir / "layout.json").write_text(
        json.dumps(layout, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (task_dir / "texts.json").write_text(
        json.dumps({"texts": manifest.get("texts", [])}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    style_guide = manifest.get("styleGuide") or manifest.get("style-guide") or {}
    (task_dir / "style-guide.json").write_text(
        json.dumps(style_guide, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _create_contact_sheet(task_dir, assets):
    tiles = []
    for item in assets:
        image = Image.open(task_dir / item["filename"]).convert("RGBA")
        image.thumbnail((160, 120), Image.Resampling.LANCZOS)
        tiles.append((item, image.copy()))
    width = 400
    height = max(100, 20 + len(tiles) * 150)
    sheet = Image.new("RGB", (width, height), "#20242b")
    draw = ImageDraw.Draw(sheet)
    for index, (item, image) in enumerate(tiles):
        top = 15 + index * 150
        checker = Image.new("RGB", (170, 125), "#eeeeee")
        sheet.paste(checker, (10, top))
        sheet.paste(image, (15, top + 3), image)
        draw.text((195, top + 8), f"{item['id']}  {item['type']}", fill="white")
        draw.text((195, top + 30), item["filename"], fill="#aeb7c2")
    sheet.save(task_dir / "contact-sheet.png")


def package_task(task_dir, manifest):
    task_dir = Path(task_dir)
    assets = _packaged_assets(manifest)
    _validate_manifest(task_dir, manifest, assets)
    _write_metadata(task_dir, manifest, assets)
    _create_contact_sheet(task_dir, assets)
    allowed = {
        "layout.json",
        "texts.json",
        "style-guide.json",
        "contact-sheet.png",
        "review-numbered.png",
    }
    allowed.update(item["filename"] for item in assets)
    with zipfile.ZipFile(task_dir / "output.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for relative in sorted(allowed):
            path = task_dir / relative
            if path.is_file():
                archive.write(path, relative)


def _load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Prepare regenerated game UI assets")
    subparsers = parser.add_subparsers(dest="command", required=True)

    review = subparsers.add_parser("review")
    review.add_argument("--source", required=True)
    review.add_argument("--manifest", required=True)
    review.add_argument("--output", required=True)

    split = subparsers.add_parser("split")
    split.add_argument("--sheet", required=True)
    split.add_argument("--batch", required=True)
    split.add_argument("--task-dir", required=True)

    package = subparsers.add_parser("package")
    package.add_argument("--manifest", required=True)
    package.add_argument("--task-dir", required=True)

    args = parser.parse_args()
    if args.command == "review":
        create_review(args.source, _load_json(args.manifest), args.output)
    elif args.command == "split":
        batch = _load_json(args.batch)
        for item in batch["assets"]:
            extract_generated_asset(
                args.sheet,
                item["cell"],
                Path(args.task_dir) / item["filename"],
                (item["width"], item["height"]),
                item["type"] != "background",
                item.get("keyColor"),
                item.get("tolerance", 24),
                item.get("padding", 0),
            )
    else:
        package_task(Path(args.task_dir), _load_json(args.manifest))


if __name__ == "__main__":
    main()
