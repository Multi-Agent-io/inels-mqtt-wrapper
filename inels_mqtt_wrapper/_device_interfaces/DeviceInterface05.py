from .._logging import logger
from ..interface import AbstractDeviceSupportsSet, AbstractDeviceSupportsStatus, StatusDataType


class DeviceInterface05(AbstractDeviceSupportsStatus, AbstractDeviceSupportsSet):
    """A base class for all the devices implementing the 'device type 05' interface"""

    device_type: str = "05"

    @staticmethod
    def _decode_status(raw_status_data: bytearray) -> StatusDataType:  # TODO: Testing required
        """
        A method for decoding the device's status from bytes.

        :param raw_status_data: A bytearray object containing the bytes, published by the device in the topic.
        :return: A device-specific dict, containing its status. For this device:
            {"brightness_percentage": 100}
        """
        raw_value = 0xFFFF - int.from_bytes(raw_status_data, byteorder="big")
        brightness_percentage = int((raw_value - 10000) / 1000 * 5)
        return {"brightness_percentage": brightness_percentage}

    @staticmethod
    def _encode_brightness(brightness: int) -> bytes:
        """
        Encode the brightness percentage data into bytes, accepted by the device.

        :param brightness: The desired brightness percentage value.
            Brightness percentage must be an integer between 0 and 100 increased in 10% steps.
        :return: Bytes data, accepted by the device
        """
        out_real = 0xFFFF - (brightness / 5 * 1000 + 10000)
        return int(out_real).to_bytes(length=2, byteorder="big")

    @staticmethod
    def _encode_ramp_time(ramp_time_duration_sec: int) -> bytes:
        """
        Encode the ramp up / ramp down duration into bytes, accepted by the device.

        :param ramp_time_duration_sec: The desired ramp up / ramp down duration in seconds.
        :return: Bytes data, accepted by the device
        """
        out_real = ramp_time_duration_sec / 0.065
        return int(out_real).to_bytes(length=2, byteorder="big")

    async def set_brightness_percentage(self, brightness_percentage: int) -> None:  # TODO: Testing required
        """
        Set the device's desired brightness percentage.

        :param brightness_percentage: The desired brightness percentage value.
            Brightness percentage must be an integer between 0 and 100 increased in 10% steps.
        :return: None
        """
        assert brightness_percentage in range(
            0, 110, 10
        ), "Brightness percentage must be an integer between 0 and 100 increased in 10% steps"
        data_0 = b"\x01"
        payload = bytearray(data_0)
        brightness_encoded = self._encode_brightness(brightness_percentage)
        payload.extend(bytearray(brightness_encoded))
        assert len(payload) == 3
        await self._publish_to_set_topic(payload)
        logger.info(f"Brightness percentage set to {brightness_percentage}% on the device {self.dev_id}")

    async def ramp_up(self) -> None:  # TODO: Testing required
        """
        Execute the device's 'ramp up' command.

        :return: None
        """
        data_0 = b"\x02"
        payload = bytearray(data_0)
        await self._publish_to_set_topic(payload)
        logger.info(f"Ramp up command sent to the device {self.dev_id}")

    async def without_function(self) -> None:  # TODO: Testing required
        """
        Execute the device's 'without function' command.

        :return: None
        """
        data_0 = b"\x04"
        payload = bytearray(data_0)
        await self._publish_to_set_topic(payload)
        logger.info(f"Without function command sent to the device {self.dev_id}")

    async def set_ramp_up_time_seconds(self, ramp_duration_seconds: int) -> None:  # TODO: Testing required
        """
        Set the device's desired ramp up time.

        :param ramp_duration_seconds: The desired duration of the ramp up in seconds.
        :return: None
        """
        assert ramp_duration_seconds >= 0, "Ramp duration must be an integer greater or equal to zero"
        data_0 = b"\x05"
        payload = bytearray(data_0)
        brightness_encoded = self._encode_ramp_time(ramp_duration_seconds)
        payload.extend(bytearray(brightness_encoded))
        assert len(payload) == 3
        await self._publish_to_set_topic(payload)
        logger.info(f"Ramp up time set to {ramp_duration_seconds}s on the device {self.dev_id}")

    async def set_ramp_down_time_seconds(self, ramp_duration_seconds: int) -> None:  # TODO: Testing required
        """
        Set the device's desired ramp down time.

        :param ramp_duration_seconds: The desired duration of the ramp down in seconds.
        :return: None
        """
        assert ramp_duration_seconds >= 0, "Ramp duration must be an integer greater or equal to zero"
        data_0 = b"\x06"
        payload = bytearray(data_0)
        brightness_encoded = self._encode_ramp_time(ramp_duration_seconds)
        payload.extend(bytearray(brightness_encoded))
        assert len(payload) == 3
        await self._publish_to_set_topic(payload)
        logger.info(f"Ramp down time set to {ramp_duration_seconds}s on the device {self.dev_id}")

    async def test_communication(self) -> None:  # TODO: Testing required
        """
        Execute the device's 'test communication' command.

        :return: None
        """
        data_0 = b"\x07"
        payload = bytearray(data_0)
        await self._publish_to_set_topic(payload)
        logger.info(f"Test communication command sent to the device {self.dev_id}")
