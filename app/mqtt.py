import paho.mqtt.client as mqtt
import json

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
        self.client.connect(self.broker, self.port)
        self.client.loop_forever()                

    def disconnect(self):
        self.client.disconnect()                 

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker!")
            self.client.subscribe(self.topic)
        else:
            print(f"Failed to connect, rc={rc}")

    def _on_message(self, client, userdata, message):   
        payload = json.loads(message.payload.decode("utf-8")) 
        self.on_data(payload)
        print("Received message")