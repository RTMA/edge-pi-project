import pika

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
                 trigger=None):
        if config_path:
            import configparser
            config = configparser.ConfigParser()
            config.read(config_path)
            
            self._host = config.get('RabbitMQ', 'host', fallback=host)
            self._port = config.getint('RabbitMQ', 'port', fallback=port)
            self._username = config.get('RabbitMQ', 'username', fallback=username)
            self._password = config.get('RabbitMQ', 'password', fallback=password)
            self._virtual_host = config.get('RabbitMQ', 'virtual_host', fallback=virtual_host)
            self._trigger = trigger
        else:
            self._host = host
            self._port = port
            self._username = username
            self._password = password
            self._virtual_host = virtual_host
            
        
        self._connection = None
        self._channel = None
        
        
    def setup(self):
        if not self._host or not self._port or not self._username or not self._password or not self._virtual_host:
            raise ValueError("RabbitMQ connection parameters are not set.")
    
        credentials = pika.PlainCredentials(self._username, self._password)
        self._connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self._host,
                port=self._port,
                virtual_host=self._virtual_host,
                credentials=credentials
            )
        )
        self._channel = self._connection.channel()
        
    def declare_exchange(self, exchange_name, exchange_type='topic'):
        if not self._channel:
            raise ValueError("Channel is not initialized. Call setup() first.")
        
        self._channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=exchange_type
        )
    
    def declare_queue(self, queue_name):
        if not self._channel:
            raise ValueError("Channel is not initialized. Call setup() first.")
        
        self._channel.queue_declare(queue=queue_name)
        
    def bind_queue(self, queue_name, exchange_name, routing_key):
        if not self._channel:
            raise ValueError("Channel is not initialized. Call setup() first.")
        
        self._channel.queue_bind(
            queue=queue_name,
            exchange=exchange_name,
            routing_key=routing_key
        )
        
    def publish(self, exchange_name, routing_key, message):
        if not self._channel:
            raise ValueError("Channel is not initialized. Call setup() first.")
        self._channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=str(message),
        )
        
    def consume(self, queue_name, callback):
        if not self._channel:
            raise ValueError("Channel is not initialized. Call setup() first.")
        
        self._channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=True
        )
        
    def start_consuming(self):
        if not self._channel:
            raise ValueError("Channel is not initialized. Call setup() first.")
        
        print('Waiting for messages. To exit press CTRL+C')
        self._channel.start_consuming()
        
    def close(self):
        if self._connection:
            self._connection.close()
        if self._channel:
            self._channel.close()
            
    def callback(self, ch, method, properties, body):
        print(f"Received message: {body.decode()}")
        # Hier kan je de logica toevoegen om de ontvangen berichten te verwerken.
            
    def loop(self, band_nummer):
        try:
            self.setup()
            self.declare_exange('Banden')
            self.declare_exange('Detectie')
            self.declare_queue('band_detectie')
            self.bind_queue('band_detectie', 'Banden', f'band_{band_nummer}')
            
            self.consume('band_detectie', self.callback)
            self.start_consuming()
        except KeyboardInterrupt:
            print("Exiting...")
        finally:
            self.close()