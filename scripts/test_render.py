import io
import sys
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
import render


class RendererTests(unittest.TestCase):
    def make_image(self, background=(255, 255, 255, 255), transparent=False):
        image = Image.new("RGBA", (96, 96), background)
        draw = ImageDraw.Draw(image)
        if transparent:
            image = Image.new("RGBA", (96, 96), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
        draw.ellipse((18, 18, 78, 78), fill=(125, 220, 40, 255))
        draw.ellipse((30, 28, 43, 43), fill=(255, 255, 255, 255))
        draw.ellipse((53, 28, 66, 43), fill=(255, 255, 255, 255))
        draw.ellipse((35, 33, 40, 41), fill=(10, 10, 10, 255))
        draw.ellipse((56, 33, 61, 41), fill=(10, 10, 10, 255))
        draw.polygon((42, 63, 48, 54, 54, 63, 48, 72), fill=(5, 5, 5, 255))
        return image

    def test_light_background_is_suppressed_but_light_eyes_remain(self):
        art = render._cell_rows(self.make_image())
        chars = "".join(char for row in art for char, _ in row)
        self.assertLess(chars.count(" "), len(chars) * 0.7)
        self.assertIn("@", chars)

    def test_transparent_image_keeps_silhouette(self):
        art = render._cell_rows(self.make_image(transparent=True))
        self.assertTrue(any(char != " " for row in art for char, _ in row))

    def test_dark_portrait_preserves_dark_pixels(self):
        image = Image.new("RGBA", (96, 96), (12, 12, 12, 255))
        ImageDraw.Draw(image).ellipse((24, 24, 72, 72), fill=(35, 190, 45, 255))
        art = render._cell_rows(image)
        colors = {color for row in art for char, color in row if char != " "}
        self.assertIn("#0c0c0c", colors)

    def test_high_contrast_features_and_svg_colors(self):
        art = render._cell_rows(self.make_image())
        svg = render.svg("dark", art, {"avatar_url": "x"}, {"repos": 1, "followers": 2, "stars": 3, "contributions": 4})
        self.assertIn("<tspan fill=", svg)
        self.assertGreater(svg.count('fill="#'), 20)
        self.assertIn("@media (prefers-reduced-motion:reduce)", svg)
        self.assertEqual(svg.count("<text x=\"34\""), render.PORTRAIT_ROWS)


if __name__ == "__main__":
    unittest.main()
