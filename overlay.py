"""
overlay.py
----------
Loads meme images from /memes/ and composites them beside the camera frame.

Layout (side-by-side)
---------------------
┌─────────────────────┬─────────────────┐
│   Camera feed       │   Meme image    │
│   (640 × 480)       │   (320 × 480)   │
└─────────────────────┴─────────────────┘
Total window: 960 × 480

The meme panel shows:
  • A black background when no gesture is detected
  • The matching meme image when a gesture is held
  • A label at the bottom naming the gesture
"""

import os
import cv2
import numpy as np


# ── Meme filenames — adjust if your actual file names differ ──────────────────
GESTURE_TO_FILE = {
    "THUMBS_UP":  "hamster_thumbsup.jpg",
    "PEACE":      "hamster_peace.jpg",
    "OPEN_HAND":  "hamster_open.jpg",
    "FIST":       "hamster_fist.jpg",
    "POINTING":   "monkey_pointing.jpeg",
}

GESTURE_LABELS = {
    "THUMBS_UP": "Thumbs Up",
    "PEACE":     "Peace Sign",
    "OPEN_HAND": "Open Hand ",
    "FIST":      "Fist",
    "POINTING":  "Thinking...",
    "NONE":      "",
}

MEME_PANEL_W = 320
FONT          = cv2.FONT_HERSHEY_DUPLEX
FONT_SCALE    = 0.8
FONT_COLOR    = (255, 255, 255)
FONT_THICK    = 2
LABEL_BG      = (30, 30, 30)


class OverlayRenderer:
    def __init__(self, memes_dir: str = "memes"):
        self.memes: dict[str, np.ndarray | None] = {}
        self._load_memes(memes_dir)

    # ── Private ───────────────────────────────────────────────────────────────

    def _load_memes(self, memes_dir: str):
        """Load every meme image once at startup (supports transparency)."""
        for gesture, filename in GESTURE_TO_FILE.items():
            path = os.path.join(memes_dir, filename)
            if os.path.exists(path):
                # Load with alpha channel so PNGs with transparency work
                img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                self.memes[gesture] = img
                print(f"[Overlay] Loaded: {filename}")
            else:
                self.memes[gesture] = None
                print(f"[Overlay] WARNING: {path} not found — will show placeholder")

    def _resize_to_panel(self, img: np.ndarray, panel_h: int) -> np.ndarray:
        """Resize image to fit the meme panel, keeping aspect ratio."""
        h, w = img.shape[:2]
        scale = min(MEME_PANEL_W / w, panel_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    def _alpha_composite(self, bg: np.ndarray, fg: np.ndarray, y_off: int, x_off: int):
        """Paste fg (BGRA) onto bg (BGR) at (x_off, y_off) using alpha blending."""
        if fg.shape[2] == 4:
            alpha = fg[:, :, 3] / 255.0
            for c in range(3):
                bg[y_off:y_off+fg.shape[0], x_off:x_off+fg.shape[1], c] = (
                    alpha * fg[:, :, c] + (1 - alpha) * bg[y_off:y_off+fg.shape[0], x_off:x_off+fg.shape[1], c]
                )
        else:
            bg[y_off:y_off+fg.shape[0], x_off:x_off+fg.shape[1]] = fg[:, :, :3]

    def _build_meme_panel(self, gesture: str, panel_h: int) -> np.ndarray:
        """Return a (panel_h × MEME_PANEL_W × 3) BGR panel."""
        panel = np.zeros((panel_h, MEME_PANEL_W, 3), dtype=np.uint8)

        img = self.memes.get(gesture)

        if img is not None:
            resized = self._resize_to_panel(img, panel_h - 40)   # leave space for label
            rh, rw = resized.shape[:2]
            y_off = (panel_h - 40 - rh) // 2
            x_off = (MEME_PANEL_W - rw) // 2
            self._alpha_composite(panel, resized, y_off, x_off)
        else:
            # Placeholder text when image file is missing
            cv2.putText(panel, "Image not found", (10, panel_h // 2),
                        FONT, 0.5, (80, 80, 80), 1)

        # Label bar at the bottom
        label = GESTURE_LABELS.get(gesture, "")
        if label:
            bar_y = panel_h - 36
            cv2.rectangle(panel, (0, bar_y), (MEME_PANEL_W, panel_h), LABEL_BG, -1)
            text_size = cv2.getTextSize(label, FONT, FONT_SCALE, FONT_THICK)[0]
            tx = (MEME_PANEL_W - text_size[0]) // 2
            cv2.putText(panel, label, (tx, panel_h - 10),
                        FONT, FONT_SCALE, FONT_COLOR, FONT_THICK)

        return panel

    # ── Public ────────────────────────────────────────────────────────────────

    def render(self, camera_frame: np.ndarray, gesture: str) -> np.ndarray:
        """
        Returns the final side-by-side frame:
            [camera_frame | meme_panel]
        """
        panel_h = camera_frame.shape[0]
        meme_panel = self._build_meme_panel(gesture, panel_h)
        return np.hstack([camera_frame, meme_panel])
