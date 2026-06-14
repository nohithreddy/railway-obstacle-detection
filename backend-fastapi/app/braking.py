from datetime import datetime


class EmergencyBrakeController:
    def __init__(self) -> None:
        self.applied = False
        self.last_reason = ""
        self.last_applied_at: datetime | None = None

    def apply(self, reason: str) -> dict:
        self.applied = True
        self.last_reason = reason
        self.last_applied_at = datetime.utcnow()
        return {
            "status": "applied",
            "reason": reason,
            "applied_at": self.last_applied_at.isoformat() + "Z",
        }

    def release(self, operator_id: str) -> dict:
        self.applied = False
        return {
            "status": "released",
            "operator_id": operator_id,
            "released_at": datetime.utcnow().isoformat() + "Z",
        }
