from uuid import uuid4

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.braking import EmergencyBrakeController
from app.decision_engine import decide
from app.notification import send_portal_alert, send_sms_alert
from app.schemas import DriverResponse, ObstacleEvent, SensorReading

app = FastAPI(title="Railway Obstacle Detection API", version="1.0.0")
brakes = EmergencyBrakeController()
events: dict[str, ObstacleEvent] = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "railway-obstacle-detection"}


@app.post("/api/v1/detections", response_model=ObstacleEvent)
def ingest_detection(reading: SensorReading) -> ObstacleEvent:
    decision = decide(reading)
    event = ObstacleEvent(event_id=str(uuid4()), reading=reading, decision=decision)
    events[event.event_id] = event

    if decision.action == "AUTO_BRAKE":
        brakes.apply(f"{reading.object_type} detected {reading.distance_m}m ahead")
        send_sms_alert(event, "+910000000000")

    send_portal_alert(event)
    return event


@app.get("/api/v1/events")
def list_events() -> list[ObstacleEvent]:
    return list(events.values())[-100:]


@app.post("/api/v1/driver-response")
def driver_response(response: DriverResponse) -> dict:
    event = events.get(response.event_id)
    if not event:
        return {"accepted": False, "reason": "event_not_found"}
    return {
        "accepted": True,
        "event_id": response.event_id,
        "driver_action": response.action,
        "operator_id": response.operator_id,
    }


@app.post("/api/v1/brake/release")
def release_brake(operator_id: str) -> dict:
    return brakes.release(operator_id)


@app.websocket("/ws/telemetry")
async def telemetry(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            reading = SensorReading(**await websocket.receive_json())
            event = ingest_detection(reading)
            await websocket.send_json(event.model_dump(mode="json"))
    except WebSocketDisconnect:
        return
