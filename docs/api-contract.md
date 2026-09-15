# Railway Portal API Contract

## Auth

`POST /api/v1/auth/login?operator_id=driver-17&password=changeme`

```json
{ "access_token": "<jwt>", "token_type": "bearer", "role": "driver" }
```

Send `Authorization: Bearer <jwt>` on `/api/v1/driver-response` and `/api/v1/brake/release`. `/api/v1/detections` and `/api/v1/events` stay open — the edge device posting telemetry isn't a logged-in human. Demo users: `driver-17` and `operator-1`, both password `changeme` — replace with a real user store before this leaves a bench network.

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
