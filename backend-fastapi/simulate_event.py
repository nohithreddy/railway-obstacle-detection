import random
import time

import requests


OBJECTS = [
    ("plastic_bag", 0.2, 0.2),
    ("person", 0.6, 1.7),
    ("motorcycle", 1.0, 1.4),
    ("truck", 2.5, 3.5),
    ("fallen_tree", 8.0, 1.2),
]


while True:
    obj, width, height = random.choice(OBJECTS)
    payload = {
        "object_type": obj,
        "confidence": round(random.uniform(0.75, 0.98), 2),
        "distance_m": round(random.uniform(25, 300), 1),
        "relative_velocity_mps": 0,
        "width_m": width,
        "height_m": height,
        "track_position": "center",
    }
    print(requests.post("http://localhost:8000/api/v1/detections", json=payload, timeout=5).json())
    time.sleep(2)
