from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
import requests

from dotenv import load_dotenv
import os

import aiohttp
import asyncio

load_dotenv()

PHYPHOX_HOST = os.getenv("PHYPHOX_HOST")
PHYPHOX_PORT = os.getenv("PHYPHOX_PORT")


class Collector(ABC):
    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def get_data(self) -> AsyncGenerator[float | None, None]:  # .asend() is not used therefore [.., None]
        raise NotImplementedError


class Phyphox(Collector):
    def __init__(
        self,
        host: str | None = None,
        port: str | int | None = None,
        source: str | None = None,
        buffers: list[str] | None = None,
        session: aiohttp.ClientSession | None = None,  # session for context manager
    ):
        self.phyphox_host: str = host or PHYPHOX_HOST
        if not self.phyphox_host:
            raise ValueError("No host provided")

        self.phyphox_port: int | str = port or PHYPHOX_PORT
        if not self.phyphox_port:
            raise ValueError("No port provided")

        self.phyphox_endpoint: str = f"http://{self.phyphox_host}:{self.phyphox_port}"

        self.request_source: str = source or "linear_acceleration"
        self.request_buffers: list[str] = buffers or ["accX", "accY", "accZ"]

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        await self._check_endpoint()
        await self._validate_config()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _check_endpoint(self) -> None:
        try:
            async with self.session.head(self.phyphox_endpoint) as response:
                response.raise_for_status()

        except aiohttp.ClientError:
            raise ConnectionError("Service unavailable")

    async def _validate_config(self) -> None:
        try:
            async with self.session.get(self.phyphox_endpoint + "/config") as response_config:
                response_config.raise_for_status()
                json_config = await response_config.json()

                experiment_sources = {input.get("source") for input in json_config.get("inputs")}
                experiment_buffers = {buffer.get("name") for buffer in json_config.get("buffers")}

                if self.request_source not in experiment_sources:
                    raise ValueError(f"Source not found: '{self.request_source}'")

                if not set(self.request_buffers) <= experiment_buffers:
                    raise KeyError(f"Buffers not found: {self.request_buffers - experiment_buffers}")

        except aiohttp.ClientError:
            raise ConnectionError("Config inaccessible")

    async def get_data(self) -> AsyncGenerator[float | None, None]:
        try:
            async with self.session.get(
                f"{self.phyphox_endpoint}/get?{'&'.join(self.request_buffers)}"
            ) as response_data:
                response_data.raise_for_status()
                json_data = await response_data.json()

                for buffer in self.request_buffers:
                    yield next(iter(json_data.get("buffer", {}).get(buffer, {}).get("buffer", [])), None)

        except aiohttp.ClientError:
            raise ConnectionError("Service unavailable")

        except requests.exceptions.JSONDecodeError as e:
            raise ValueError(f"JSON Decode Error: {e}")


async def main():
    async with Phyphox() as phyphox:
        while True:
            async for result in phyphox.get_data():
                print(result)
            await asyncio.sleep(0.05)  # 20Hz


if __name__ == "__main__":
    asyncio.run(main())
