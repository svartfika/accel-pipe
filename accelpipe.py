import asyncio
from sensor_stream_manager import SensorStreamManager, Phyphox


async def demo_producer(data):
    print(data)


async def main():
    stream = SensorStreamManager()
    collector_phyphox = Phyphox()

    stream.add_collector(collector_phyphox)
    stream.add_callback(demo_producer)

    await stream.start()


if __name__ == "__main__":
    asyncio.run(main())
