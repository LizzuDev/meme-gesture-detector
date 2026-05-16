"""
hand_tracker.py
---------------
Wraps MediaPipe Hands to detect one hand and return its 21 landmarks.
"""

import mediapipe as mp
import cv2


class HandTracker:
    # MediaPipe landmark indices
    WRIST        = 0
    THUMB_TIP    = 4
    THUMB_IP     = 3
    THUMB_MCP    = 2
    INDEX_TIP    = 8
    INDEX_PIP    = 6
    MIDDLE_TIP   = 12
    MIDDLE_PIP   = 10
    RING_TIP     = 16
    RING_PIP     = 14
    PINKY_TIP    = 20
    PINKY_PIP    = 18
    INDEX_MCP    = 5
    MIDDLE_MCP   = 9
    RING_MCP     = 13
    PINKY_MCP    = 17
    
    def __init__(self, max_hands=1, detection_conf=0.7, tracking_conf=0.7):
        self._mp_hands  = mp.solutions.hands
        self._mp_draw   = mp.solutions.drawing_utils
        self._mp_styles = mp.solutions.drawing_styles

        self.hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_conf,
            min_tracking_confidence=tracking_conf,
        )

    def process(self, frame_bgr):
        """
        Run hand detection on a BGR frame.
        Returns (landmarks_list, annotated_frame).

        landmarks_list : list of 21 (x, y, z) tuples in normalised coords,
                         or None if no hand found.
        """
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        annotated = frame_bgr.copy()
        landmarks = None

        if results.multi_hand_landmarks:
            hand_lm = results.multi_hand_landmarks[0]   # first hand only

            # Draw skeleton
            self._mp_draw.draw_landmarks(
                annotated,
                hand_lm,
                self._mp_hands.HAND_CONNECTIONS,
                self._mp_styles.get_default_hand_landmarks_style(),
                self._mp_styles.get_default_hand_connections_style(),
            )

            h, w, _ = frame_bgr.shape
            landmarks = [
                (lm.x * w, lm.y * h, lm.z)
                for lm in hand_lm.landmark
            ]

        return landmarks, annotated

    def close(self):
        self.hands.close()
