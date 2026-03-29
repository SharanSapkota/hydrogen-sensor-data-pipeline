
import time
import json
from collections import deque
import uuid
from datetime import datetime, timezone
from threading import Thread
import paho.mqtt.client as mqtt
# from model import predict


BROKER                  = "localhost"
PORT                    = 1883
TOPIC_SENSORS           = "h2/sensor/mq5"
TOPIC_RESULTS           = "hydrogen/results"
TOTAL_NUMBER_OF_SENSORS = 1
LEAK_PPM_THRESHOLD      = 1000
PREDICTION_INTERVAL     = 5  # seconds

# ─── Shared buffer ───────────────────────────────────────────────────────────

sensor_buffer: dict = {}

# ─── MQTT Client ─────────────────────────────────────────────────────────────

class MqttClient:
    def __init__(self, broker: str, port: int, topic: str, on_data):
        self.broker   = broker
        self.port     = port
        self.topic    = topic
        self.on_data  = on_data
        self.client   = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def connect(self):
        print(f"[MQTT] Connection successful:")

        self.client.connect(self.broker, self.port)
        self.client.loop_forever()

    def disconnect(self):
        self.client.disconnect()

    def publish(self, topic: str, payload: dict):
        self.client.publish(topic, json.dumps(payload))
        print(f"[MQTT] Published to {topic}")

    def _on_connect(self, client, userdata, flags, rc):
        print(f"[MQTT] ----- successful:")
        if rc == 0:
            print(f"[MQTT] Co nnected to broker at {self.broker}:{self.port}")
            self.client.subscribe(self.topic)
            print(f"[MQTT] Subscribed to {self.topic}")
        else:
            print(f"[MQTT] Failed to connect, rc={rc}")

    def _on_message(self, client, userdata, message):
        print(f"[MQTT] Connection on message:")

        try:
            payload = json.loads(message.payload.decode("utf-8"))
            self.on_data(payload, client)
        except Exception as e:
            print(f"[MQTT] Failed to parse message: {e}")

# ─── Data handler ─────────────────────────────────────────────────────────────

history_buffer = deque(maxlen=10)

def handle_mqtt_data(data: dict, client):
    sensor_id   = "1"
    ppm         = data["ppm"]
    humidity    = "10"
    temperature = "10"

    total_sensors = 1

    sensor_data = {
        "sensorId":    sensor_id,
        "ppm":         ppm,
        "humidity":    humidity,
        "temperature": temperature
    }

    sensor_alert = "good"

    if ppm > 50:
        sensor_alert = "Alert"

    if ppm > 70:
        sensor_alert = "High"

    sensor_data["sensor_alert"] = sensor_alert

    history_buffer.append(sensor_data)

    payload = {
        "total_sensors": total_sensors,
        "sensors":       [sensor_data],
        "history":       list(history_buffer)
    }

    client.publish(TOPIC_RESULTS, json.dumps(payload))

    print(f"[Sensor {sensor_id}] {ppm} ppm | {temperature}°C | {humidity}%")
    print(f"[History] {len(history_buffer)}/10 entries stored")


# ─── Prediction loop ─────────────────────────────────────────────────────────

# def prediction_loop(mqtt_client: MqttClient):
#     while True:
#         time.sleep(PREDICTION_INTERVAL)

#         if len(sensor_buffer) < TOTAL_NUMBER_OF_SENSORS:
#             print(f"[Pipeline] Waiting... {len(sensor_buffer)}/{TOTAL_NUMBER_OF_SENSORS} sensors reported")
#             continue

#         print(f"[Pipeline] Running prediction on {len(sensor_buffer)} sensors")

#         # Snapshot and clear buffer
#         snapshot = dict(sensor_buffer)
#         sensor_buffer.clear()

#         # Build matrix ordered by sensor ID
#         ordered_ids = sorted(snapshot.keys())
#         matrix      = [
#             [snapshot[sid]["ppm"], snapshot[sid]["temperature"], snapshot[sid]["humidity"]]
#             for sid in ordered_ids
#         ]

#         # Run model
#         prediction = predict(matrix)

#         print(f"[Pipeline] Decision: {prediction['final_decision']} "
#               f"(KNN: {prediction['knn_confidence']:.2f}, RF: {prediction['rf_confidence']:.2f})")

#         # Only publish if leak detected
#         if prediction["final_decision"] != "leak":
#             print("[Pipeline] No leak — skipping publish")
#             continue

#         # Build result payload matching Node.js expected format
#         payload = {
#             "event_id":    str(uuid.uuid4()),
#             "detected_at": datetime.now(timezone.utc).isoformat(),
#             "prediction":  prediction,
#             "sensors": [
#                 {
#                     "sensor_id":   sid,
#                     "ppm":         snapshot[sid]["ppm"],
#                     "temperature": snapshot[sid]["temperature"],
#                     "humidity":    snapshot[sid]["humidity"],
#                     "timestamp":   int(time.time())
#                 }
#                 for sid in ordered_ids
#             ]
#         }

#         mqtt_client.publish(TOPIC_RESULTS, payload)

# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    mqtt_client = MqttClient(
        broker  = BROKER,
        port    = PORT,
        topic   = TOPIC_SENSORS,
        on_data = handle_mqtt_data
    )

    # Start prediction loop in background thread
    # worker        = Thread(target=prediction_loop, args=(mqtt_client,))
    # worker.daemon = True
    # worker.start()

    # Connect blocks here with loop_forever()
    mqtt_client.connect()

if __name__ == "__main__":
    main()
