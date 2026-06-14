from app.decision_engine import decide
from app.schemas import BrakeStatus, RiskLevel, SensorReading


def test_small_obstacle_warns_driver():
    result = decide(
        SensorReading(
            object_type="debris",
            confidence=0.9,
            distance_m=120,
            width_m=0.3,
            height_m=0.2,
        )
    )

    assert result.risk_level == RiskLevel.small
    assert result.action == "WARN_DRIVER"
    assert result.brake_status == BrakeStatus.released


def test_medium_obstacle_requests_driver_decision():
    result = decide(
        SensorReading(
            object_type="person",
            confidence=0.95,
            distance_m=80,
            width_m=0.6,
            height_m=1.7,
        )
    )

    assert result.risk_level == RiskLevel.medium
    assert result.driver_confirmation_required is True


def test_large_obstacle_applies_brake():
    result = decide(
        SensorReading(
            object_type="truck",
            confidence=0.98,
            distance_m=60,
            width_m=2.4,
            height_m=3.0,
        )
    )

    assert result.risk_level == RiskLevel.large
    assert result.action == "AUTO_BRAKE"
    assert result.brake_status == BrakeStatus.applied
