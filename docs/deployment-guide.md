# Deployment Guide

## Edge Device

1. Install Ubuntu 22.04 on Jetson Orin or Raspberry Pi.
2. Connect LiDAR, camera, GPS, IMU, and modem.
3. Install Python, OpenCV, Ultralytics YOLO, and MQTT client libraries.
4. Export trained YOLOv8 weights to ONNX or TensorRT for faster inference.
5. Configure the edge process to publish detections to MQTT and the FastAPI REST endpoint.

## Backend

```powershell
cd backend-fastapi
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Database

```bash
createdb railway_safety
psql railway_safety < database/postgresql_schema.sql
```

Use MongoDB or object storage for raw camera frames, LiDAR point clouds, and model artifacts.

## Frontend

```powershell
cd frontend-dashboard
npm install
npm run build
npm run preview
```

## Cloud

- Use AWS IoT Core or Azure IoT Hub for sensor telemetry.
- Store images and LiDAR scans in S3/Azure Blob.
- Deploy FastAPI behind TLS with API gateway and Web Application Firewall.
- Deploy frontend to static hosting or railway control intranet.

## Production Safety

Emergency braking must run through certified train control hardware. The software decision engine should be treated as advisory until validated through railway safety certification.
