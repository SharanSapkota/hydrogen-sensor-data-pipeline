import time
from threading import Thread
from app.mqtt import MqttClient
from app import build_sensor_value_vector

TOTAL_NUMBER_OF_SENSORS = 10

sensor_buffer = {}
def main():
    mqtt_client = MqttClient(broker="localhost", port=1883, topic="test/topic", on_data=handleMQTTData)
    mqtt_client.connect()

def handleMQTTData(data):
    sensorId = data["sensorId"]
    ppm = data["hydrogenPpm"]
    sensor_buffer[sensorId] = ppm


def prediction_loop():
    transformed_sensor_data = build_sensor_value_vector(sensor_buffer)
    # Pass this value to the model
    time.sleep(5)

if __name__ == "__main__":
    main()
    while (true):
        worker = Thread(target=prediction_loop)
        worker.daemon = True
        worker.start()