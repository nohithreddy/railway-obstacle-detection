# Railway Obstacle Detection and Intelligent Train Control System

Industrial-grade project scaffold for an AI-powered railway safety system using LiDAR, cameras, GPS/IMU, real-time decisioning, notifications, emergency braking simulation, and a 3D control dashboard.

## Modules

- `backend-fastapi/` - Python FastAPI service for detections, decision engine, braking, notifications, WebSocket telemetry, and simulated sensor ingestion.
- `frontend-dashboard/` - React + Three.js railway control portal with live obstacle visualization.
- `spring-control-service/` - Java Spring Boot service skeleton for enterprise railway portal integration.
- `database/` - PostgreSQL schema and MongoDB event shape.
- `docs/` - Architecture diagrams, UML/sequence/use-case diagrams, deployment guide, testing plan, B.Tech report, and IEEE paper draft.

## Design

- Figma dashboard mockup: https://www.figma.com/design/djhbfdvqNsDoG5vVZCfy5j

## Quick Start

### Backend

```powershell
cd C:\Users\91767\Downloads\railway-obstacle-detection\backend-fastapi
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```powershell
cd C:\Users\91767\Downloads\railway-obstacle-detection\frontend-dashboard
npm install
npm run dev
```

Open `http://localhost:5173`.

## Safety Note

This repository is a final-year/project-grade reference implementation and simulator. Real railway braking, signaling, and safety-critical deployment require certified hardware, fail-safe control systems, railway authority approval, formal verification, redundancy, and compliance with applicable standards such as EN 50126, EN 50128, EN 50129, IEC 61508, and local railway regulations.
