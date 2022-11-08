from ..interface import AbstractDeviceSupportsStatus, StatusDataType


# TODO: Implement device interface
class DeviceInterface19(AbstractDeviceSupportsStatus):
    """A base class for all the devices implementing the 'device type 19' interface"""

    device_type: str = "19"

    @staticmethod
    def _decode_status(raw_status_data: bytearray) -> StatusDataType:
        raise NotImplementedError  # TODO: Implement _decode_status() method for class DeviceInterface19
