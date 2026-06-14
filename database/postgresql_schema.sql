CREATE TABLE trains (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    route_code TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE obstacle_events (
    id UUID PRIMARY KEY,
    train_id TEXT NOT NULL REFERENCES trains(id),
    object_type TEXT NOT NULL,
    confidence NUMERIC(5,4) NOT NULL,
    risk_level TEXT NOT NULL CHECK (risk_level IN ('small', 'medium', 'large')),
    risk_score NUMERIC(5,4) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    distance_m DOUBLE PRECISION NOT NULL,
    relative_velocity_mps DOUBLE PRECISION NOT NULL,
    track_position TEXT NOT NULL,
    action TEXT NOT NULL,
    brake_status TEXT NOT NULL,
    image_uri TEXT,
    lidar_scan_uri TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE driver_actions (
    id BIGSERIAL PRIMARY KEY,
    event_id UUID NOT NULL REFERENCES obstacle_events(id),
    train_id TEXT NOT NULL REFERENCES trains(id),
    operator_id TEXT NOT NULL,
    action TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    actor_id TEXT NOT NULL,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_obstacle_events_train_created ON obstacle_events(train_id, created_at DESC);
CREATE INDEX idx_obstacle_events_risk ON obstacle_events(risk_level);
