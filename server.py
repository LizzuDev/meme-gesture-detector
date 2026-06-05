"""
Servidor Central de IA (Backend)
--------------------------------
Este archivo es el corazón de la aplicación. Actúa como un puente en tiempo real:
recibe los fotogramas de tu cámara web que envía el navegador, los analiza usando 
nuestros detectores de IA (para buscar manos y caras), y luego responde al instante
con el gesto detectado para que la página pueda mostrar el meme correcto.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import base64
import json
import time

from hand_tracker import HandTracker
from gesture_detector import GestureDetector
from face_tracker import FaceTracker
from face_detector import FaceDetector
from tictactoe import TicTacToeMode
from overlay import GESTURE_LABELS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared AI instances
tracker = HandTracker(max_hands=2, detection_conf=0.7, tracking_conf=0.7)
face_tracker = FaceTracker()
detector = GestureDetector()
face_detector = FaceDetector()
ttt_game = TicTacToeMode()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected via WebSocket")
    
    displayed_gesture = "NONE"
    last_trigger_time = 0.0
    COOLDOWN_SECONDS = 1.0

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            
            mode = msg.get("mode", "MEMES")
            img_b64 = msg.get("image", "")
            width = msg.get("width", 640)
            height = msg.get("height", 480)
            
            if img_b64.startswith("data:image"):
                img_b64 = img_b64.split(",")[1]
                
            img_bytes = base64.b64decode(img_b64)
            np_arr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            if frame is None:
                await websocket.send_json({"error": "Invalid frame"})
                continue

            # Process frame
            landmarks, _ = tracker.process(frame)
            face_landmarks, face_blendshapes, _ = face_tracker.process(frame)
            
            lms_json = []
            if landmarks:
                for hand in landmarks:
                    hand_json = [{"x": lm[0]/width, "y": lm[1]/height, "z": lm[2]} for lm in hand]
                    lms_json.append(hand_json)

            now = time.time()
            raw_gesture = detector.detect(landmarks) if landmarks else "NONE"
            
            response = {"mode": mode, "landmarks": lms_json, "gesture": raw_gesture}
            
            if mode == "MEMES":
                raw_face = face_detector.detect(face_landmarks, face_blendshapes)
                
                if raw_gesture != "NONE":
                    displayed_gesture = raw_gesture
                    last_trigger_time = now
                elif raw_face != "NONE":
                    displayed_gesture = raw_face
                    last_trigger_time = now
                elif now - last_trigger_time > COOLDOWN_SECONDS:
                    displayed_gesture = "NONE"
                    
                response["gesture"] = displayed_gesture
                response["label"] = GESTURE_LABELS.get(displayed_gesture, "")
            elif mode == "TICTACTOE":
                displayed_gesture = "NONE"
                ttt_state = ttt_game.process(landmarks, width, height)
                response["tictactoe"] = ttt_state
            
            await websocket.send_json(response)
            
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import uvicorn
    print("Starting server on ws://localhost:8000")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

