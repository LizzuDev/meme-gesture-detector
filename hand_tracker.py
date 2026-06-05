"""
hand_tracker.py
---------------
Wraps MediaPipe Hands to detect one hand and return its 21 landmarks.
"""

import mediapipe as mp
import cv2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

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
        base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_conf,
            min_hand_presence_confidence=tracking_conf,
            min_tracking_confidence=tracking_conf,
            running_mode=vision.RunningMode.IMAGE
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

    def process(self, frame_bgr):
        """
        Run hand detection on a BGR frame.
        Returns (landmarks_list, annotated_frame).

        landmarks_list : list of 21 (x, y, z) tuples in normalised coords,
                         or None if no hand found.
        """
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        results = self.detector.detect(mp_image)

        annotated = frame_bgr.copy()
        landmarks = None

        if results.hand_landmarks:
            landmarks = []
            h, w, _ = frame_bgr.shape
            
            for hand_lm in results.hand_landmarks:
                pts = [(int(lm.x * w), int(lm.y * h)) for lm in hand_lm]
                
                # Draw connections
                connections = vision.HandLandmarksConnections.HAND_CONNECTIONS
                for connection in connections:
                    start_idx = connection.start
                    end_idx = connection.end
                    cv2.line(annotated, pts[start_idx], pts[end_idx], (0, 255, 0), 2)
                
                # Draw points
                for pt in pts:
                    cv2.circle(annotated, pt, 4, (0, 0, 255), -1)

                landmarks.append([
                    (lm.x * w, lm.y * h, lm.z)
                    for lm in hand_lm
                ])

        return landmarks, annotated

    def close(self):
        self.detector.close()
