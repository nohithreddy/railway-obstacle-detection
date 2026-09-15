import logging
import os

import requests

from app.schemas import ObstacleEvent

logger = logging.getLogger("railway.notification")

PORTAL_ALERTS_URL = os.environ.get("PORTAL_ALERTS_URL", "http://localhost:8081/api/portal/alerts")


def send_portal_alert(event: ObstacleEvent) -> dict:
    payload = {
        "eventId": event.event_id,
        "trainId": event.reading.train_id,
        "objectType": event.reading.object_type,
        "riskLevel": event.decision.risk_level.value,
        "latitude": event.reading.latitude,
        "longitude": event.reading.longitude,
        "distanceM": event.reading.distance_m,
        "action": event.decision.action,
    }
    try:
        response = requests.post(PORTAL_ALERTS_URL, json=payload, timeout=2.0)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        logger.warning("Control portal unreachable at %s: %s", PORTAL_ALERTS_URL, exc)
        return {"channel": "railway_portal", "event_id": event.event_id, "sent": False, "reason": "portal_unreachable"}


def send_sms_alert(event: ObstacleEvent, phone_number: str) -> dict:
    return {
        "channel": "sms",
        "to": phone_number,
        "text": f"{event.decision.risk_level.upper()} obstacle: {event.reading.object_type} "
        f"{event.reading.distance_m}m ahead of {event.reading.train_id}",
        "sent": True,
    }
