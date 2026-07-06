import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image


SCRIPT = Path(__file__).parents[1] / "game-ui-redraw" / "scripts" / "asset_pipeline.py"
SPEC = importlib.util.spec_from_file_location("asset_pipeline", SCRIPT)
asset_pipeline = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(asset_pipeline)


class AssetPipelineTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_review_draws_confirmed_boxes_and_skips_text(self):
        source = self.root / "source.png"
        output = self.root / "review-numbered.png"
        Image.new("RGB", (100, 80), "white").save(source)
        manifest = {
            "canvas": {"width": 100, "height": 80},
            "assets": [
                {"id": "01", "type": "button", "bbox": [10, 10, 40, 20], "status": "confirmed"},
                {"id": "02", "type": "icon", "bbox": [50, 10, 40, 20], "status": "confirmed"},
            ],
            "texts": [{"id": "t01", "text": "开始", "bbox": [15, 15, 20, 10]}],
        }

        asset_pipeline.create_review(source, manifest, output)

        with Image.open(output) as review:
            self.assertEqual(review.size, (100, 80))
            self.assertNotEqual(review.getpixel((10, 10)), (255, 255, 255))

    def test_review_rejects_out_of_bounds_boxes(self):
        source = self.root / "source.png"
        output = self.root / "review-numbered.png"
        Image.new("RGB", (100, 80), "white").save(source)
        manifest = {
            "canvas": {"width": 100, "height": 80},
            "assets": [
                {"id": "bad", "type": "button", "bbox": [70, 10, 40, 20], "status": "confirmed"},
            ],
        }

        with self.assertRaisesRegex(ValueError, "bad.*exceeds source image bounds"):
            asset_pipeline.create_review(source, manifest, output)

    def test_split_uses_generated_sheet_and_makes_ui_transparent(self):
        sheet = self.root / "generated.png"
        image = Image.new("RGB", (20, 20), "#00ff00")
        for x in range(5, 15):
            for y in range(6, 14):
                image.putpixel((x, y), (255, 0, 0))
        image.save(sheet)
        output = self.root / "buttons" / "start-01.png"

        asset_pipeline.extract_generated_asset(
            sheet, [0, 0, 20, 20], output, (40, 20), transparent=True
        )

        result = Image.open(output)
        self.assertEqual(result.size, (40, 20))
        self.assertEqual(result.mode, "RGBA")
        self.assertEqual(result.getpixel((0, 0))[3], 0)
        self.assertGreater(max(pixel[3] for pixel in result.getdata()), 0)

    def test_split_accepts_key_color_tolerance_and_padding(self):
        sheet = self.root / "generated.png"
        image = Image.new("RGB", (20, 20), "#123456")
        for x in range(8, 12):
            for y in range(8, 12):
                image.putpixel((x, y), (240, 200, 10))
        image.save(sheet)
        output = self.root / "icons" / "coin-01.png"

        asset_pipeline.extract_generated_asset(
            sheet,
            [0, 0, 20, 20],
            output,
            (20, 20),
            transparent=True,
            key_color="#123456",
            tolerance=4,
            padding=2,
        )

        result = Image.open(output)
        self.assertEqual(result.mode, "RGBA")
        self.assertEqual(result.getpixel((0, 0))[3], 0)
        self.assertGreater(max(pixel[3] for pixel in result.getdata()), 0)

    def test_package_validates_files_and_excludes_source_images(self):
        task = self.root / "task"
        (task / "buttons").mkdir(parents=True)
        Image.new("RGBA", (30, 12), (255, 0, 0, 255)).save(
            task / "buttons" / "start-01.png"
        )
        Image.new("RGB", (100, 80), "blue").save(task / "source.png")
        (task / "generated-sheet.png").write_text("not packaged", encoding="utf-8")
        (task / "assets-draft.json").write_text("not packaged", encoding="utf-8")
        manifest = {
            "canvas": {"width": 100, "height": 80},
            "assets": [
                {
                    "id": "01",
                    "type": "button",
                    "name": "start",
                    "filename": "buttons/start-01.png",
                    "bbox": [10, 20, 30, 12],
                    "zIndex": 1,
                    "prompt": "red game start button without text",
                    "status": "generated",
                }
            ],
            "texts": [
                {
                    "id": "t01",
                    "text": "开始",
                    "bbox": [15, 22, 20, 8],
                    "align": "center",
                    "color": "#ffffff",
                    "role": "static",
                }
            ],
            "styleGuide": {"palette": ["#ff0000"], "materials": ["glossy"]},
        }

        asset_pipeline.package_task(task, manifest)

        layout = json.loads((task / "layout.json").read_text())
        style_guide = json.loads((task / "style-guide.json").read_text())
        self.assertEqual(layout["assets"][0]["width"], 30)
        self.assertEqual(style_guide["palette"], ["#ff0000"])
        with zipfile.ZipFile(task / "output.zip") as archive:
            names = archive.namelist()
        self.assertIn("buttons/start-01.png", names)
        self.assertIn("layout.json", names)
        self.assertIn("style-guide.json", names)
        self.assertNotIn("source.png", names)
        self.assertNotIn("generated-sheet.png", names)
        self.assertNotIn("assets-draft.json", names)
        self.assertFalse(any(name.startswith("tests/") for name in names))

    def test_package_skips_pending_and_rejected_assets(self):
        task = self.root / "task"
        (task / "buttons").mkdir(parents=True)
        Image.new("RGBA", (30, 12), (255, 0, 0, 255)).save(
            task / "buttons" / "start-01.png"
        )
        manifest = {
            "canvas": {"width": 100, "height": 80},
            "assets": [
                {
                    "id": "01",
                    "type": "button",
                    "filename": "buttons/start-01.png",
                    "bbox": [10, 20, 30, 12],
                    "zIndex": 1,
                    "prompt": "red game start button without text",
                    "status": "generated",
                },
                {
                    "id": "02",
                    "type": "icon",
                    "filename": "icons/missing-pending.png",
                    "bbox": [0, 0, 10, 10],
                    "zIndex": 2,
                    "prompt": "pending icon",
                    "status": "pending",
                },
                {
                    "id": "03",
                    "type": "icon",
                    "filename": "icons/missing-rejected.png",
                    "bbox": [0, 0, 10, 10],
                    "zIndex": 3,
                    "prompt": "rejected icon",
                    "status": "rejected",
                },
            ],
            "texts": [],
        }

        asset_pipeline.package_task(task, manifest)

        layout = json.loads((task / "layout.json").read_text())
        self.assertEqual([item["id"] for item in layout["assets"]], ["01"])
        with zipfile.ZipFile(task / "output.zip") as archive:
            names = archive.namelist()
        self.assertNotIn("icons/missing-pending.png", names)
        self.assertNotIn("icons/missing-rejected.png", names)

    def test_package_rejects_transparent_background(self):
        task = self.root / "task"
        (task / "background").mkdir(parents=True)
        Image.new("RGBA", (100, 80), (0, 0, 255, 120)).save(
            task / "background" / "main.png"
        )
        manifest = {
            "canvas": {"width": 100, "height": 80},
            "assets": [
                {
                    "id": "bg",
                    "type": "background",
                    "filename": "background/main.png",
                    "bbox": [0, 0, 100, 80],
                    "zIndex": 0,
                    "prompt": "opaque game lobby background",
                    "status": "generated",
                }
            ],
            "texts": [],
        }

        with self.assertRaisesRegex(ValueError, "background must be opaque"):
            asset_pipeline.package_task(task, manifest)

    def test_package_rejects_wrong_asset_dimensions(self):
        task = self.root / "task"
        (task / "icons").mkdir(parents=True)
        Image.new("RGBA", (9, 9), "red").save(task / "icons" / "coin-01.png")
        manifest = {
            "canvas": {"width": 100, "height": 80},
            "assets": [
                {
                    "id": "01",
                    "type": "icon",
                    "name": "coin",
                    "filename": "icons/coin-01.png",
                    "bbox": [0, 0, 10, 10],
                    "zIndex": 1,
                    "prompt": "gold coin icon",
                    "status": "generated",
                }
            ],
            "texts": [],
        }

        with self.assertRaisesRegex(ValueError, "expected 10x10"):
            asset_pipeline.package_task(task, manifest)


if __name__ == "__main__":
    unittest.main()
