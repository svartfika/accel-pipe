from abc import ABC
import requests

class Collector(ABC):
    pass

class Phyphox(Collector):
    phyphox_host = "0.0.0.0"
    phyphox_port = 65535  # 49152-65535
    phyphox_endpoint = f"http://{phyphox_host}:{phyphox_port}"

    request_source = "linear_acceleration"
    request_buffers = {"accX", "accY", "accZ"}

    experiment_config = requests.get(phyphox_endpoint + "/config").json()
    
    experiment_sources = {input.get("source") for input in experiment_config.get("inputs")}
    if request_source not in experiment_sources:
        raise ValueError(f"Requierd source '{request_source}' not found in experiment")

    experiment_buffers = {buffer.get("name") for buffer in experiment_config.get("buffers")}
    if not request_buffers <= experiment_buffers:
        missing_buffers = request_buffers - experiment_buffers
        raise KeyError(f"Required buffers not found in experiment buffers: {missing_buffers}")
