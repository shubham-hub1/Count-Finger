# -------------------------------------------------------------
# finger_counter_simple.py
# Real‑time finger counting using MediaPipe Tasks API
# -------------------------------------------------------------
# Requirements (install via requirements.txt):
#   mediapipe>=0.10.0
#   opencv-python
#   numpy
# -------------------------------------------------------------

import os
import urllib.request
import cv2
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    RunningMode,
)

# ------------------------------------------------------------------
# 1️⃣ Resolve / download the hand‑landmarker model
# ------------------------------------------------------------------
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
MODEL_PATH = os.path.join(SCRIPT_DIR, "hand_landmarker.task")

if not os.path.exists(MODEL_PATH):
    print("🔎 Model not found – downloading (≈ 4 MB)…")
    url = (
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
        "hand_landmarker/float16/latest/hand_landmarker.task"
    )
    try:
        urllib.request.urlretrieve(url, MODEL_PATH)
        print("✅ Model downloaded to", MODEL_PATH)
    except Exception as e:
        raise RuntimeError(f"Failed to download MediaPipe model: {e}") from e

# ------------------------------------------------------------------
# 2️⃣ HandLandmarker configuration (single hand, image mode)
# ------------------------------------------------------------------
options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=RunningMode.IMAGE,
    num_hands=1,
    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.6,
    min_tracking_confidence=0.5,
)
landmarker = HandLandmarker.create_from_options(options)

# ------------------------------------------------------------------
# 3️⃣ Finger‑counting helper (0‑5)
# ------------------------------------------------------------------
THUMB_TIP, THUMB_IP = 4, 3
INDEX_TIP, INDEX_PIP = 8, 6
MIDDLE_TIP, MIDDLE_PIP = 12, 10
RING_TIP, RING_PIP = 16, 14
PINKY_TIP, PINKY_PIP = 20, 18
FINGER_TIPS = {THUMB_TIP, INDEX_TIP, MIDDLE_TIP, RING_TIP, PINKY_TIP}

def count_fingers(landmarks, handedness: str) -> int:
    """Return number of extended fingers (0‑5).

    * Thumb – compare x (direction depends on left/right hand).
    * Other fingers – tip y < pip y means the finger is up.
    """
    lm = landmarks
    # Thumb
    is_right = handedness == "Right"
    thumb_up = (lm[THUMB_TIP].x < lm[THUMB_IP].x) if is_right else (lm[THUMB_TIP].x > lm[THUMB_IP].x)
    # Other fingers
    fingers_up = [thumb_up]
    for tip, pip in [
        (INDEX_TIP, INDEX_PIP),
        (MIDDLE_TIP, MIDDLE_PIP),
        (RING_TIP, RING_PIP),
        (PINKY_TIP, PINKY_PIP),
    ]:
        fingers_up.append(lm[tip].y < lm[pip].y)
    return sum(fingers_up)

# ------------------------------------------------------------------
# 4️⃣ Drawing helpers
# ------------------------------------------------------------------
def draw_finger_count(img, count):
    h, w = img.shape[:2]
    txt = f"Fingers: {count}"
    overlay = img.copy()
    cv2.rectangle(overlay, (w // 2 - 120, h // 2 - 40), (w // 2 + 120, h // 2 + 10), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, img, 0.4, 0, img)
    cv2.putText(img, txt, (w // 2 - 110, h // 2 + 5), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3, cv2.LINE_AA)

# Hand‑connection pairs (same as legacy MediaPipe HAND_CONNECTIONS)
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),          # thumb
    (0, 5), (5, 6), (6, 7), (7, 8),          # index
    (0, 9), (9, 10), (10, 11), (11, 12),    # middle
    (0, 13), (13, 14), (14, 15), (15, 16),  # ring
    (0, 17), (17, 18), (18, 19), (19, 20),  # pinky
]

def draw_hand_skeleton(img, landmarks):
    h, w = img.shape[:2]
    pts = [(int(p.x * w), int(p.y * h)) for p in landmarks]
    for a, b in HAND_CONNECTIONS:
        cv2.line(img, pts[a], pts[b], (0, 255, 0), 2, cv2.LINE_AA)
    for i, (cx, cy) in enumerate(pts):
        radius = 6 if i in FINGER_TIPS else 3
        cv2.circle(img, (cx, cy), radius, (0, 255, 0), -1)

# ------------------------------------------------------------------
# 5️⃣ Main loop
# ------------------------------------------------------------------
def main():
    print("\n=== Finger Counter Demo ===")
    print("  Show any hand pose to your webcam.")
    print("  The number of extended fingers is printed in the console and overlaid on the video feed.")
    print("  Press Q or ESC to quit.\n")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("❌ Cannot open webcam – check that a camera is connected.")
    # Optional resolution tweak
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            # Mirror for a natural selfie view
            frame = cv2.flip(frame, 1)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result = landmarker.detect(mp_image)

            finger_cnt = 0
            if result.hand_landmarks and result.handedness:
                lm = result.hand_landmarks[0]
                hand_label = result.handedness[0][0].category_name  # "Left" or "Right"
                finger_cnt = count_fingers(lm, hand_label)
                draw_hand_skeleton(frame, lm)

            draw_finger_count(frame, finger_cnt)
            print(f"\rDetected fingers: {finger_cnt}", end="")
            cv2.imshow("Finger Counter – Q/ESC to quit", frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), 27):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        landmarker.close()
        print("\n\n🚪 Demo finished. Thanks for trying!\n")

if __name__ == "__main__":
    main()
