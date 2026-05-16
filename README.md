<div align="center">

# 🐹 Meme Gesture Detector

**Real-time hand gesture recognition that triggers meme reactions — running entirely on CPU**

![Python](https://img.shields.io/badge/Python-3.8--3.11-blue?style=flat-square&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green?style=flat-square&logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-red?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=flat-square&logo=windows)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

<br/>

> *Show a thumbs-up → hamster approves. Flash a peace sign → hamster vibes. No GPU needed.*

</div>

---

## What Is This?

A lightweight computer vision app that watches your hand through a webcam and shows a matching meme beside you — in real time.

Built as a beginner-friendly introduction to:
- Real-time video processing
- Hand landmark detection with MediaPipe
- Gesture classification logic
- Image overlay rendering

No neural network training. No GPU required. Just Python + a webcam.

---

## Gestures & Memes

| Gesture | Hand Shape | Meme |
|---------|-----------|------|
| 👍 Thumbs Up | Only thumb extended | Hamster giving thumbs up |
| ✌️ Peace | Index + middle fingers up | Hamster peace sign |
| 🖐️ Open Hand | All five fingers extended | Hamster waving |
| ✊ Fist | All fingers closed | Hamster fist |
| ☝️ Pointing | Only index finger up | Thinking monkey |

---

## Project Structure

```
meme_detector/
│
├── main.py               ← Entry point, main loop
├── camera.py             ← Webcam capture + mirror mode
├── hand_tracker.py       ← MediaPipe hand landmark detection
├── gesture_detector.py   ← Gesture classification logic
├── overlay.py            ← Meme image loading + side-by-side rendering
│
├── memes/
│   ├── hamster_thumbsup.png
│   ├── hamster_peace.png
│   ├── hamster_open.png
│   ├── hamster_fist.png
│   └── monkey_pointing.png
│
├── screenshots/          ← Auto-created when you press S
├── requirements.txt
└── README.md
```

---

## Requirements

- Python **3.8 – 3.11** (MediaPipe does not support 3.12+ on Windows yet)
- A webcam — built-in, or a phone via **DroidCam** / **Iriun Webcam**
- No GPU needed — runs on a mid-range CPU

---

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/meme-gesture-detector.git
cd meme-gesture-detector

# 2. Create a virtual environment
python -m venv venv
.\venv\Scripts\activate        # Windows PowerShell
# source venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your meme images to memes/
#    File names must match exactly as listed above

# 5. Run
python main.py
```

---

## Camera Options

| Setup | Setting in `main.py` |
|-------|----------------------|
| Default webcam | `CAMERA_SOURCE = 0` |
| DroidCam USB | `CAMERA_SOURCE = 1` or `2` |
| DroidCam Wi-Fi | `CAMERA_SOURCE = "http://192.168.x.x:4747/video"` |
| Iriun Webcam | `CAMERA_SOURCE = 0` or `1` |

---

## Controls

| Key | Action |
|-----|--------|
| `Q` or `ESC` | Quit |
| `S` | Save screenshot to `screenshots/` |

---

## How It Works

```
Webcam Feed
    ↓
OpenCV — captures and mirrors each frame
    ↓
MediaPipe Hands — detects 21 landmarks on your hand
    ↓
Gesture Detector — classifies finger positions into a gesture
    ↓
Overlay Renderer — picks the matching meme image
    ↓
Output Window — shows camera + meme side by side
```

The gesture classifier works by checking which fingers are extended using landmark Y-coordinates and distance calculations — no machine learning inference at runtime.

---

## Tips for Best Detection

- Make sure your hand is **well lit**
- Keep your hand **fully visible** in the frame
- Hold gestures **steady** for ~0.5 seconds
- Works best against a **plain background**

---

## Troubleshooting

**Camera won't open**
→ Try changing `CAMERA_SOURCE` to `1` or `2` in `main.py`

**Gestures not detecting correctly**
→ Check your lighting and make sure your full hand is in frame

**MediaPipe install fails**
→ Confirm you are using Python 3.8–3.11, not 3.12+

---

## Future Ideas

- [ ] Multiple hand support
- [ ] Sound effects per gesture
- [ ] Animated GIF memes
- [ ] Gesture score / combo system
- [ ] Pose matching with memes
- [ ] AR-style effects (aura, filters)

---

## Tech Stack

| Library | Purpose |
|---------|---------|
| [OpenCV](https://opencv.org/) | Video capture, frame rendering, overlays |
| [MediaPipe](https://mediapipe.dev/) | Real-time hand landmark tracking |
| [NumPy](https://numpy.org/) | Array and frame operations |

---

## License

free to use, modify, and share.

---

<div align="center">
Made with 🐹 and way too much free time
</div>
