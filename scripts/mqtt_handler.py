import configparser
import paho.mqtt.client as mqtt
import random

class MQTTHandler:
    def __init__(self, config_path="config/config.ini", on_trigger=None, logger=None):
        self.on_trigger = on_trigger
        self.logger = logger
        self.load_config(config_path)
        self.setup_client()

    def load_config(self, config_path):
        config = configparser.ConfigParser()
        config.read(config_path)

        mqtt_cfg = config["MQTT"]
        self.broker = mqtt_cfg.get("broker")
        self.port = mqtt_cfg.getint("port")
        self.username = mqtt_cfg.get("username")
        self.password = mqtt_cfg.get("password")
        self.topic_subscribe = mqtt_cfg.get("topic_subscribe")
        self.topic_publish = mqtt_cfg.get("topic_publish")
        base_id = mqtt_cfg.get("client_id")
        self.client_id = f"{base_id}_{random.randint(1000, 9999)}"

    def setup_client(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=self.client_id)
        self.client.username_pw_set(self.username, self.password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def start(self):
        self.logger.info("MQTT verbinden met %s:%d als %s", self.broker, self.port, self.client_id)
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.logger.info("Verbonden met MQTT broker. Abonneren op: %s", self.topic_subscribe)
            client.subscribe(self.topic_subscribe)
        else:
            self.logger.error("Verbinding met broker mislukt. Code: %s", rc)

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8").strip()
        self.logger.info("Bericht ontvangen op topic %s: %s", msg.topic, payload)
        if self.on_trigger:
            self.on_trigger(payload)

    def publish_detectie_resultaat(self, label):
        topic = f"{self.topic_publish}{label}/1"
        self.client.publish(topic, payload=label)
        self.logger.info("Verzend: %s naar topic: %s", label, topic)
