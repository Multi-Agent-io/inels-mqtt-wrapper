from ..interface import AbstractDeviceSupportsSet, AbstractDeviceSupportsStatus, StatusDataType


# TODO: Implement device interface
class DeviceInterface03(AbstractDeviceSupportsStatus, AbstractDeviceSupportsSet):
    """A base class for all the devices implementing the 'device type 03' interface"""

    device_type: str = "03"

    @staticmethod
    def _decode_status(raw_status_data: bytearray) -> StatusDataType:
        raise NotImplementedError  # TODO: Implement _decode_status() method for class DeviceInterface03
