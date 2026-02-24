class MqttClient:
    def __init__(self, brokerIp: str, brokerPort: str, topic: str, on_data):
        self.brokerIp = brokerIp
        self.brokerPort = brokerPort
        self.topic = topic
        self.client = mqtt.client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.on_data = on_data

    def connect(self):
        self.client.connect(self.brokerIp, self.brokerPort)
        self.client.loop_start()
    
    def disconnect(self):
        self.client.disconnect


    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connection successful!")
            self.client.subscribe(self.topic)
    
    def on_message(self, client, userdata, message):
        payload = message.payload.decode("utf-8")
        self.on_data(payload)
        print("recieved")