# Railway Portal API Contract

## Ingest Detection

`POST /api/v1/detections`

```json
{
  "train_id": "TRAIN-001",
  "latitude": 17.385,
  "longitude": 78.4867,
  "train_speed_mps": 22,
  "object_type": "person",
  "confidence": 0.94,
  "distance_m": 72.5,
  "relative_velocity_mps": 0,
  "width_m": 0.6,
  "height_m": 1.7,
  "track_position": "center"
}
```

## Response

```json
{
  "event_id": "uuid",
  "decision": {
    "risk_level": "medium",
    "action": "REQUEST_DRIVER_DECISION",
    "brake_status": "released",
    "driver_confirmation_required": true
  }
}
```

## Driver Response

`POST /api/v1/driver-response`

```json
{
  "event_id": "uuid",
  "train_id": "TRAIN-001",
  "action": "SLOW_DOWN",
  "operator_id": "driver-17",
  "notes": "Obstacle moving away from track"
}
```

## Control Portal (spring-control-service, port 8081)

`POST /api/portal/alerts` - forward an event from the FastAPI backend to the control portal.

```json
{
  "eventId": "uuid",
  "trainId": "TRAIN-001",
  "objectType": "person",
  "riskLevel": "medium",
  "latitude": 17.385,
  "longitude": 78.4867,
  "distanceM": 72.5,
  "action": "REQUEST_DRIVER_DECISION"
}
```

`GET /api/portal/alerts?trainId=TRAIN-001` - list alerts, newest first, optionally filtered by train.

`GET /api/portal/alerts/{eventId}` - fetch one alert.

`POST /api/portal/emergency-response/{eventId}` - activate the emergency response protocol for an event.

`GET /api/portal/trains/{trainId}/status` - latest alert, alert count, and whether emergency response is active for a train.

`GET /api/portal/audit-log` - recent portal actions (alert received, emergency activated), newest first.
