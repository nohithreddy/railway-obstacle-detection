from app.schemas import ObstacleEvent


def send_portal_alert(event: ObstacleEvent) -> dict:
    return {
        "channel": "railway_portal",
        "event_id": event.event_id,
        "risk_level": event.decision.risk_level,
        "message": event.decision.message,
        "sent": True,
    }


def send_sms_alert(event: ObstacleEvent, phone_number: str) -> dict:
    return {
        "channel": "sms",
        "to": phone_number,
        "text": f"{event.decision.risk_level.upper()} obstacle: {event.reading.object_type} "
        f"{event.reading.distance_m}m ahead of {event.reading.train_id}",
        "sent": True,
    }
