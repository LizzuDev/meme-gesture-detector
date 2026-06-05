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
from tictactoe       import TicTacToeMode

# ── Configuration ─────────────────────────────────────────────────────────────

CAMERA_SOURCE     = 0          # 0 = first webcam / DroidCam USB
                               # Change to 1 or 2 if DroidCam is on a different index
                               # Or use: "http://192.168.x.x:4747/video" for Wi-Fi

FRAME_WIDTH       = 640
FRAME_HEIGHT      = 480
COOLDOWN_SECONDS  = 1      # How long the meme stays visible after gesture ends
WINDOW_TITLE      = "Detector de Memes  |  Q = Salir  |  M = Modo"

SCREENSHOT_DIR    = "screenshots"


# ── Main loop ─────────────────────────────────────────────────────────────────

def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    camera   = Camera(CAMERA_SOURCE, FRAME_WIDTH, FRAME_HEIGHT)
    tracker  = HandTracker(max_hands=2, detection_conf=0.7, tracking_conf=0.7)
    detector = GestureDetector()
    renderer = OverlayRenderer(memes_dir="memes")
    ttt_game = TicTacToeMode()

    # State
    mode = "MEMES"
    displayed_gesture = "NONE"
    last_trigger_time = 0.0

    print("[Principal] Ejecutando — presiona Q o ESC para salir, S para capturar, M para cambiar de modo.")

    while True:
        frame = camera.read()
        if frame is None:
            print("[Principal] Error al leer la camara — verifica el origen de tu video.")
            break

        # ── Hand tracking ──────────────────────────────────────────────────
        landmarks, annotated_frame = tracker.process(frame)

        now = time.time()
        
        if mode == "MEMES":
            # ── Gesture detection ──────────────────────────────────────────────
            raw_gesture = detector.detect(landmarks)

            if raw_gesture != "NONE":
                displayed_gesture = raw_gesture
                last_trigger_time = now
            elif now - last_trigger_time > COOLDOWN_SECONDS:
                displayed_gesture = "NONE"

            # ── Render ────────────────────────────────────────────────────────
            output = renderer.render(annotated_frame, displayed_gesture)
        else:
            output = ttt_game.process_and_render(annotated_frame, landmarks)

        # UI elements
        fps_text = f"FPS: {int(1 / max(time.time() - now, 1e-6))}"
        cv2.putText(output, fps_text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(output, "M = Cambiar Modo", (output.shape[1] - 220, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow(WINDOW_TITLE, output)

        # ── Key handling ───────────────────────────────────────────────────
        key = cv2.waitKey(1) & 0xFF

        if key in (ord('q'), ord('Q'), 27):   # Q or ESC
            break
            
        if key in (ord('m'), ord('M')):
            mode = "TICTACTOE" if mode == "MEMES" else "MEMES"
            if mode == "TICTACTOE":
                ttt_game.reset()
                print("[Principal] Cambiado a Modo 3 en Raya.")
            else:
                print("[Principal] Cambiado a Modo Memes.")

        if key in (ord('s'), ord('S')):       # S → screenshot
            ts   = time.strftime("%Y%m%d_%H%M%S")
            path = os.path.join(SCREENSHOT_DIR, f"meme_{ts}.png")
            cv2.imwrite(path, output)
            print(f"[Principal] Captura guardada → {path}")

    # ── Cleanup ───────────────────────────────────────────────────────────────
    camera.release()
    tracker.close()
    cv2.destroyAllWindows()
    print("[Principal] Cerrado.")


if __name__ == "__main__":
    main()
