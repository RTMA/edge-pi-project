import pika
import logging

class Rabbit:
    
    _host = None
    _port = None
    _username = None
    _password = None
    _virtual_host = None
    
    _connection = None
    _channel = None
    
    def __init__(self, 
                 host='localhost', 
                 port=5672, 
                 username='guest', 
                 password='guest',
                 virtual_host='/',
                 config_path=None, 
                 on_trigger=None,
                 logger=None):
        self._on_trigger = on_trigger

        if logger is None:
            logging.basicConfig(level=logging.INFO)
            self._logger = logging.getLogger(__name__)
        else:
            self._logger = logger

        if config_path:
            import configparser
            config = configparser.ConfigParser()
            config.read(config_path)
            
            self._host = config.get('RABBITMQ', 'host', fallback=host)
            self._port = config.getint('RABBITMQ', 'port', fallback=port)
            self._username = config.get('RABBITMQ', 'username', fallback=username)
            self._password = config.get('RABBITMQ', 'password', fallback=password)
            self._virtual_host = config.get('RABBITMQ', 'virtual_host', fallback=virtual_host)
            self._band_nummer = config.getint('RABBITMQ', 'band_nummer', fallback=10)
            self._logger.info(f"Loaded RabbitMQ config from {config_path}")
        else:
            self._host = host
            self._port = port
            self._username = username
            self._password = password
            self._virtual_host = virtual_host
            self._logger.info("Using direct RabbitMQ parameters")
            self._band_nummer = 10  # Default band number if not specified in config
        
        self._connection = None
        self._channel = None
        
    def setup(self):
        if not self._host or not self._port or not self._username or not self._password or not self._virtual_host:
            self._logger.error("RabbitMQ connection parameters are not set.")
            raise ValueError("RabbitMQ connection parameters are not set.")
    
        credentials = pika.PlainCredentials(self._username, self._password)
        self._logger.info(f"Connecting to RabbitMQ at {self._host}:{self._port} with virtual host '{self._virtual_host}'")
        self._logger.info(f"Using username: {self._username} and password: {'*' * len(self._password)}")
        self._connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self._host,
                port=self._port,
                virtual_host=self._virtual_host,
                credentials=credentials
            )
        )
        self._channel = self._connection.channel()
        self._logger.info("RabbitMQ connection and channel established.")
        
    def declare_exchange(self, exchange_name, exchange_type='topic'):
        if not self._channel:
            self._logger.error("Channel is not initialized. Call setup() first.")
            raise ValueError("Channel is not initialized. Call setup() first.")
        
        self._channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=exchange_type
        )
        self._logger.info(f"Declared exchange '{exchange_name}' of type '{exchange_type}'.")
    
    def declare_queue(self, queue_name):
        if not self._channel:
            self._logger.error("Channel is not initialized. Call setup() first.")
            raise ValueError("Channel is not initialized. Call setup() first.")
        
        self._channel.queue_declare(queue=queue_name)
        self._logger.info(f"Declared queue '{queue_name}'.")
        
    def bind_queue(self, queue_name, exchange_name, routing_key):
        if not self._channel:
            self._logger.error("Channel is not initialized. Call setup() first.")
            raise ValueError("Channel is not initialized. Call setup() first.")
        
        self._channel.queue_bind(
            queue=queue_name,
            exchange=exchange_name,
            routing_key=routing_key
        )
        self._logger.info(f"Bound queue '{queue_name}' to exchange '{exchange_name}' with routing key '{routing_key}'.")
        
    def publish(self, exchange_name, routing_key, message):
        if not self._channel:
            self._logger.error("Channel is not initialized. Call setup() first.")
            raise ValueError("Channel is not initialized. Call setup() first.")
        self._channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=str(message),
        )
        self._logger.info(f"Published message to exchange '{exchange_name}' with routing key '{routing_key}': {message}")
        
    def consume(self, queue_name, callback):
        if not self._channel:
            self._logger.error("Channel is not initialized. Call setup() first.")
            raise ValueError("Channel is not initialized. Call setup() first.")
        
        self._channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=True
        )
        self._logger.info(f"Started consuming queue '{queue_name}'.")
        
    def start_consuming(self):
        if not self._channel:
            self._logger.error("Channel is not initialized. Call setup() first.")
            raise ValueError("Channel is not initialized. Call setup() first.")
        
        self._logger.info('Waiting for messages. To exit press CTRL+C')
        self._channel.start_consuming()
        
    def close(self):
        if self._connection:
            self._connection.close()
            self._logger.info("RabbitMQ connection closed.")
        if self._channel:
            self._channel.close()
            self._logger.info("RabbitMQ channel closed.")
            
    def callback(self, ch, method, properties, body: bytes):
        msg = body.decode()
        self._logger.info(f"Received message: {msg}")
        if self._on_trigger:
            self._on_trigger(msg)
            
    def loop(self):
        try:
            self.setup()
            self.declare_exchange('Banden')
            self.declare_queue(f'band_detectie_band_{self._band_nummer}')
            self.bind_queue(f'band_detectie_band_{self._band_nummer}', 'Banden', f'band.{self._band_nummer}')
            
            self.consume(f'band_detectie_band_{self._band_nummer}', self.callback)
            self.start_consuming()
        except KeyboardInterrupt:
            self._logger.info("Exiting...")
            
    def send_label(self, label):
        if not self._channel:
            self._logger.error("Channel is not initialized. Call setup() first.")
            raise ValueError("Channel is not initialized. Call setup() first.")
        
        routing_key = f"detectie.b{self._band_nummer}"
        self.publish('Detectie', routing_key, label)