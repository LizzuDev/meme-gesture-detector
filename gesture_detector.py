"""
gesture_detector.py
-------------------
Converts 21 MediaPipe hand landmarks into one of named gestures.
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
    
    dist_tip = math.hypot(tip[0] - wrist[0], tip[1] - wrist[1])
    dist_pip = math.hypot(pip[0] - wrist[0], pip[1] - wrist[1])
    
    return dist_tip > dist_pip

def _thumb_up(landmarks):
    if landmarks is None: return False
    hs = _hand_size(landmarks)
    is_up = landmarks[HT.THUMB_TIP][1] < landmarks[HT.THUMB_IP][1] - (hs * 0.1)
    # Ensure thumb is extended (not folded across palm)
    dist = math.hypot(landmarks[HT.THUMB_TIP][0] - landmarks[HT.INDEX_MCP][0],
                      landmarks[HT.THUMB_TIP][1] - landmarks[HT.INDEX_MCP][1])
    return is_up and (dist > hs * 0.5)

def _thumb_down(landmarks):
    if landmarks is None: return False
    hs = _hand_size(landmarks)
    # Tip must be lower than IP
    is_down = landmarks[HT.THUMB_TIP][1] > landmarks[HT.THUMB_IP][1] + (hs * 0.1)
    # Ensure thumb is extended (not folded across palm)
    dist = math.hypot(landmarks[HT.THUMB_TIP][0] - landmarks[HT.INDEX_MCP][0],
                      landmarks[HT.THUMB_TIP][1] - landmarks[HT.INDEX_MCP][1])
    return is_down and (dist > hs * 0.5)

def _is_korean_heart(landmarks):
    if landmarks is None: return False
    hs = _hand_size(landmarks)
    t_tip = landmarks[HT.THUMB_TIP]
    i_tip = landmarks[HT.INDEX_TIP]
    dist = math.hypot(t_tip[0] - i_tip[0], t_tip[1] - i_tip[1])
    
    index_up = _finger_up(landmarks, HT.INDEX_TIP, HT.INDEX_PIP)
    middle = _finger_up(landmarks, HT.MIDDLE_TIP, HT.MIDDLE_PIP)
    ring   = _finger_up(landmarks, HT.RING_TIP,   HT.RING_PIP)
    pinky  = _finger_up(landmarks, HT.PINKY_TIP,  HT.PINKY_PIP)
    
    return dist < (hs * 0.7) and index_up and not middle and not ring and not pinky

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
    
    return index_dist < (hs * 1.0) and thumb_dist < (hs * 1.0) and not (m1_up and m2_up)

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

# Gesture classifier
# ──────────────────────────────────────────────

class GestureDetector:
    GESTURES = ("THUMBS_UP", "PEACE", "OPEN_HAND", "FIST", "POINTING", "PENGUIN_FLOWERS", "DOG_HEART", "SHY_FINGERS", "CALL_ME", "THUMBS_DOWN", "GLASSES", "ITALIAN", "SHH", "NONE")

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

        # For single hand gestures, process the first hand
        landmarks = hands_landmarks[0]

        if _is_korean_heart(landmarks): return "PENGUIN_FLOWERS"
        if _is_italian(landmarks): return "ITALIAN"

        # Which fingers are extended?
        thumb  = _thumb_up(landmarks)
        thumb_down = _thumb_down(landmarks)
        index  = _finger_up(landmarks, HT.INDEX_TIP,  HT.INDEX_PIP)
        middle = _finger_up(landmarks, HT.MIDDLE_TIP, HT.MIDDLE_PIP)
        ring   = _finger_up(landmarks, HT.RING_TIP,   HT.RING_PIP)
        pinky  = _finger_up(landmarks, HT.PINKY_TIP,  HT.PINKY_PIP)

        fingers = (thumb, index, middle, ring, pinky)

        if thumb and not index and not middle and not ring and not pinky:
            return "THUMBS_UP"
            
        if thumb_down and not index and not middle and not ring and not pinky:
            return "THUMBS_DOWN"
            
        if thumb and pinky and not index and not middle and not ring:
            return "CALL_ME"
        
        #index + middle up, others closed
        if index and middle and not ring and not pinky:
            return "PEACE"

        #all five extended
        if all(fingers):
            return "OPEN_HAND"

        #all five closed
        if not any(fingers):
            return "FIST"

        #only index up, rest closed
        if index and not middle and not ring and not pinky:
            # Check if index is pointing UP (SHH) or SIDEWAYS/FORWARD (POINTING)
            i_tip = landmarks[HT.INDEX_TIP]
            i_pip = landmarks[HT.INDEX_PIP]
            dx = abs(i_tip[0] - i_pip[0])
            dy = abs(i_tip[1] - i_pip[1])
            
            if dy > dx * 1.5:  # pointing strictly vertical
                return "SHH"
            else:
                return "POINTING"

        return "NONE"
