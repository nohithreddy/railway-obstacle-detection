import json

import paho.mqtt.client as mqtt

from app.schemas import ObstacleEvent


def publish_event(event: ObstacleEvent, broker_host: str = "localhost", topic: str = "railway/events") -> None:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(broker_host, 1883, 30)
    client.publish(topic, json.dumps(event.model_dump(mode="json")), qos=1)
    client.disconnect()
