"""
gesture_detector.py
-------------------
Converts 21 MediaPipe hand landmarks into one of 5 named gestures.

Gestures
--------
THUMBS_UP   → hamster raising thumb
PEACE       → hamster peace sign (V / victory)
OPEN_HAND   → hamster open hand / wave
FIST        → hamster closed fist
POINTING    → thinking monkey (index finger up, rest closed)
NONE        → no recognisable gesture
"""

from hand_tracker import HandTracker as HT


def _finger_up(landmarks, tip_idx, pip_idx, mcp_idx):
    tip = landmarks[tip_idx]
    pip = landmarks[pip_idx]
    mcp = landmarks[mcp_idx]
    
    
    dy = pip[1] - tip[1]
    dx = abs(pip[0] - mcp[0])
    return dy > 0.02 * landmarks[0][1] or dx < 15


def _thumb_up(landmarks):
    if landmarks is None:
        return False
    
    thumb_tip = landmarks[HT.THUMB_TIP]
    thumb_mcp = landmarks[HT.THUMB_MCP]
    thumb_ip  = landmarks[HT.THUMB_IP]   
    
   
    dy = thumb_mcp[1] - thumb_tip[1]
    index_mcp = landmarks[HT.INDEX_MCP]
    dx = abs(thumb_tip[0] - index_mcp[0])
    
    return dy > 25 and dx > 20



# Gesture classifier
# ──────────────────────────────────────────────

class GestureDetector:
    GESTURES = ("THUMBS_UP", "PEACE", "OPEN_HAND", "FIST", "POINTING", "NONE")

    def detect(self, landmarks) -> str:
        """
        landmarks : list of 21 (x, y, z) tuples (pixel coords).
        Returns one of the strings in GESTURES.
        """
        if landmarks is None:
            return "NONE"

        # Which fingers are extended?
        thumb  = _thumb_up(landmarks)
        index  = _finger_up(landmarks, HT.INDEX_TIP,  HT.INDEX_PIP, HT.INDEX_MCP)   # أضفنا MCP
        middle = _finger_up(landmarks, HT.MIDDLE_TIP, HT.MIDDLE_PIP, HT.MIDDLE_MCP)
        ring   = _finger_up(landmarks, HT.RING_TIP,   HT.RING_PIP,   HT.RING_MCP)
        pinky  = _finger_up(landmarks, HT.PINKY_TIP,  HT.PINKY_PIP,  HT.PINKY_MCP)

        fingers = (thumb, index, middle, ring, pinky)

        
        #only thumb up, all four fingers closed
        if thumb and not index and not middle and not ring and not pinky:
            return "THUMBS_UP"
        
        #index + middle up, others closed
        if index and middle and not thumb and not ring and not pinky:
            return "PEACE"

        #all five extended
        if all(fingers):
            return "OPEN_HAND"

        #all five closed
        if not any(fingers):
            return "FIST"

        #only index up, rest closed (including thumb)
        if index and not thumb and not middle and not ring and not pinky:
            return "POINTING"

        return "NONE"
