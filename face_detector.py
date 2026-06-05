"""
Detector de Rostros y Expresiones
---------------------------------
Este módulo se especializa en "leer tu cara". Utiliza los modelos avanzados de 
MediaPipe para medir la tensión de tus músculos faciales (los 'blendshapes'). 
Gracias a esto, puede distinguir matemáticamente entre una sonrisa genuina, 
una cara de asombro o un simple movimiento de la boca al hablar.
"""
import math

class FaceDetector:
    def __init__(self):
        self._debugged = False

    def detect(self, landmarks_list, blendshapes):
        if not landmarks_list:
            return "NONE"

        if blendshapes and not self._debugged:
            print(f"[FaceDetector] Blendshapes detectados, usando alta precisión.")
            self._debugged = True

        # Primero intentamos con blendshapes (si el modelo los soporta)
        if blendshapes:
            face = detect_from_blendshapes(blendshapes)
            if face != "NONE":
                return face

        # Fallback: intentar detectar con distancias manuales
        return detect_from_landmarks(landmarks_list)


def detect_from_blendshapes(blendshapes):
    """Detecta expresiones faciales utilizando los blendshapes de MediaPipe."""
    blink_left = blendshapes.get("eyeBlinkLeft", 0)
    blink_right = blendshapes.get("eyeBlinkRight", 0)
    
    if blink_left > 0.45 and blink_right < 0.15:
        return "WINKING"
    if blink_right > 0.45 and blink_left < 0.15:
        return "WINKING"

    smile = blendshapes.get("mouthSmileLeft", 0) > 0.35 and blendshapes.get("mouthSmileRight", 0) > 0.35
    if smile:
        return "HAPPY"

    if blendshapes.get("jawOpen", 0) > 0.2:
        if blendshapes.get("browInnerUp", 0) > 0.2:
            return "SURPRISED"
        else:
            return "TONGUE_OUT"

    if blendshapes.get("browDownLeft", 0) > 0.4 and blendshapes.get("browDownRight", 0) > 0.4:
        return "ANGRY"

    return "NONE"


def detect_from_landmarks(landmarks_list):
    """Detecta expresiones faciales calculando proporciones entre los puntos clave del rostro."""
    face = landmarks_list[0]

    LEFT_EYE_IDX = [33, 133, 159, 145]
    RIGHT_EYE_IDX = [362, 263, 386, 374]

    def dist(a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def eye_ratio(eye_indices):
        left, right, bottom, top = [face[i] for i in eye_indices]
        eye_w = dist(left, right)
        eye_h = dist(top, bottom)
        return eye_h / max(eye_w, 1e-6)

    left_ear = eye_ratio(LEFT_EYE_IDX)
    right_ear = eye_ratio(RIGHT_EYE_IDX)
    if abs(left_ear - right_ear) > 0.08 and min(left_ear, right_ear) < 0.15:
        return "WINKING"

    mouth_l = face[61]
    mouth_r = face[291]
    mouth_top = face[13]
    mouth_bot = face[14]
    mouth_w = dist(mouth_l, mouth_r)
    mouth_h = dist(mouth_top, mouth_bot)
    mar = mouth_h / max(mouth_w, 1e-6)

    avg_corner_y = (face[61][1] + face[291][1]) / 2
    center_top_y = face[13][1]
    face_height = dist(face[10], face[152])
    
    smile_ratio = (center_top_y - avg_corner_y) / max(face_height, 1e-6)
    
    if smile_ratio > 0.015:
        return "HAPPY"

    if mar > 0.35:
        brow_y = face[105][1]
        eye_y = face[159][1]
        face_height = dist(face[10], face[152])
        if (eye_y - brow_y) / face_height > 0.11:
            return "SURPRISED"
        return "TONGUE_OUT"

    left_brow = face[105]
    right_brow = face[285]
    left_eye_top = face[145]
    right_eye_top = face[374]
    brow_to_eye = (dist(left_brow, left_eye_top) + dist(right_brow, right_eye_top)) / 2
    eye_w_avg = (dist(face[33], face[133]) + dist(face[362], face[263])) / 2
    if brow_to_eye < eye_w_avg * 0.45:
        return "ANGRY"

    return "NONE"
