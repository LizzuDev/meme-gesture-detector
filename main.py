"""
main.py
-------
Entry point for the Meme Gesture Detector.

Controls
--------
  Q or ESC → quit
  S        → save a screenshot to screenshots/

Cooldown logic
--------------
Once a gesture is recognised it stays on screen for COOLDOWN_SECONDS
even if the hand moves away, so the meme has time to be seen.
"""

import cv2
import time
import os

from camera          import Camera
from hand_tracker    import HandTracker
from gesture_detector import GestureDetector
from overlay         import OverlayRenderer


# ── Configuration ─────────────────────────────────────────────────────────────

CAMERA_SOURCE     = 0          # 0 = first webcam / DroidCam USB
                               # Change to 1 or 2 if DroidCam is on a different index
                               # Or use: "http://192.168.x.x:4747/video" for Wi-Fi

FRAME_WIDTH       = 640
FRAME_HEIGHT      = 480
COOLDOWN_SECONDS  = 1      # How long the meme stays visible after gesture ends
WINDOW_TITLE      = "Meme Gesture Detector  |  Q = quit"

SCREENSHOT_DIR    = "screenshots"


# ── Main loop ─────────────────────────────────────────────────────────────────

def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    camera   = Camera(CAMERA_SOURCE, FRAME_WIDTH, FRAME_HEIGHT)
    tracker  = HandTracker(max_hands=1, detection_conf=0.7, tracking_conf=0.7)
    detector = GestureDetector()
    renderer = OverlayRenderer(memes_dir="memes")

    # Cooldown state
    displayed_gesture = "NONE"
    last_trigger_time = 0.0

    print("[Main] Running — press Q or ESC to quit, S to screenshot.")

    while True:
        frame = camera.read()
        if frame is None:
            print("[Main] Frame read failed — check your camera source.")
            break

        # ── Hand tracking ──────────────────────────────────────────────────
        landmarks, annotated_frame = tracker.process(frame)

        # ── Gesture detection ──────────────────────────────────────────────
        raw_gesture = detector.detect(landmarks)

        now = time.time()

        if raw_gesture != "NONE":
            # Fresh gesture → start / extend the cooldown window
            displayed_gesture = raw_gesture
            last_trigger_time = now
        elif now - last_trigger_time > COOLDOWN_SECONDS:
            # Cooldown expired and no gesture → clear the meme
            displayed_gesture = "NONE"

        # ── Render ────────────────────────────────────────────────────────
        output = renderer.render(annotated_frame, displayed_gesture)

        # Optional: show FPS in top-left corner
        fps_text = f"FPS: {int(1 / max(time.time() - now, 1e-6))}"
        cv2.putText(output, fps_text, (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow(WINDOW_TITLE, output)

        # ── Key handling ───────────────────────────────────────────────────
        key = cv2.waitKey(1) & 0xFF

        if key in (ord('q'), ord('Q'), 27):   # Q or ESC
            break

        if key in (ord('s'), ord('S')):       # S → screenshot
            ts   = time.strftime("%Y%m%d_%H%M%S")
            path = os.path.join(SCREENSHOT_DIR, f"meme_{ts}.png")
            cv2.imwrite(path, output)
            print(f"[Main] Screenshot saved → {path}")

    # ── Cleanup ───────────────────────────────────────────────────────────────
    camera.release()
    tracker.close()
    cv2.destroyAllWindows()
    print("[Main] Closed.")


if __name__ == "__main__":
    main()
