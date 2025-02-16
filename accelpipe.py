import asyncio
from sensor_stream_manager import SensorStreamManager, Phyphox
from time import time_ns


async def demo_callback(data):
    print({"timestamp": time_ns()} | data)


async def main():
    stream = SensorStreamManager()
    collector_phyphox = Phyphox()

    stream.add_collector(collector_phyphox)
    stream.add_callback(demo_callback)

    await stream.start()


if __name__ == "__main__":
    asyncio.run(main())
