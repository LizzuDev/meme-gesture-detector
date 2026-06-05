"""
overlay.py
----------
Loads meme images from /memes/ and composites them beside the camera frame.
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

GESTURE_TO_FILE = {
    "THUMBS_UP":  "hamster_thumbsup.jpg",
    "PEACE":      "hamster_peace.jpg",
    "OPEN_HAND":  "hamster_open.jpg",
    "FIST":       "hamster_fist.jpg",
    "POINTING":   "monkey_pointing.jpeg",
    "PENGUIN_FLOWERS": "penguin-flowers.jpg",
    "DOG_HEART":  "dog-heart.jpg",
    "SHY_FINGERS": "cat-fingers-touching.jpg",
    "CALL_ME":    "cat-phone-signal.jpg",
    "THUMBS_DOWN": "sad-hamster.jpg",
    "GLASSES":    "cat-glasses.jpg",
    "ITALIAN":    "cat-doubt.jpg",
    "SHH":        "cat-shh.jpg",
}

GESTURE_LABELS = {
    "THUMBS_UP": "10/10",
    "PEACE":     "Todo chill",
    "OPEN_HAND": "POV: te lamo la mano",
    "FIST":      "Buscando pleito",
    "POINTING":  "Quedaste funado",
    "PENGUIN_FLOWERS": "Awwwww",
    "DOG_HEART": "Awwwww",
    "SHY_FINGERS": "Yo literal",
    "CALL_ME":    "Desbloquéame porfa",
    "THUMBS_DOWN": "No era necesario...",
    "GLASSES":    "De hecho",
    "ITALIAN":    "Literalmente quedé",
    "SHH":        "Shhhh",
    "NONE":      "",
}

MEME_PANEL_W = 420

class OverlayRenderer:
    def __init__(self, memes_dir: str = "memes"):
        self.memes = {}
        self._load_memes(memes_dir)
        
        # Load a fun/bold font, fallback to standard
        try:
            self.font = ImageFont.truetype("C:\\Windows\\Fonts\\segoeuib.ttf", 22)
            self.font_small = ImageFont.truetype("C:\\Windows\\Fonts\\segoeui.ttf", 16)
        except IOError:
            try:
                self.font = ImageFont.truetype("arialbd.ttf", 22)
                self.font_small = ImageFont.truetype("arial.ttf", 16)
            except IOError:
                self.font = ImageFont.load_default()
                self.font_small = ImageFont.load_default()
                
        self._bg_cache = {}

    def _load_memes(self, memes_dir: str):
        for gesture, filename in GESTURE_TO_FILE.items():
            path = os.path.join(memes_dir, filename)
            if os.path.exists(path):
                try:
                    img = Image.open(path).convert("RGBA")
                    self.memes[gesture] = img
                    print(f"[Overlay] Cargado: {filename}")
                except Exception as e:
                    print(f"[Overlay] Error cargando {filename}: {e}")
                    self.memes[gesture] = None
            else:
                self.memes[gesture] = None

    def _get_rounded_image(self, img, radius):
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0) + img.size, radius, fill=255)
        result = img.copy()
        result.putalpha(mask)
        return result

    def _get_gradient_bg(self, width, height):
        """Generate a solid black background."""
        key = (width, height)
        if key in self._bg_cache:
            return self._bg_cache[key].copy()
            
        base = Image.new('RGBA', (width, height), (0,0,0,255))
        self._bg_cache[key] = base
        return base.copy()

    def render(self, camera_frame: np.ndarray, gesture: str) -> np.ndarray:
        h, w, c = camera_frame.shape
        
        # Base vibrant background
        panel = self._get_gradient_bg(MEME_PANEL_W, h)
        
        img = self.memes.get(gesture)
        label = GESTURE_LABELS.get(gesture, "")
        
        if img is not None:
            # Resize image maintaining aspect ratio
            target_w = MEME_PANEL_W - 80
            target_h = h - 200
            
            img_ratio = img.width / img.height
            target_ratio = target_w / target_h
            
            if img_ratio > target_ratio:
                new_w = target_w
                new_h = int(new_w / img_ratio)
            else:
                new_h = target_h
                new_w = int(new_h * img_ratio)
                
            resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Just the image with rounded corners
            rounded = self._get_rounded_image(resized, 15)
            
            x_off = (MEME_PANEL_W - new_w) // 2
            y_off = (h - new_h) // 2 - 40
            
            # Drop shadow
            shadow = Image.new("RGBA", panel.size, (0,0,0,0))
            shadow_draw = ImageDraw.Draw(shadow)
            shadow_draw.rounded_rectangle(
                [x_off+5, y_off+10, x_off+new_w+5, y_off+new_h+10], 
                15, fill=(0, 0, 0, 100)
            )
            shadow = shadow.filter(ImageFilter.GaussianBlur(10))
            panel.alpha_composite(shadow)
            
            # Paste image directly
            panel.alpha_composite(rounded, dest=(x_off, y_off))
            
        elif gesture != "NONE":
            # Elegant missing placeholder
            draw = ImageDraw.Draw(panel)
            text = "Buscando meme..."
            bbox = draw.textbbox((0, 0), text, font=self.font_small)
            tx = (MEME_PANEL_W - (bbox[2] - bbox[0])) // 2
            draw.text((tx, h // 2), text, font=self.font_small, fill=(255, 255, 255, 200))
            
        # Fun highly-legible label
        if label:
            draw = ImageDraw.Draw(panel, "RGBA")
            bbox = draw.textbbox((0, 0), label, font=self.font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            
            box_w = min(text_w + 50, MEME_PANEL_W - 40)
            box_h = text_h + 40
            
            bx = (MEME_PANEL_W - box_w) // 2
            by = h - box_h - 40
            
            # Solid white rectangle with slightly rounded edges (radius=8)
            shadow_bg = Image.new("RGBA", panel.size, (0,0,0,0))
            ImageDraw.Draw(shadow_bg).rounded_rectangle(
                [bx, by+5, bx + box_w, by + box_h+5],
                radius=8, fill=(0, 0, 0, 80)
            )
            shadow_bg = shadow_bg.filter(ImageFilter.GaussianBlur(8))
            panel.alpha_composite(shadow_bg)
            
            draw.rounded_rectangle(
                [bx, by, bx + box_w, by + box_h],
                radius=8, fill=(255, 255, 255, 255)
            )
            
            # Dark text for contrast
            tx = bx + (box_w - text_w) // 2
            ty = by + (box_h - text_h) // 2 - 4
            draw.text((tx, ty), label, font=self.font, fill=(30, 30, 40, 255))
        
        # Convert panel to numpy array for cv2
        panel_cv2 = cv2.cvtColor(np.array(panel.convert("RGB")), cv2.COLOR_RGB2BGR)
        
        return np.hstack([camera_frame, panel_cv2])


