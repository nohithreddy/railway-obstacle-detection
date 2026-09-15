from uuid import uuid4

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.braking import EmergencyBrakeController
from app.decision_engine import decide
from app.notification import send_portal_alert, send_sms_alert
from app.schemas import DriverResponse, ObstacleEvent, SensorReading
from app.security import CurrentUser, Role, authenticate, create_access_token, get_current_user, require_permission
from app.store import EventStore

app = FastAPI(title="Railway Obstacle Detection API", version="1.0.0")
brakes = EmergencyBrakeController()
store = EventStore()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "railway-obstacle-detection", "db_available": store.db_available}


@app.post("/api/v1/auth/login")
def login(operator_id: str, password: str) -> dict:
    role = authenticate(operator_id, password)
    token = create_access_token(operator_id, role)
    return {"access_token": token, "token_type": "bearer", "role": role.value}


@app.post("/api/v1/detections", response_model=ObstacleEvent)
def ingest_detection(reading: SensorReading) -> ObstacleEvent:
    decision = decide(reading)
    event = ObstacleEvent(event_id=str(uuid4()), reading=reading, decision=decision)
    store.save(event)

    if decision.action == "AUTO_BRAKE":
        brakes.apply(f"{reading.object_type} detected {reading.distance_m}m ahead")
        send_sms_alert(event, "+910000000000")

    send_portal_alert(event)
    return event


@app.get("/api/v1/events")
def list_events() -> list[ObstacleEvent]:
    return store.list_recent(100)


@app.post("/api/v1/driver-response")
def driver_response(response: DriverResponse, user: CurrentUser = Depends(get_current_user)) -> dict:
    require_permission(user.role, "submit_driver_response")
    if response.operator_id != user.operator_id:
        return {"accepted": False, "reason": "operator_mismatch"}

    event = store.get(response.event_id)
    if not event:
        return {"accepted": False, "reason": "event_not_found"}

    store.record_driver_action(response.event_id, response.train_id, user.operator_id, response.action, response.notes)
    return {
        "accepted": True,
        "event_id": response.event_id,
        "driver_action": response.action,
        "operator_id": user.operator_id,
    }


@app.post("/api/v1/brake/release")
def release_brake(user: CurrentUser = Depends(get_current_user)) -> dict:
    require_permission(user.role, "release_brake")
    return brakes.release(user.operator_id)


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
