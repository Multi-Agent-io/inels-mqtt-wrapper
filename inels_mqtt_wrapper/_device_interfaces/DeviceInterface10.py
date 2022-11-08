from ..interface import AbstractDeviceSupportsStatus, StatusDataType


# TODO: Implement device interface
class DeviceInterface10(AbstractDeviceSupportsStatus):
    """A base class for all the devices implementing the 'device type 10' interface"""

    device_type: str = "10"

    @staticmethod
    def _decode_status(raw_status_data: bytearray) -> StatusDataType:
        raise NotImplementedError  # TODO: Implement _decode_status() method for class DeviceInterface10
