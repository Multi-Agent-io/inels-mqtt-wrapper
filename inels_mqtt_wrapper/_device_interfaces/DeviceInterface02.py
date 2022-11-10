from ..interface import AbstractDeviceSupportsSet, AbstractDeviceSupportsStatus, StatusDataType


class DeviceInterface02(AbstractDeviceSupportsStatus, AbstractDeviceSupportsSet):
    """A base class for all the devices implementing the 'device type 02' interface"""

    device_type: str = "02"

    @staticmethod
    def _decode_status(raw_status_data: bytearray) -> StatusDataType:  # TODO: Testing required
        """
        A method for decoding the device's status from bytes.

        :param raw_status_data: A bytearray object containing the bytes, published by the device in the topic.
        :return: A device-specific dict, containing its status. For this device:
            {"unit_id": 2, "switched_on": True}
        """
        data_0, data_1 = raw_status_data
        return {
            "unit_id": data_0,
            "switched_on": bool(data_1),
        }

    @staticmethod
    def _encode_ramp_time(ramp_time_duration_sec: int) -> bytes:
        """
        Encode the ramp up / ramp down duration into bytes, accepted by the device.

        :param ramp_time_duration_sec: The desired ramp up / ramp down duration in seconds.
        :return: Bytes data, accepted by the device
        """
        # TODO: Implementation. Encoding algorithm unknown: specification missing the description.
        assert 0 < ramp_time_duration_sec <= 60 * 60, "The delay time must not exceed 60 minutes."
        raise NotImplementedError

    async def switch_on(self) -> None:  # TODO: Testing required
        """
        Switch on the device

        :return: None
        """
        data_0 = b"\x01"
        payload = bytearray(data_0)
        await self._publish_to_set_topic(payload)

    async def switch_off(self) -> None:  # TODO: Testing required
        """
        Switch off the device

        :return: None
        """
        data_0 = b"\x02"
        payload = bytearray(data_0)
        await self._publish_to_set_topic(payload)

    async def impulse(self) -> None:  # TODO: Testing required
        """
        Execute the device's 'impulse' command.

        :return: None
        """
        data_0 = b"\x03"
        payload = bytearray(data_0)
        await self._publish_to_set_topic(payload)

    async def ramp_down(self) -> None:  # TODO: Testing required
        """
        Execute the device's 'ramp down' command.

        :return: None
        """
        data_0 = b"\x04"
        payload = bytearray(data_0)
        await self._publish_to_set_topic(payload)

    async def ramp_up(self) -> None:  # TODO: Testing required
        """
        Execute the device's 'ramp up' command.

        :return: None
        """
        data_0 = b"\x05"
        payload = bytearray(data_0)
        await self._publish_to_set_topic(payload)

    async def test_communication(self) -> None:  # TODO: Testing required
        """
        Execute the device's 'test communication' command.

        :return: None
        """
        data_0 = b"\x08"
        payload = bytearray(data_0)
        await self._publish_to_set_topic(payload)

    async def set_ramp_down_time_seconds(self, ramp_duration_seconds: int) -> None:  # TODO: Testing required
        """
        Set the device's desired ramp down time. The device will be switched off
        (ramp down) after the set amount of seconds. The delay must not exceed 60 minutes.

        :param ramp_duration_seconds: The desired duration of the ramp down in seconds.
            Must not exceed 60 minutes.
        :return: None
        """
        data_0 = b"\x06"
        payload = bytearray(data_0)
        raw_ramp_time = self._encode_ramp_time(ramp_duration_seconds)
        payload.extend(bytearray(raw_ramp_time))
        assert len(payload) == 3
        await self._publish_to_set_topic(payload)

    async def set_ramp_up_time_seconds(self, ramp_duration_seconds: int) -> None:  # TODO: Testing required
        """
        Set the device's desired ramp down time. The device will be switched on
        (ramp up) after the set amount of seconds. The delay must not exceed 60 minutes.

        :param ramp_duration_seconds: The desired duration of the ramp up in seconds.
            Must not exceed 60 minutes.
        :return: None
        """
        data_0 = b"\x07"
        payload = bytearray(data_0)
        raw_ramp_time = self._encode_ramp_time(ramp_duration_seconds)
        payload.extend(bytearray(raw_ramp_time))
        assert len(payload) == 3
        await self._publish_to_set_topic(payload)
