from ..interface import AbstractDeviceSupportsStatus, StatusDataType


class DeviceInterface12(AbstractDeviceSupportsStatus):
    """A base class for all the devices implementing the 'device type 12' interface"""

    device_type: str = "12"

    @staticmethod
    def _decode_status(raw_status_data: bytearray) -> StatusDataType:  # TODO: Testing required
        data_0, data_1, data_2, data_3, data_4 = raw_status_data
        return {
            "battery_low": data_2 % 16 == 1,
            "rftc_status": "RFTC is switched to eLAN mode" if bytes(data_2) == b"\x80" else None,
            "temperature": data_0 * 0.5,
        }
