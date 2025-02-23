import asyncio
from contextlib import AsyncExitStack

from .collector import Collector


class SensorStreamManager:
    def __init__(self):
        self.collectors: list[Collector] = []
        self.callbacks: list[callable] = []
        self.running = False
        self.update_freq = 20

    def add_collector(self, collector: Collector):
        self.collectors.append(collector)

    def add_callback(self, callback: callable):
        self.callbacks.append(callback)

    async def start(self):
        self.running = True
        async with AsyncExitStack() as stack:
            collectors = [await stack.enter_async_context(c) for c in self.collectors]
            while self.running:
                for collector in collectors:
                    data = dict(
                        zip(
                            ["x", "y", "z"],
                            [value async for value in collector.get_data()],
                        )
                    )
                    for callback in self.callbacks:
                        await callback(data)
                await asyncio.sleep(1.0 / self.update_freq)

    def stop(self):
        self.running = False
