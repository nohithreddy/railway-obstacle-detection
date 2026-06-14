from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"


class BrakeStatus(str, Enum):
    released = "released"
    requested = "requested"
    applied = "applied"


class SensorReading(BaseModel):
    train_id: str = "TRAIN-001"
    latitude: float = 17.385
    longitude: float = 78.4867
    train_speed_mps: float = 22.0
    object_type: str
    confidence: float = Field(ge=0, le=1)
    distance_m: float = Field(gt=0)
    relative_velocity_mps: float = 0.0
    width_m: float = Field(gt=0)
    height_m: float = Field(gt=0)
    track_position: str = "center"
    image_uri: Optional[str] = None
    lidar_scan_uri: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DecisionResult(BaseModel):
    risk_level: RiskLevel
    risk_score: float = Field(ge=0, le=1)
    action: str
    time_to_collision_s: Optional[float]
    braking_distance_m: float
    brake_status: BrakeStatus
    driver_confirmation_required: bool
    message: str


class ObstacleEvent(BaseModel):
    event_id: str
    reading: SensorReading
    decision: DecisionResult
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DriverResponse(BaseModel):
    event_id: str
    train_id: str
    action: str
    operator_id: str
    notes: Optional[str] = None
