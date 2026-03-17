import time
from threading import Thread
from app.mqtt import MqttClient
from app import build_sensor_value_vector

TOTAL_NUMBER_OF_SENSORS = 1

sensor_buffer = {}

def handleMQTTData(data):
    sensorId = data["sensorId"]
    ppm      = data["ppm"]
    humidity = data["humidity"]
    temperature = data["temperature"]
    sensor_buffer[sensorId] = ppm
    print(f"Received → Sensor {sensorId}: {ppm} ppm")

def prediction_loop():
    while True:
        if len(sensor_buffer) > 0:
            transformed_sensor_data = build_sensor_value_vector(sensor_buffer)
            # Pass to your model here
            print(f"Predicting on: {transformed_sensor_data}")
        else:
            print("Waiting for sensor data...")
        
        time.sleep(5)

def main():
    # worker = Thread(target=prediction_loop)
    # worker.daemon = True
    # worker.start()

    mqtt_client = MqttClient(
        broker  = "localhost",
        port    = 1883,
        topic   = "hydrogen/sensors",
        on_data = handleMQTTData
    )
    mqtt_client.connect()  

if __name__ == "__main__":
    main()
