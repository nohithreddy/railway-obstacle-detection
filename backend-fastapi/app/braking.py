import os
from datetime import datetime

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None


class EmergencyBrakeController:
    """Simulated by default. Set BRAKE_RELAY_GPIO_PIN on a Raspberry Pi to
    drive a real relay board that cuts motor power on AUTO_BRAKE."""

    def __init__(self) -> None:
        self.applied = False
        self.last_reason = ""
        self.last_applied_at: datetime | None = None

        gpio_pin = os.environ.get("BRAKE_RELAY_GPIO_PIN")
        self._gpio_pin = int(gpio_pin) if gpio_pin else None
        if self._gpio_pin is not None and GPIO is not None:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self._gpio_pin, GPIO.OUT, initial=GPIO.LOW)

    def apply(self, reason: str) -> dict:
        self.applied = True
        self.last_reason = reason
        self.last_applied_at = datetime.utcnow()
        self._set_relay(True)
        return {
            "status": "applied",
            "reason": reason,
            "applied_at": self.last_applied_at.isoformat() + "Z",
        }

    def release(self, operator_id: str) -> dict:
        self.applied = False
        self._set_relay(False)
        return {
            "status": "released",
            "operator_id": operator_id,
            "released_at": datetime.utcnow().isoformat() + "Z",
        }

    def _set_relay(self, engaged: bool) -> None:
        if self._gpio_pin is not None and GPIO is not None:
            GPIO.output(self._gpio_pin, GPIO.HIGH if engaged else GPIO.LOW)
