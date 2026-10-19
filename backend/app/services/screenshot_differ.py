"""
WebMender AI — Screenshot Differ
Pixel-level and perceptual comparison of before/after screenshots.
"""

import base64
import io
import asyncio
from PIL import Image, ImageChops
import numpy as np


class ScreenshotDiffer:
    """
    Compares two base64-encoded PNG screenshots and returns a diff score.

    Score: 0.0 = identical, 1.0 = completely different
    Uses a combination of:
      - Pixel-level absolute diff (fast)
      - Structural region analysis (identifies where changes occurred)
    """

    def _decode(self, b64: str) -> Image.Image:
        raw = base64.b64decode(b64)
        return Image.open(io.BytesIO(raw)).convert("RGB")

    async def compare(self, before_b64: str, after_b64: str) -> float:
        """Compute normalised diff score between two screenshots."""
        return await asyncio.get_event_loop().run_in_executor(
            None, self._sync_compare, before_b64, after_b64
        )

    def _sync_compare(self, before_b64: str, after_b64: str) -> float:
        try:
            before = self._decode(before_b64)
            after = self._decode(after_b64)

            # Resize to common size if needed
            if before.size != after.size:
                after = after.resize(before.size, Image.LANCZOS)

            diff = ImageChops.difference(before, after)
            arr = np.array(diff, dtype=np.float32)

            # Normalise: max possible diff per pixel is 255*3
            score = float(arr.mean()) / (255.0 * 3.0)
            return round(min(score * 10, 1.0), 4)   # amplify small changes
        except Exception:
            return 0.5  # conservative fallback

    def highlight_regions(self, before_b64: str, after_b64: str) -> str:
        """
        Generate a highlighted diff image (base64 PNG) marking changed regions.
        Red overlay = changed pixels.
        """
        try:
            before = self._decode(before_b64)
            after = self._decode(after_b64)
            if before.size != after.size:
                after = after.resize(before.size, Image.LANCZOS)

            diff = ImageChops.difference(before, after)
            arr = np.array(diff)
            mask = (arr.sum(axis=2) > 30).astype(np.uint8) * 255

            highlight = np.array(after.copy())
            highlight[mask > 0] = [255, 80, 80]   # red overlay

            result = Image.fromarray(highlight.astype(np.uint8))
            buf = io.BytesIO()
            result.save(buf, format="PNG")
            return base64.b64encode(buf.getvalue()).decode("utf-8")
        except Exception:
            return ""
