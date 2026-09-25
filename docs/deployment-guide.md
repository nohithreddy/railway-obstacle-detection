# Deployment Guide

## Edge Device

1. Install Ubuntu 22.04 (or Raspberry Pi OS) on Jetson Orin or Raspberry Pi.
2. Connect LiDAR/ultrasonic, camera, GPS, IMU, and modem.
3. On a Raspberry Pi, run `bash backend-fastapi/edge/setup_pi.sh` — creates the venv, installs `requirements.txt` plus the device-only `edge/requirements-edge.txt` (`RPi.GPIO`), writes `.env` from `.env.example`, and pre-caches the YOLO weights so the first real run doesn't need internet.
4. Export trained YOLOv8 weights to ONNX or TensorRT for faster inference.
5. Configure the edge process to publish detections to MQTT and the FastAPI REST endpoint.
6. For anything past a bench test, install the systemd units in `backend-fastapi/edge/systemd/` so the backend and capture loop restart on crash and start on boot.

For a starter-tier physical build (Raspberry Pi + camera + HC-SR04 + relay), see [backend-fastapi/edge/capture_loop.py](../backend-fastapi/edge/capture_loop.py) and the full bill of materials, wiring, and systemd setup in [prototype-build-plan.md](prototype-build-plan.md).

## Backend

```powershell
cd backend-fastapi
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env    # then edit DATABASE_URL / JWT_SECRET_KEY / PORTAL_ALERTS_URL
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

`GET /health` reports `db_available`: if Postgres isn't reachable at startup the API still runs, but event history won't survive a restart (see [store.py](../backend-fastapi/app/store.py)). `POST /api/v1/auth/login` (demo users `driver-17` / `operator-1`, password `changeme` — replace before this leaves a bench network) issues the bearer token required by `/api/v1/driver-response` and `/api/v1/brake/release`.

## Database

```bash
createdb railway_safety
psql railway_safety < database/postgresql_schema.sql
```

The backend also runs `Base.metadata.create_all()` against `DATABASE_URL` on startup, so a fresh `railway_safety` database gets its tables even without running the SQL file by hand.

Use MongoDB or object storage for raw camera frames, LiDAR point clouds, and model artifacts.

## Control Portal

```powershell
cd spring-control-service
mvn spring-boot:run
```

Runs on port 8081. Set `PORTAL_ALERTS_URL` on the backend to point at it (defaults to `http://localhost:8081/api/portal/alerts`) — the backend posts every detection there in real time, not just to its own event store.

## Frontend

```powershell
cd frontend-dashboard
npm install
npm run build
npm run preview
```

Set `VITE_API_URL` (see `.env.example`) to the backend's address so the dashboard polls real events instead of its built-in demo data.

## Continuous Integration

[.github/workflows/ci.yml](../.github/workflows/ci.yml) runs `pytest` (backend), `mvn test` (control portal), and `npm run build` (frontend) on every pull request and push to `main` — a merge only ships once all three are green.

## Cloud

- Use AWS IoT Core or Azure IoT Hub for sensor telemetry.
- Store images and LiDAR scans in S3/Azure Blob.
- Deploy FastAPI behind TLS with API gateway and Web Application Firewall.
- Deploy frontend to static hosting or railway control intranet.

## Production Safety

Emergency braking must run through certified train control hardware. The software decision engine should be treated as advisory until validated through railway safety certification.
