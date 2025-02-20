import dotenv
import os

dotenv.load_dotenv()

KAFKA_HOST = os.getenv("KAFKA_HOST", "localhost")
KAFKA_PORT = os.getenv("KAFKA_PORT", 9092)

KAFKA_CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP", "sensor_group")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "sensor_data")
