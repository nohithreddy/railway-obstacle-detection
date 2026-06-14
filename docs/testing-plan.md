# Testing Plan

## Unit Tests

- Risk classification for small, medium, and large obstacle classes.
- Braking distance and time-to-collision calculations.
- LiDAR cluster filtering inside track gauge.
- Notification payload formatting.

## Integration Tests

- POST `/api/v1/detections` stores and returns decision data.
- WebSocket `/ws/telemetry` accepts sensor frames and returns event decisions.
- Driver response endpoint rejects unknown event IDs.
- Brake release endpoint records operator ID.

## AI Model Tests

- Validate YOLOv8 mean Average Precision on railway obstacle validation set.
- Test day, night, rain, fog, tunnel, and station scenarios.
- Measure false positive and false negative rates by object class.

## Field Simulation

- Replay recorded videos and LiDAR scans.
- Verify distance estimates against measured ground truth.
- Verify alert latency below operational threshold.
- Confirm large obstacles trigger brake command in simulator.

## Security Tests

- Authentication and role-based access tests.
- TLS and certificate validation.
- Audit-log immutability checks.
- API fuzzing for malformed telemetry payloads.
