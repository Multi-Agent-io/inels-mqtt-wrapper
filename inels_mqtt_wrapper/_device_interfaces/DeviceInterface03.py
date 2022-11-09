from ..interface import AbstractDeviceSupportsSet, AbstractDeviceSupportsStatus, StatusDataType


# TODO: Implement device interface
class DeviceInterface03(AbstractDeviceSupportsStatus, AbstractDeviceSupportsSet):
    """A base class for all the devices implementing the 'device type 03' interface"""

    device_type: str = "03"

    @staticmethod
    def _decode_status(raw_status_data: bytearray) -> StatusDataType:
        raise NotImplementedError  # TODO: Implement _decode_status() method for class DeviceInterface03

    async def immediately_pull_up_the_shutters(self) -> None:
        """
        Immediately pulls up the shutters
        :return: No return
        """
        # TODO: Doc needs clarification
        # TODO: Implementation
        raise NotImplementedError

    async def start_shutters_up(self) -> None:
        """
        Starts pulling the shutters up
        :return: No return
        """
        # TODO: Implementation
        raise NotImplementedError

    async def stop_shutters_up(self) -> None:
        """
        Stops pulling the shutters up
        :return: No return
        """
        # TODO: Implementation
        raise NotImplementedError

    async def start_shutters_down(self) -> None:
        """
        Starts pulling the shutters down
        :return: No return
        """
        # TODO: Implementation
        raise NotImplementedError

    async def stop_shutters_down(self) -> None:
        """
        Stops pulling the shutters down
        :return: No return
        """
        # TODO: Implementation
        raise NotImplementedError

    @staticmethod
    def _encode_time(time_seconds_int: int) -> bytes:
        """
        Encode the time in seconds to get the byte value accepted by the device
        :param time_seconds_int: A time value in seconds to be encoded
        :return: No return
        """
        assert time_seconds_int >= 0, "A value must by greater or equal to zero"
        out_value = int(time_seconds_int / 0.06577)
        return out_value.to_bytes(length=2, byteorder="big")

    async def set_shutter_up_time(self, time_seconds: int) -> None:
        """
        Setting the time when the shutters pull up
        :param time_seconds: A time in seconds when the shutters will be pulled up
        :return: No return
        """
        # TODO: Doc needs clarification
        # TODO: Implementation
        raise NotImplementedError

    async def set_shutter_down_time(self, time_seconds: int) -> None:
        """
        Setting the time when the shutters pull down
        :param time_seconds: A time in seconds when the shutters will be pulled down
        :return: No return
        """
        # TODO: Doc needs clarification
        # TODO: Implementation
        raise NotImplementedError
