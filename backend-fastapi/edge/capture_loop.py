"""Edge capture loop for the starter-tier physical prototype (Raspberry Pi).

Reads a live camera feed, runs YOLOv8 detection, reads an HC-SR04 ultrasonic
distance sensor, and posts each detection to the FastAPI backend as a
SensorReading. Not part of the FastAPI app package — run directly on the
edge device:

    python edge/capture_loop.py

See docs/prototype-build-plan.md for wiring and env var defaults.
"""

import math
import os
import time
from datetime import datetime

import cv2
import requests
from dotenv import load_dotenv
from ultralytics import YOLO

load_dotenv()  # reads backend-fastapi/.env if present; harmless no-op otherwise

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000/api/v1/detections")
TRAIN_ID = os.environ.get("TRAIN_ID", "TRAIN-001")
TRAIN_SPEED_MPS = float(os.environ.get("TRAIN_SPEED_MPS", "1.0"))
MODEL_WEIGHTS = os.environ.get("MODEL_WEIGHTS", "yolov8n.pt")
CAMERA_INDEX = int(os.environ.get("CAMERA_INDEX", "0"))
CAMERA_HFOV_DEG = float(os.environ.get("CAMERA_HFOV_DEG", "62.0"))
POLL_INTERVAL_S = float(os.environ.get("POLL_INTERVAL_S", "0.2"))

TRIG_PIN = int(os.environ.get("ULTRASONIC_TRIG_PIN", "23"))
ECHO_PIN = int(os.environ.get("ULTRASONIC_ECHO_PIN", "24"))

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None


def setup_ultrasonic() -> None:
    if GPIO is None:
        print("RPi.GPIO not available — using a fixed 5.0m test distance.")
        return
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)
    GPIO.output(TRIG_PIN, False)
    time.sleep(0.5)


def read_distance_m() -> float:
    """HC-SR04 pulse-echo distance reading; a fixed value off-hardware keeps the loop runnable for dev."""
    if GPIO is None:
        return 5.0

    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    timeout = time.time() + 0.04
    pulse_start = pulse_end = time.time()
    while GPIO.input(ECHO_PIN) == 0 and pulse_start < timeout:
        pulse_start = time.time()
    while GPIO.input(ECHO_PIN) == 1 and pulse_end < timeout:
        pulse_end = time.time()

    duration = pulse_end - pulse_start
    return round((duration * 343.0) / 2, 2)


def bbox_size_m(bbox_px: tuple, frame_width_px: int, distance_m: float) -> tuple:
    """Approximate real-world width/height from a pixel bbox, distance, and camera horizontal FOV."""
    x1, y1, x2, y2 = bbox_px
    meters_per_px = (2 * distance_m * math.tan(math.radians(CAMERA_HFOV_DEG / 2))) / frame_width_px
    return round((x2 - x1) * meters_per_px, 2), round((y2 - y1) * meters_per_px, 2)


def run() -> None:
    setup_ultrasonic()
    model = YOLO(MODEL_WEIGHTS)
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera index {CAMERA_INDEX}")

    print(f"Edge capture loop running. Posting to {BACKEND_URL}")
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                continue

            distance = read_distance_m()
            results = model.predict(frame, verbose=False)[0]

            for box in results.boxes:
                object_type = results.names[int(box.cls[0])]
                confidence = round(float(box.conf[0]), 2)
                width_m, height_m = bbox_size_m(tuple(box.xyxy[0].tolist()), frame.shape[1], distance)

                reading = {
                    "train_id": TRAIN_ID,
                    "train_speed_mps": TRAIN_SPEED_MPS,
                    "object_type": object_type,
                    "confidence": confidence,
                    "distance_m": distance,
                    "relative_velocity_mps": 0.0,
                    "width_m": max(width_m, 0.01),
                    "height_m": max(height_m, 0.01),
                    "track_position": "center",
                }
                try:
                    requests.post(BACKEND_URL, json=reading, timeout=2.0)
                except requests.RequestException as exc:
                    print(f"[{datetime.utcnow().isoformat()}] failed to post detection: {exc}")

            time.sleep(POLL_INTERVAL_S)
    finally:
        cap.release()
        if GPIO is not None:
            GPIO.cleanup()


if __name__ == "__main__":
    run()
