import asyncio
from sensor_stream_manager import SensorStreamManager, Phyphox
from time import time_ns
from quixstreams import Application
from quixstreams.kafka.producer import Producer
from constants import KAFKA_HOST, KAFKA_PORT, KAFKA_TOPIC
from functools import partial


app = Application(broker_address=f"{KAFKA_HOST}:{KAFKA_PORT}")
topic = app.topic(name=KAFKA_TOPIC, value_serializer="json")


async def kafka_producer(producer: Producer, data):
    message = topic.serialize(key="sensor_xyz", value=data)
    producer.produce(topic=topic.name, key=message.key, value=message.value)


async def demo_callback(data):
    print({"timestamp": time_ns()} | data)


async def main():
    stream = SensorStreamManager()
    collector_phyphox = Phyphox()

    stream.add_collector(collector_phyphox)
    stream.add_callback(demo_callback)

    with app.get_producer() as producer:
        stream.add_callback(partial(kafka_producer, producer))

    await stream.start()


if __name__ == "__main__":
    asyncio.run(main())
