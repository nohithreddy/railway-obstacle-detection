#!/usr/bin/env bash
# One-shot setup for the Raspberry Pi. Run from backend-fastapi/:
#   bash edge/setup_pi.sh
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
pip install -r edge/requirements-edge.txt

if [ ! -f .env ]; then
    cp .env.example .env
    echo "Wrote .env from .env.example — edit DATABASE_URL / JWT_SECRET_KEY / PORTAL_ALERTS_URL / BRAKE_RELAY_GPIO_PIN before first real run."
fi

# Cache YOLO weights now, while there's internet — a field demo with a flaky
# Pi hotspot shouldn't depend on downloading them mid-run.
python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

echo "Setup done. Next:"
echo "  1. edit .env"
echo "  2. wire the sensor + relay per docs/prototype-build-plan.md, verify with a multimeter"
echo "  3. either run manually (see deployment-guide.md) or install the systemd units in edge/systemd/"
