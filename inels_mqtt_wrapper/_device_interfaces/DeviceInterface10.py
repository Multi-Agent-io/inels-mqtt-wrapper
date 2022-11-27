from ..AbstractDeviceSupportsStatus import AbstractDeviceSupportsStatus, StatusDataType


class DeviceInterface10(AbstractDeviceSupportsStatus):
    """A base class for all the devices implementing the 'device type 10' interface"""

    device_type: str = "10"
    status_message_len_bytes: int = 5

    @staticmethod
    def _decode_status(raw_status_data: bytearray) -> StatusDataType:
        data_0, data_2, data_3, data_4, data_5 = raw_status_data
        temperature_in = int.from_bytes(bytearray((data_2, data_3)), byteorder="little", signed=True) / 100
        temperature_out = int.from_bytes(bytearray((data_4, data_5)), byteorder="little", signed=True) / 100
        return {
            "battery_low": bool(data_0),
            "temperature_in": temperature_in,
            "temperature_out": temperature_out,
        }
