from abc import ABC
from collections.abc import Generator
import requests

from dotenv import load_dotenv
import os

load_dotenv()


class Collector(ABC):
    def get_data(self) -> Generator[float | None]:
        raise NotImplementedError


class Phyphox(Collector):
    def __init__(
        self,
        host: str | None = None,
        port: str | int | None = None,
        source: str | None = None,
        buffers: list[str] | None = None,
    ):
        self.phyphox_host = host or os.getenv("PHYPHOX_HOST")
        if not self.phyphox_host:
            raise ValueError("No host provided")

        self.phyphox_port = port or os.getenv("PHYPHOX_PORT")
        if not self.phyphox_port:
            raise ValueError("No port provided")

        self.phyphox_endpoint = f"http://{self.phyphox_host}:{self.phyphox_port}"

        self.request_source = source or "linear_acceleration"
        self.request_buffers = buffers or ["accX", "accY", "accZ"]

        self._check_endpoint()
        self._validate_config()

    def _check_endpoint(self) -> None:
        try:
            response = requests.head(self.phyphox_endpoint)
            response.raise_for_status()

        except (requests.RequestException, requests.Timeout):
            raise ConnectionError("Service unavailable")

    def _validate_config(self) -> None:
        try:
            response_config = requests.get(self.phyphox_endpoint + "/config")
            response_config.raise_for_status()
            json_config = response_config.json()

            experiment_sources = {input.get("source") for input in json_config.get("inputs")}
            experiment_buffers = {buffer.get("name") for buffer in json_config.get("buffers")}

            if self.request_source not in experiment_sources:
                raise ValueError(f"Source not found: '{self.request_source}'")

            if not set(self.request_buffers) <= experiment_buffers:
                raise KeyError(f"Buffers not found: {self.request_buffers - experiment_buffers}")

        except (requests.RequestException, requests.Timeout):
            raise ConnectionError("Config inaccessible")

    def get_data(self) -> Generator[float | None]:
        try:
            response_data = requests.get(f"{self.phyphox_endpoint}/get?{'&'.join(self.request_buffers)}")
            response_data.raise_for_status()
            json_data = response_data.json()

            return (
                next(iter(json_data.get("buffer", {}).get(buffer, {}).get("buffer", [])), None)
                for buffer in self.request_buffers
            )

        except (requests.RequestException, requests.Timeout):
            raise ConnectionError("Service unavailable")

        except requests.exceptions.JSONDecodeError as e:
            raise ValueError(f"JSON Decode Error: {e}")


if __name__ == "__main__":
    Phyphox().get_data()
