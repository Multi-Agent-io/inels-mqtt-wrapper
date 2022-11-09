from ..interface import AbstractDeviceSupportsSet, AbstractDeviceSupportsStatus, StatusDataType


# TODO: Implement device interface
# TODO: Cannot implement the public 'set' interface - specification unclear
class DeviceInterface09(AbstractDeviceSupportsStatus, AbstractDeviceSupportsSet):
    """A base class for all the devices implementing the 'device type 09' interface"""

    device_type: str = "09"

    @staticmethod
    def _decode_status(raw_status_data: bytearray) -> StatusDataType:
        raise NotImplementedError  # TODO: Implement _decode_status() method for class DeviceInterface09
