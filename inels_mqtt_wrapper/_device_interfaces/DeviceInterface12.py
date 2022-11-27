from ..AbstractDeviceSupportsStatus import AbstractDeviceSupportsStatus, StatusDataType


class DeviceInterface12(AbstractDeviceSupportsStatus):
    """A base class for all the devices implementing the 'device type 12' interface"""

    device_type: str = "12"
    status_message_len_bytes: int = 5

    @staticmethod
    def _decode_status(raw_status_data: bytearray) -> StatusDataType:  # TODO: Testing required
        data_0, data_1, data_2, data_3, data_4 = raw_status_data
        rftc_status = "RFTC is switched to eLAN mode" if data_2 == int.from_bytes(b"\x80", byteorder="big") else None
        return {
            "battery_low": data_2 % 16 == 1,
            "rftc_status": rftc_status,
            "temperature": data_0 * 0.5,
        }
