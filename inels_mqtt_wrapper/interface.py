class AbstractDeviceInterface:
    device_type: str = "UNDEFINED"

    def __init__(self, mac_address: str, device_address: str) -> None:
        self.mac_address: str = mac_address
        self.device_address: str = device_address
        self._status_topic_name: str = f"inels/status/{mac_address}/{self.device_type}/{device_address}"
        self._set_topic_name: str = f"inels/set/{mac_address}/{self.device_type}/{device_address}"
        self._connected_topic_name: str = f"inels/connected/{mac_address}/{self.device_type}/{device_address}"
