# Finger Counter – MediaPipe Tasks API

## Overview
A lightweight **real‑time finger‑counting** demo written in pure Python. It uses **MediaPipe's HandLandmarker (Tasks API)** to detect a hand from your webcam and counts the number of extended fingers (0‑5). The result is shown both on the video feed and printed to the console.

---

## Features
- **Automatic model download** – the required `hand_landmarker.task` file (≈ 4 MB) is fetched the first time you run the script.
- **No deprecated APIs** – fully compatible with MediaPipe ≥ 0.10.
- **Simple hand‑skeleton overlay** and a clear finger‑count label.
- Works on Windows, macOS, and Linux (Python 3.8+).

---

## Demo
*(Run the script to see the webcam window with the finger count overlay. Press **Q** or **Esc** to exit.)*

---

## Installation
```bash
# Clone the repository (or copy the RockPaperScissors folder)
git clone https://github.com/yourusername/finger-counter.git
cd finger-counter/RockPaperScissors

# OPTIONAL: create a virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt
```

> **Note**: `requirements.txt` already contains `mediapipe>=0.10.0`, `opencv-python`, and `numpy`.

---

## Usage
```bash
python finger_counter_simple.py
```
The script will:
1. Check for `hand_landmarker.task` in the same directory. If missing, it downloads it automatically.
2. Open your webcam, detect a single hand, count extended fingers, and overlay the count.
3. Print the count to the console in real time.
4. Exit when you press **Q** or **Esc**.

---

## How the counting works
- **Thumb** – compared via the x‑coordinate (handedness aware).
- **Other fingers** – tip y‑coordinate must be above the PIP joint (lower y value → finger extended).
- The sum of the five boolean checks gives the finger count (0‑5).

---

## Troubleshooting
| Issue | Fix |
|------|------|
| **Model not found** | The script automatically downloads it. If the download fails, ensure you have internet access and run the script again. |
| **Webcam does not open** | Make sure no other application is using the camera. Test with `python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"` (should print `True`). |
| **`AttributeError: module 'mediapipe' has no attribute 'solutions'`** | This script uses the **Tasks API** only; the error occurs only if you try to run an older script that still imports `mediapipe.solutions`. Use this file instead. |
| **Performance is slow** | Reduce the capture resolution by removing or lowering the `cap.set` calls, or run on a GPU‑enabled environment. |

---

## License
MIT – feel free to modify, redistribute, and use it in your own projects.

---

*Enjoy counting your fingers!*
