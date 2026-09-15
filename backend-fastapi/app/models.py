import uuid
from datetime import datetime, timezone

from sqlalchemy import BigInteger, Column, Float, ForeignKey, Numeric, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Train(Base):
    __tablename__ = "trains"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    route_code = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=_utcnow)


class ObstacleEventRecord(Base):
    __tablename__ = "obstacle_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    train_id = Column(String, ForeignKey("trains.id"), nullable=False)
    object_type = Column(String, nullable=False)
    confidence = Column(Numeric(5, 4), nullable=False)
    risk_level = Column(String, nullable=False)
    risk_score = Column(Numeric(5, 4), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    distance_m = Column(Float, nullable=False)
    relative_velocity_mps = Column(Float, nullable=False)
    track_position = Column(String, nullable=False)
    action = Column(String, nullable=False)
    brake_status = Column(String, nullable=False)
    image_uri = Column(Text, nullable=True)
    lidar_scan_uri = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=_utcnow)


class DriverAction(Base):
    __tablename__ = "driver_actions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    event_id = Column(UUID(as_uuid=True), ForeignKey("obstacle_events.id"), nullable=False)
    train_id = Column(String, ForeignKey("trains.id"), nullable=False)
    operator_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=_utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    actor_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=False)
    event_metadata = Column("metadata", JSONB, nullable=False, default=dict)
    created_at = Column(TIMESTAMP(timezone=True), default=_utcnow)
