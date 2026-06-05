"""
gesture_detector.py
-------------------
Converts 21 MediaPipe hand landmarks into one of named gestures.
"""

"""
Clasificador de Gestos Manuales
-------------------------------
Aquí es donde ocurre la magia geométrica de las manos. Este archivo contiene
reglas específicas (distancias y ángulos entre tus nudillos y puntas de los dedos)
para decidir si estás haciendo un corazón coreano, señalando como una pistola, 
o levantando las dos manos para activar al mapache Pedro.
"""
import math
from hand_tracker import HandTracker as HT

def _hand_size(landmarks):
    if not landmarks: return 1.0
    w = landmarks[HT.WRIST]
    m = landmarks[HT.MIDDLE_MCP]
    return max(math.hypot(m[0] - w[0], m[1] - w[1]), 1.0)

def _finger_up(landmarks, tip_idx, pip_idx):
    wrist = landmarks[HT.WRIST]
    tip = landmarks[tip_idx]
    pip = landmarks[pip_idx]
    mcp = landmarks[pip_idx - 1] # En MediaPipe, el MCP siempre es PIP-1
    
    dist_tip = math.hypot(tip[0] - wrist[0], tip[1] - wrist[1])
    dist_pip = math.hypot(pip[0] - wrist[0], pip[1] - wrist[1])
    dist_mcp = math.hypot(mcp[0] - wrist[0], mcp[1] - wrist[1])
    
    # El dedo está levantado si su punta está más lejos de la muñeca que sus articulaciones
    return dist_tip > dist_pip + 5 and dist_tip > dist_mcp + 5

def _thumb_extended(landmarks):
    if landmarks is None: return False
    hs = _hand_size(landmarks)
    # Pulgar extendido: está lo suficientemente lejos del nudillo del índice
    # Esto evita que un pulgar pegado cuente como abierto
    dist = math.hypot(landmarks[HT.THUMB_TIP][0] - landmarks[HT.INDEX_MCP][0],
                      landmarks[HT.THUMB_TIP][1] - landmarks[HT.INDEX_MCP][1])
    return dist > hs * 0.55

def _thumb_up(landmarks):
    if landmarks is None: return False
    hs = _hand_size(landmarks)
    # Pulgar apuntando estrictamente hacia arriba (Y de la punta mucho menor que Y del nudillo)
    is_up = landmarks[HT.THUMB_TIP][1] < landmarks[HT.THUMB_IP][1] - (hs * 0.05)
    dist = math.hypot(landmarks[HT.THUMB_TIP][0] - landmarks[HT.INDEX_MCP][0],
                      landmarks[HT.THUMB_TIP][1] - landmarks[HT.INDEX_MCP][1])
    return is_up and (dist > hs * 0.5)

def _thumb_down(landmarks):
    if landmarks is None: return False
    hs = _hand_size(landmarks)
    # Pulgar apuntando hacia abajo (Y mayor que IP)
    is_down = landmarks[HT.THUMB_TIP][1] > landmarks[HT.THUMB_IP][1] + (hs * 0.05)
    dist = math.hypot(landmarks[HT.THUMB_TIP][0] - landmarks[HT.INDEX_MCP][0],
                      landmarks[HT.THUMB_TIP][1] - landmarks[HT.INDEX_MCP][1])
    return is_down and (dist > hs * 0.5)

def _is_korean_heart(landmarks):
    if landmarks is None: return False
    hs = _hand_size(landmarks)
    t_tip = landmarks[HT.THUMB_TIP]
    i_tip = landmarks[HT.INDEX_TIP]
    dist = math.hypot(t_tip[0] - i_tip[0], t_tip[1] - i_tip[1])
    
    # En un corazón coreano, el índice está flexionado, por lo que no usamos _finger_up estricto.
    # Solo revisamos que los otros tres dedos estén cerrados y el pulgar/índice estén cerca.
    middle = _finger_up(landmarks, HT.MIDDLE_TIP, HT.MIDDLE_PIP)
    ring   = _finger_up(landmarks, HT.RING_TIP,   HT.RING_PIP)
    pinky  = _finger_up(landmarks, HT.PINKY_TIP,  HT.PINKY_PIP)
    
    return dist < (hs * 0.8) and not middle and not ring and not pinky

def _is_two_hand_heart(hand1, hand2):
    hs = _hand_size(hand1)
    i1 = hand1[HT.INDEX_TIP]
    i2 = hand2[HT.INDEX_TIP]
    t1 = hand1[HT.THUMB_TIP]
    t2 = hand2[HT.THUMB_TIP]
    
    index_dist = math.hypot(i1[0] - i2[0], i1[1] - i2[1])
    thumb_dist = math.hypot(t1[0] - t2[0], t1[1] - t2[1])
    
    m1_up = _finger_up(hand1, HT.MIDDLE_TIP, HT.MIDDLE_PIP)
    m2_up = _finger_up(hand2, HT.MIDDLE_TIP, HT.MIDDLE_PIP)
    
    return index_dist < (hs * 1.5) and thumb_dist < (hs * 1.5) and not (m1_up and m2_up)

def _is_shy_fingers(hand1, hand2):
    hs = _hand_size(hand1)
    i1 = hand1[HT.INDEX_TIP]
    i2 = hand2[HT.INDEX_TIP]
    t1 = hand1[HT.THUMB_TIP]
    t2 = hand2[HT.THUMB_TIP]
    
    index_dist = math.hypot(i1[0] - i2[0], i1[1] - i2[1])
    thumb_dist = math.hypot(t1[0] - t2[0], t1[1] - t2[1])
    
    return index_dist < (hs * 1.0) and thumb_dist > (hs * 1.8)

def _is_ok_sign(landmarks):
    hs = _hand_size(landmarks)
    t_tip = landmarks[HT.THUMB_TIP]
    i_tip = landmarks[HT.INDEX_TIP]
    dist = math.hypot(t_tip[0] - i_tip[0], t_tip[1] - i_tip[1])
    
    middle = _finger_up(landmarks, HT.MIDDLE_TIP, HT.MIDDLE_PIP)
    ring   = _finger_up(landmarks, HT.RING_TIP,   HT.RING_PIP)
    pinky  = _finger_up(landmarks, HT.PINKY_TIP,  HT.PINKY_PIP)
    
    return dist < (hs * 0.7) and middle and ring and pinky

def _is_italian(landmarks):
    hs = _hand_size(landmarks)
    t_tip = landmarks[HT.THUMB_TIP]
    i_tip = landmarks[HT.INDEX_TIP]
    m_tip = landmarks[HT.MIDDLE_TIP]
    
    d1 = math.hypot(t_tip[0] - i_tip[0], t_tip[1] - i_tip[1])
    d2 = math.hypot(t_tip[0] - m_tip[0], t_tip[1] - m_tip[1])
    d3 = math.hypot(i_tip[0] - m_tip[0], i_tip[1] - m_tip[1])
    
    index_up = _finger_up(landmarks, HT.INDEX_TIP, HT.INDEX_PIP)
    middle_up = _finger_up(landmarks, HT.MIDDLE_TIP, HT.MIDDLE_PIP)
    ring   = _finger_up(landmarks, HT.RING_TIP,   HT.RING_PIP)
    pinky  = _finger_up(landmarks, HT.PINKY_TIP,  HT.PINKY_PIP)
    
    return d1 < (hs * 0.8) and d2 < (hs * 0.8) and d3 < (hs * 0.8) and index_up and middle_up and not ring and not pinky

def _is_open_hand(landmarks):
    if landmarks is None: return False
    thumb_ext = _thumb_extended(landmarks)
    index  = _finger_up(landmarks, HT.INDEX_TIP,  HT.INDEX_PIP)
    middle = _finger_up(landmarks, HT.MIDDLE_TIP, HT.MIDDLE_PIP)
    ring   = _finger_up(landmarks, HT.RING_TIP,   HT.RING_PIP)
    pinky  = _finger_up(landmarks, HT.PINKY_TIP,  HT.PINKY_PIP)
    return thumb_ext and index and middle and ring and pinky

# Gesture classifier
# ──────────────────────────────────────────────

class GestureDetector:
    GESTURES = ("THUMBS_UP", "PEACE", "OPEN_HAND", "WAVING", "FIST", "PENGUIN_FLOWERS", "DOG_HEART", "SHY_FINGERS", "CALL_ME", "THUMBS_DOWN", "GLASSES", "ITALIAN", "GUN", "PEDRO_RACCOON", "NONE")

    def detect(self, hands_landmarks) -> str:
        """
        hands_landmarks : list of hands, where each hand is a list of 21 (x, y, z) tuples (pixel coords).
        Returns one of the strings in GESTURES.
        """
        if not hands_landmarks:
            return "NONE"

        # Check for two hands gesture
        if len(hands_landmarks) == 2:
            if _is_two_hand_heart(hands_landmarks[0], hands_landmarks[1]):
                return "DOG_HEART"
            if _is_shy_fingers(hands_landmarks[0], hands_landmarks[1]):
                return "SHY_FINGERS"
            if _is_ok_sign(hands_landmarks[0]) and _is_ok_sign(hands_landmarks[1]):
                return "GLASSES"
            if _is_open_hand(hands_landmarks[0]) and _is_open_hand(hands_landmarks[1]):
                return "PEDRO_RACCOON"

        # For single hand gestures, process the first hand
        landmarks = hands_landmarks[0]

        if _is_korean_heart(landmarks): return "PENGUIN_FLOWERS"
        if _is_italian(landmarks): return "ITALIAN"

        # Which fingers are extended?
        thumb_ext = _thumb_extended(landmarks)
        thumb_is_up = _thumb_up(landmarks)
        thumb_is_down = _thumb_down(landmarks)
        index  = _finger_up(landmarks, HT.INDEX_TIP,  HT.INDEX_PIP)
        middle = _finger_up(landmarks, HT.MIDDLE_TIP, HT.MIDDLE_PIP)
        ring   = _finger_up(landmarks, HT.RING_TIP,   HT.RING_PIP)
        pinky  = _finger_up(landmarks, HT.PINKY_TIP,  HT.PINKY_PIP)

        fingers = (thumb_ext, index, middle, ring, pinky)

        if index and not middle and not ring and not pinky:
            return "GUN"

        if index and middle and ring and pinky and thumb_ext:
            wrist = landmarks[HT.WRIST]
            mcp = landmarks[HT.MIDDLE_MCP]
            angle = math.degrees(math.atan2(mcp[1] - wrist[1], mcp[0] - wrist[0]))
            is_tilted = abs(angle + 90) > 15
            if is_tilted:
                return "WAVING"
            return "OPEN_HAND"

        if thumb_is_up and not index and not middle and not ring and not pinky:
            return "THUMBS_UP"
            
        if thumb_is_down and not index and not middle and not ring and not pinky:
            return "THUMBS_DOWN"
            
        if thumb_ext and pinky and not index and not middle and not ring:
            return "CALL_ME"
        
        if index and middle and not ring and not pinky:
            return "PEACE"

        if all(fingers):
            return "OPEN_HAND"

        if not any(fingers):
            return "FIST"

        return "NONE"
