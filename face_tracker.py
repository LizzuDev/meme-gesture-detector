"""
face_tracker.py
---------------
Wraps MediaPipe Face Landmarker to detect faces and extract blendshapes.
"""

import mediapipe as mp
import cv2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class FaceTracker:
    def __init__(self, max_faces=1, detection_conf=0.7, tracking_conf=0.7):
        base_options = python.BaseOptions(model_asset_path='face_landmarker.task')
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            num_faces=max_faces,
            min_face_detection_confidence=detection_conf,
            min_face_presence_confidence=tracking_conf,
            min_tracking_confidence=tracking_conf,
            output_face_blendshapes=True,
            running_mode=vision.RunningMode.IMAGE
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)

    def process(self, frame_bgr):
        """
        Run face detection on a BGR frame.
        Returns (landmarks_list, blendshapes_dict, annotated_frame).
        """
        annotated = frame_bgr.copy()
        landmarks = None
        blendshapes = None

        try:
            rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            results = self.detector.detect(mp_image)
        except Exception as e:
            print(f"[FaceTracker] Error detectando rostro: {e}")
            return landmarks, blendshapes, annotated

        if results.face_landmarks:
            landmarks = []
            h, w, _ = frame_bgr.shape

            # Face contour key indices
            FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
                         397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
                         172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109, 10]
            LEFT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246, 33]
            RIGHT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398, 362]
            MOUTH = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409, 270, 269, 267, 0, 61]
            NOSE_BRIDGE = [168, 6, 197, 195, 5]
            LEFT_EYEBROW = [46, 53, 52, 65, 55]
            RIGHT_EYEBROW = [285, 295, 282, 283, 276]
            
            for face_lm in results.face_landmarks:
                pts = [(int(lm.x * w), int(lm.y * h)) for lm in face_lm]
                
                # Draw face contour (thicker lines for visibility)
                oval_pts = [pts[i] for i in FACE_OVAL]
                for i in range(len(oval_pts) - 1):
                    cv2.line(annotated, oval_pts[i], oval_pts[i+1], (255, 200, 100), 2)
                
                # Draw eyes
                eye_pts = [pts[i] for i in LEFT_EYE]
                for i in range(len(eye_pts) - 1):
                    cv2.line(annotated, eye_pts[i], eye_pts[i+1], (100, 255, 100), 2)
                eye_pts = [pts[i] for i in RIGHT_EYE]
                for i in range(len(eye_pts) - 1):
                    cv2.line(annotated, eye_pts[i], eye_pts[i+1], (100, 255, 100), 2)
                
                # Draw mouth
                mouth_pts = [pts[i] for i in MOUTH]
                for i in range(len(mouth_pts) - 1):
                    cv2.line(annotated, mouth_pts[i], mouth_pts[i+1], (100, 100, 255), 2)
                
                # Draw eyebrows
                brow_pts = [pts[i] for i in LEFT_EYEBROW]
                for i in range(len(brow_pts) - 1):
                    cv2.line(annotated, brow_pts[i], brow_pts[i+1], (200, 100, 200), 2)
                brow_pts = [pts[i] for i in RIGHT_EYEBROW]
                for i in range(len(brow_pts) - 1):
                    cv2.line(annotated, brow_pts[i], brow_pts[i+1], (200, 100, 200), 2)
                
                # Draw nose bridge
                cv2.line(annotated, pts[168], pts[6], (255, 255, 100), 2)
                
                # Print expression on frame if face detected
                cv2.putText(annotated, "Rostro detectado", (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 100), 2)

                landmarks.append([
                    (lm.x * w, lm.y * h, lm.z)
                    for lm in face_lm
                ])
                
        if results.face_blendshapes and len(results.face_blendshapes) > 0:
            blendshapes = {b.category_name: b.score for b in results.face_blendshapes[0]}

        return landmarks, blendshapes, annotated

    def close(self):
        self.detector.close()
