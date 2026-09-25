# Physical Prototype Build Plan — Starter Tier

Turns the simulator into a tabletop demo you can point a camera at: a small motorized cart on a track, a real ultrasonic sensor for distance, a real relay that cuts motor power on `AUTO_BRAKE`, and the existing dashboard/portal showing it happen live. Budget target: ₹15,000–25,000.

## Bill of Materials

Sourced from Indian robotics distributors (Robu.in is an official Raspberry Pi reseller; Robokits and Probots are standard hobbyist suppliers). Prices found while writing this plan — check current pricing before ordering, they drift.

| Item | Purpose | Price (₹) | Where |
|---|---|---|---|
| Raspberry Pi 5, 4GB | Runs `backend-fastapi` + `edge/capture_loop.py` at the edge | ~6,000 | [Robu.in](https://robu.in/product/raspberry-pi-5-model-4gb/) |
| Official 27W USB-C PD power supply | Pi 5 needs this exact spec, not a phone charger | ~900–1,200 | [Robu.in](https://robu.in/product/official-27w-usb-c-pd-power-supply-for-raspberry-pi-5-black/) |
| microSD card, 32GB, Class 10 | OS + model weights | ~500–800 | [Amazon.in](https://www.amazon.in/SanDisk-Ultra-microSD-UHS-I-120MB/dp/B08L5HMJVW) |
| Raspberry Pi Camera Module 3 | Feeds YOLOv8 detection | ~3,300–3,900 | [Robu.in](https://robu.in/product/raspberry-pi-camera-module-3/) |
| HC-SR04 ultrasonic sensor | Distance reading (`read_distance_m()`) | ~55–105 | [Robokits](https://robokits.co.in/sensors/ultrasonic-sensor/hc-sr04-ultrasonic-sensor-distance-measuring-module) / [Robu.in](https://robu.in/product/hc-sr04-ultrasonic-range-finder/) |
| 2-channel 5V relay module | Cuts motor power on `AUTO_BRAKE` | ~90–150 | [Robu.in](https://robu.in/product/5v-2-channel-relay-module/) |
| 2WD acrylic chassis kit — 2× TT gear motor, wheels, caster, 4×AA holder | Stands in for "the train" | ~380–600 | [Probots](https://probots.co.in/2wd-clear-acrylic-smart-robot-chassis-car-kit.html) |
| Breadboard + 140pcs jumper wire kit | Wiring the sensor and relay to GPIO | ~110–310 | [Robu.in](https://robu.in/product/mb102-830-points-solderless-prototype-breadboard-power-supply-module-140-jumper-wires-arduino-diy-starter-kit/) |
| Assorted resistor kit | Only 2 values actually used — 1kΩ + 2kΩ for the ECHO voltage divider — but a kit is cheaper than a specialty order and covers future tweaks | ~440 | [Robu.in](https://robu.in/product/assorted-resistor-kit-250-pcs/) |
| Toy figures / blocks of varying size | Obstacles for small/medium/large risk tiers | ~200–500 | local stationery/toy shop |
| Laptop or second Pi | Runs `spring-control-service` as the "control room" | already owned | — |
| Monitor/tablet | Runs `frontend-dashboard` as the driver display | already owned | — |

**Running total: ~₹11,900–14,300** — under the ₹15,000–25,000 tier target, leaving headroom for shipping and a spare part or two (a second HC-SR04 and a few extra jumper wires are worth having; both fail more often than anything else on this list).

Cost levers if you want to go lower or higher:
- Swap the Camera Module 3 (~₹3,600) for a ~₹500–800 USB webcam — cuts the single biggest line item, at the cost of a slightly fiddlier mount and a USB port instead of the Pi's dedicated CSI connector.
- A Raspberry Pi 4 4GB instead of the 5 saves roughly ₹1,500–2,000 but runs YOLOv8n inference meaningfully slower — fine for the test protocol below, worth knowing before you commit to real-time thresholds later.

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

On-device setup (the Pi only):

```bash
cd backend-fastapi
bash edge/setup_pi.sh   # venv, requirements + RPi.GPIO, .env, pre-caches YOLO weights
# edit .env: set BRAKE_RELAY_GPIO_PIN=17 and anything else that needs to change
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
python edge/capture_loop.py
```

For anything past a one-off bench test, install the two systemd units in [edge/systemd/](../backend-fastapi/edge/systemd/) instead of running both by hand — they restart on crash and start on boot, so the rig comes back up after a power cycle without an SSH session:

```bash
sudo cp edge/systemd/*.service /etc/systemd/system/
sudo systemctl enable --now railway-backend railway-edge-capture
```

(Edit the `User=` and path fields in those two files first if your device user or clone path isn't `pi` / `/home/pi/railway-obstacle-detection`.)

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
