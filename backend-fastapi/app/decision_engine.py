from app.schemas import BrakeStatus, DecisionResult, RiskLevel, SensorReading


LARGE_CLASSES = {"truck", "bus", "derailment", "fallen_tree", "rockslide", "train", "large_vehicle"}
MEDIUM_CLASSES = {"person", "human", "cow", "buffalo", "horse", "motorcycle", "car", "small_vehicle"}
SMALL_CLASSES = {"plastic_bag", "small_animal", "debris", "branch", "rock"}


def estimate_braking_distance(speed_mps: float, deceleration_mps2: float = 0.85) -> float:
    if speed_mps <= 0:
        return 0.0
    return round((speed_mps * speed_mps) / (2 * deceleration_mps2), 2)


def classify_risk(reading: SensorReading) -> RiskLevel:
    object_type = reading.object_type.lower()
    area = reading.width_m * reading.height_m

    if object_type in LARGE_CLASSES or area >= 6.0:
        return RiskLevel.large
    if object_type in MEDIUM_CLASSES or area >= 1.0:
        return RiskLevel.medium
    if object_type in SMALL_CLASSES:
        return RiskLevel.small
    return RiskLevel.medium if reading.track_position == "center" else RiskLevel.small


def decide(reading: SensorReading) -> DecisionResult:
    closing_speed = max(reading.train_speed_mps + reading.relative_velocity_mps, 0.1)
    ttc = round(reading.distance_m / closing_speed, 2)
    braking_distance = estimate_braking_distance(reading.train_speed_mps)
    risk = classify_risk(reading)

    proximity_score = max(0.0, min(1.0, 1 - reading.distance_m / max(braking_distance * 1.5, 1)))
    class_score = {RiskLevel.small: 0.25, RiskLevel.medium: 0.62, RiskLevel.large: 0.92}[risk]
    risk_score = round(max(class_score, proximity_score) * reading.confidence, 2)

    if risk == RiskLevel.large:
        return DecisionResult(
            risk_level=risk,
            risk_score=risk_score,
            action="AUTO_BRAKE",
            time_to_collision_s=ttc,
            braking_distance_m=braking_distance,
            brake_status=BrakeStatus.applied,
            driver_confirmation_required=False,
            message="Large obstacle detected. Emergency brake applied and control room notified.",
        )

    if risk == RiskLevel.medium:
        return DecisionResult(
            risk_level=risk,
            risk_score=risk_score,
            action="REQUEST_DRIVER_DECISION",
            time_to_collision_s=ttc,
            braking_distance_m=braking_distance,
            brake_status=BrakeStatus.requested if reading.distance_m <= braking_distance else BrakeStatus.released,
            driver_confirmation_required=True,
            message="Medium obstacle detected. Driver decision required.",
        )

    return DecisionResult(
        risk_level=risk,
        risk_score=risk_score,
        action="WARN_DRIVER",
        time_to_collision_s=ttc,
        braking_distance_m=braking_distance,
        brake_status=BrakeStatus.released,
        driver_confirmation_required=False,
        message="Small obstacle detected. Warning issued; operation may continue.",
    )
