# Physical Prototype Build Plan — Starter Tier

Turns the simulator into a tabletop demo you can point a camera at: a small motorized cart on a track, a real ultrasonic sensor for distance, a real relay that cuts motor power on `AUTO_BRAKE`, and the existing dashboard/portal showing it happen live. Budget target: ₹15,000–25,000.

## Bill of Materials

| Item | Purpose | Approx. price (₹) |
|---|---|---|
| Raspberry Pi 4 (4GB) or Pi 5, + power supply, SD card (32GB) | Runs `backend-fastapi` + `edge/capture_loop.py` at the edge | 6,000–8,500 |
| Raspberry Pi Camera Module 3 (or USB webcam) | Feeds YOLOv8 detection | 1,500–2,500 |
| HC-SR04 ultrasonic sensor | Distance reading (`read_distance_m()`) | 100–150 |
| 2-channel relay module | Cuts motor power on `AUTO_BRAKE` | 150–250 |
| Small DC gear-motor cart or toy train (9–12V) + track/guide rail | Stands in for "the train" | 800–2,000 |
| Breadboard + jumper wires + resistors | Wiring the sensor and relay to GPIO | 300–500 |
| Toy figures / blocks of varying size | Obstacles for small/medium/large risk tiers | 200–500 |
| Laptop or second Pi | Runs `spring-control-service` as the "control room" | already owned |
| Monitor/tablet | Runs `frontend-dashboard` as the driver display | already owned |

Everything above already has a home in the codebase — this tier deliberately swaps in the cheapest sensor (ultrasonic, one distance value) that still exercises the full pipeline in [decision_engine.py](../backend-fastapi/app/decision_engine.py), rather than a full 2D LiDAR scan.

## Wiring

HC-SR04 → Raspberry Pi GPIO (BCM numbering, matches `edge/capture_loop.py` defaults):

| HC-SR04 pin | Pi GPIO | Note |
|---|---|---|
| VCC | 5V | |
| GND | GND | |
| TRIG | GPIO23 | `ULTRASONIC_TRIG_PIN` |
| ECHO | GPIO24 (via voltage divider, 5V→3.3V) | `ULTRASONIC_ECHO_PIN` — the Pi's GPIO is not 5V tolerant, use a resistor divider or logic-level shifter here |

Relay board → Raspberry Pi GPIO:

| Relay pin | Pi GPIO | Note |
|---|---|---|
| VCC / GND | 5V / GND | |
| IN | GPIO17 | set `BRAKE_RELAY_GPIO_PIN=17` |
| COM / NO | in series with the cart motor's power lead | wired so the relay is **normally closed** for motor power, and opens (cuts power) when the pin goes HIGH on `AUTO_BRAKE` |

Wire the relay so a Pi crash or power loss fails to the brake-applied state (normally-open motor circuit), not the other way round — the same fail-safe assumption a real interlocking system makes.

## Software integration

The app was already architected for this; nothing in the decision loop changes, only where the inputs come from and where the brake output goes.

1. **Camera + distance → detection.** [edge/capture_loop.py](../backend-fastapi/edge/capture_loop.py) runs YOLOv8n on each frame, reads the HC-SR04 for distance, estimates bbox width/height in meters from distance + camera FOV, and `POST`s a `SensorReading` to `/api/v1/detections` — the same schema the simulator already used.
2. **Decision engine.** Unchanged — [decision_engine.py](../backend-fastapi/app/decision_engine.py) classifies risk and picks an action exactly as it does today.
3. **Real brake.** [braking.py](../backend-fastapi/app/braking.py) now drives a real GPIO pin when `BRAKE_RELAY_GPIO_PIN` is set; unset (e.g. on your dev laptop), it behaves exactly as before — no environment-specific code path risk to the existing tests.
4. **Dashboard + portal.** `frontend-dashboard` and `spring-control-service` run unchanged, pointed at the Pi's IP address instead of `localhost`.

On-device setup (the Pi only — do **not** add these to `requirements.txt`, they don't install off-Pi):

```bash
pip install RPi.GPIO
cd backend-fastapi && pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BRAKE_RELAY_GPIO_PIN=17 python edge/capture_loop.py
```

## Test protocol

Mirrors the "Field Simulation" section of [testing-plan.md](testing-plan.md), scaled to the tabletop:

1. Calibrate: place an object at a known distance (tape measure), compare against `read_distance_m()` output; adjust for HC-SR04 tolerance (~±1cm at this range).
2. Run the cart at a fixed speed, place a small object (block) on the track — confirm `WARN_DRIVER` fires, cart doesn't stop.
3. Place a medium object (toy figure) — confirm `REQUEST_DRIVER_DECISION` fires and shows on the dashboard, cart keeps moving until a driver response is sent.
4. Place a large object (stack of blocks, area ≥ 6m² scaled to the cart's own size) — confirm `AUTO_BRAKE` fires, relay trips, motor cuts, and the event shows in the control portal's audit log.
5. Record video of steps 2–4 — this is the demo artifact for a portfolio or interview, and the measured distances/latencies are what turns the report's TODO accuracy numbers into real ones.

## Safety notes

- Keep motor voltage low (9–12V DC) and current within the relay's rating — this is a tabletop demo, not a load-bearing system.
- Double-check the ECHO pin voltage divider before first power-on; 5V straight into a Pi GPIO pin can damage the board.
- This plan stays entirely in scope of the project's own [safety note](../README.md#safety-note): a demonstration rig, not a certified control system. Phase 04 of [project-outlook.md](project-outlook.md) is what real certification would require.
