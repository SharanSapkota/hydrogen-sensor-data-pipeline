

import time
import json
import joblib
import numpy as np
import pandas as pd
from collections import deque
import uuid
from datetime import datetime, timezone
from threading import Thread

import paho.mqtt.client as mqtt


BROKER             = "localhost"
PORT               = 1883
TOPIC_SENSORS      = "h2/sensor/mq5"
TOPIC_RESULTS      = "hydrogen/results"
PREDICTION_INTERVAL = 5     
HISTORY_SIZE        = 10     
MODEL_PATH          = "hydrogen_leak_model.pkl"  


print("[Model] Loading XGBoost model...")
model = joblib.load(MODEL_PATH)
print("[Model] Model loaded successfully.")


sensor_history: dict = {}


def get_ppm_trend_features(sensor_id: str, current_ppm: float):
    """
    Compute ppm_rate and ppm_trend from rolling history.

    ppm_rate  = how fast PPM changed since last reading
    ppm_trend = average change over the last N readings
    """
    if sensor_id not in sensor_history:
        sensor_history[sensor_id] = deque(maxlen=HISTORY_SIZE)

    history = sensor_history[sensor_id]

    # Rate: difference from previous reading
    if len(history) >= 1:
        ppm_rate = current_ppm - history[-1]
    else:
        ppm_rate = 0.0

    # Trend: average rate of change over whole window
    if len(history) >= 2:
        diffs     = [history[i] - history[i-1] for i in range(1, len(history))]
        ppm_trend = float(np.mean(diffs))
    else:
        ppm_trend = 0.0

    # Add current reading to history
    history.append(current_ppm)

    return ppm_rate, ppm_trend


def predict_leak(ppm, temperature, humidity, ppm_rate, ppm_trend):
    """
    Feed one sensor reading into the XGBoost model.
    Returns: prediction (0 or 1), confidence (0–100%)
    """
    sample = pd.DataFrame([{
        "ppm":         ppm,
        "temperature": temperature,
        "humidity":    humidity,
        "ppm_rate":    ppm_rate,
        "ppm_trend":   ppm_trend
    }])

    prediction = model.predict(sample)[0]
    confidence = model.predict_proba(sample)[0][1] * 100   # % chance of leak

    return int(prediction), round(confidence, 2)



def handle_mqtt_data(data: dict, client):
    """
    Called every time a sensor message arrives over MQTT.
    Runs prediction immediately and publishes result.
    """

    # ── Read incoming values ───────────────────────────────
    sensor_id   = str(data.get("sensor_id", "1"))
    ppm         = float(data.get("ppm", 0))
    temperature = float(data.get("temperature", 25))   # ← must come from real sensor
    humidity    = float(data.get("humidity", 50))       # ← must come from real sensor

    # ── Compute time-trend features from rolling history ──
    ppm_rate, ppm_trend = get_ppm_trend_features(sensor_id, ppm)

    # ── Run XGBoost model ─────────────────────────────────
    prediction, confidence = predict_leak(
        ppm, temperature, humidity, ppm_rate, ppm_trend
    )

    is_leak = prediction == 1

    # ── Build result payload ──────────────────────────────
    result = {
        "event_id":    str(uuid.uuid4()),
        "detected_at": datetime.now(timezone.utc).isoformat(),
        "sensor_id":   sensor_id,
        "readings": {
            "ppm":         ppm,
            "temperature": temperature,
            "humidity":    humidity,
            "ppm_rate":    ppm_rate,
            "ppm_trend":   ppm_trend
        },
        "prediction": {
            "leak_detected": is_leak,
            "confidence":    confidence,        # e.g. 94.2 means 94.2% sure it's a leak
            "label":         "LEAK" if is_leak else "NORMAL"
        }
    }

    # ── Publish result back over MQTT ─────────────────────
    client.publish(TOPIC_RESULTS, json.dumps(result))

    # ── Console log ───────────────────────────────────────
    status = "🚨 LEAK" if is_leak else "✅ NORMAL"
    print(
        f"[Sensor {sensor_id}] "
        f"PPM={ppm:.1f} | Temp={temperature:.1f}°C | Hum={humidity:.1f}% | "
        f"Rate={ppm_rate:.2f} | Trend={ppm_trend:.2f} | "
        f"{status} ({confidence:.1f}% confidence)"
    )



class MqttClient:
    def __init__(self, broker, port, topic, on_data):
        self.broker  = broker
        self.port    = port
        self.topic   = topic
        self.on_data = on_data
        self.client  = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def connect(self):
        self.client.connect(self.broker, self.port)
        self.client.loop_forever()

    def disconnect(self):
        self.client.disconnect()

    def publish(self, topic: str, payload: dict):
        self.client.publish(topic, json.dumps(payload))

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"[MQTT] Connected to broker at {self.broker}:{self.port}")
            self.client.subscribe(self.topic)
            print(f"[MQTT] Subscribed to topic: {self.topic}")
        else:
            print(f"[MQTT] Failed to connect, rc={rc}")

    def _on_message(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            self.on_data(payload, client)
        except Exception as e:
            print(f"[MQTT] Failed to parse message: {e}")



def main():
    mqtt_client = MqttClient(
        broker  = BROKER,
        port    = PORT,
        topic   = TOPIC_SENSORS,
        on_data = handle_mqtt_data
    )

    print(f"[Pipeline] Starting. Listening on topic: {TOPIC_SENSORS}")
    print(f"[Pipeline] Publishing results to:        {TOPIC_RESULTS}")
    mqtt_client.connect()


if __name__ == "__main__":
    main()


