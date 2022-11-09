from ..interface import AbstractDeviceSupportsSet, AbstractDeviceSupportsStatus, StatusDataType


# TODO: Implement device interface
class DeviceInterface02(AbstractDeviceSupportsStatus, AbstractDeviceSupportsSet):
    """A base class for all the devices implementing the 'device type 02' interface"""

    device_type: str = "02"

    @staticmethod
    def _decode_status(raw_status_data: bytearray) -> StatusDataType:
        raise NotImplementedError  # TODO: Implement _decode_status() method for class DeviceInterface02

    @staticmethod
    def _encode_ramp_time(ramp_time_duration_sec: int) -> bytes:
        """
        Encode the ramp up / ramp down duration into bytes, accepted by the device.
        :param ramp_time_duration_sec: The desired ramp up / ramp down duration in seconds.
        :return: Bytes data, accepted by the device
        """
        # TODO: Implementation
        raise NotImplementedError

    async def switch_on(self) -> None:
        """
        Switch on the device
        :return: No return
        """
        # TODO: Implementation
        raise NotImplementedError

    async def switch_off(self) -> None:
        """
        Switch off the device
        :return: No return
        """
        # TODO: Implementation
        raise NotImplementedError

    async def impulse(self) -> None:
        """
        Execute the device's 'impulse' command.
        :return: No return
        """
        # TODO: Doc needs clarification
        # TODO: Implementation
        raise NotImplementedError

    async def ramp_down(self) -> None:
        """
        Execute the device's 'ramp down' command.
        :return: No return
        """
        # TODO: Doc needs clarification
        # TODO: Implementation
        raise NotImplementedError

    async def ramp_up(self) -> None:
        """
        Execute the device's 'ramp up' command.
        :return: No return
        """
        # TODO: Doc needs clarification
        # TODO: Implementation
        raise NotImplementedError

    async def test_communication(self) -> None:  # TODO: Testing required
        """
        Execute the device's 'test communication' command.
        :return: No return
        """
        data_0 = b"\x08"
        payload = bytearray(data_0)
        await self._publish_to_set_topic(payload)

    async def set_ramp_down_time_seconds(self, ramp_duration_seconds: int) -> None:
        """
        Set the device's desired ramp down time.
        :param ramp_duration_seconds: The desired duration of the ramp down in seconds.
        :return: No return
        """
        # TODO: Doc needs clarification
        # TODO: Implementation
        raise NotImplementedError

    async def set_ramp_up_time_seconds(self, ramp_duration_seconds: int) -> None:
        """
        Set the device's desired ramp up time.
        :param ramp_duration_seconds: The desired duration of the ramp up in seconds.
        :return: No return
        """
        # TODO: Doc needs clarification
        # TODO: Implementation
        raise NotImplementedError
