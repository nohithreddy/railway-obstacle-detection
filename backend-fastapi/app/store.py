import logging
import uuid
from typing import Optional

from sqlalchemy.exc import OperationalError

from app import models
from app.db import Base, SessionLocal, engine
from app.schemas import ObstacleEvent

logger = logging.getLogger("railway.store")


class EventStore:
    """Reads are served from an in-memory cache of the current process's events (fast, no
    DB round trip for the dashboard poll loop). Writes go to Postgres when it's reachable,
    so the event history survives a restart; if it isn't (dev machine, fresh edge device
    with no DB stood up yet), writes are skipped and the API still works off the cache.
    """

    def __init__(self) -> None:
        self._cache: dict[str, ObstacleEvent] = {}
        self.db_available = self._connect()

    def _connect(self) -> bool:
        try:
            Base.metadata.create_all(bind=engine)
            with engine.connect():
                pass
            return True
        except OperationalError:
            logger.warning("Postgres unreachable at startup — event history will not persist across restarts.")
            return False

    def save(self, event: ObstacleEvent) -> None:
        self._cache[event.event_id] = event
        if not self.db_available:
            return

        session = SessionLocal()
        try:
            if session.get(models.Train, event.reading.train_id) is None:
                session.add(models.Train(id=event.reading.train_id, name=event.reading.train_id, route_code="UNSPECIFIED"))
            session.add(
                models.ObstacleEventRecord(
                    id=uuid.UUID(event.event_id),
                    train_id=event.reading.train_id,
                    object_type=event.reading.object_type,
                    confidence=event.reading.confidence,
                    risk_level=event.decision.risk_level.value,
                    risk_score=event.decision.risk_score,
                    latitude=event.reading.latitude,
                    longitude=event.reading.longitude,
                    distance_m=event.reading.distance_m,
                    relative_velocity_mps=event.reading.relative_velocity_mps,
                    track_position=event.reading.track_position,
                    action=event.decision.action,
                    brake_status=event.decision.brake_status.value,
                    image_uri=event.reading.image_uri,
                    lidar_scan_uri=event.reading.lidar_scan_uri,
                )
            )
            session.commit()
        except Exception:
            session.rollback()
            logger.exception("Failed to persist event %s", event.event_id)
        finally:
            session.close()

    def get(self, event_id: str) -> Optional[ObstacleEvent]:
        return self._cache.get(event_id)

    def list_recent(self, limit: int = 100) -> list[ObstacleEvent]:
        return list(self._cache.values())[-limit:]

    def record_driver_action(self, event_id: str, train_id: str, operator_id: str, action: str, notes: Optional[str]) -> None:
        if not self.db_available:
            return

        session = SessionLocal()
        try:
            session.add(
                models.DriverAction(
                    event_id=uuid.UUID(event_id),
                    train_id=train_id,
                    operator_id=operator_id,
                    action=action,
                    notes=notes,
                )
            )
            session.commit()
        except Exception:
            session.rollback()
            logger.exception("Failed to record driver action for event %s", event_id)
        finally:
            session.close()
