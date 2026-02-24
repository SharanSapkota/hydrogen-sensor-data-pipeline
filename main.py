
from app.mqtt import MqttClient

def main():
    mqtt_client = MqttClient(broker="localhost", port=1883, topic="test/topic", on_data=handleMQTTData)
    mqtt_client.connect()

def handleMQTTData(data):
    # Todos:
    # 1) transform data to [s1, s2,... sn]
    # 2) pass the transformed data into model
    # 3) pass the data into the model
    # 4) After model gives the output
    # 5) Transform the output into json
    # 6) publish in the MQTT
    print(data)
    # Solution 1)
    
    # type of the data will be json()




if __name__ == "__main__":
    main()