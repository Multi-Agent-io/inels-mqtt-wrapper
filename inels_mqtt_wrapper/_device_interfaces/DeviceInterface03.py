from .._logging import logger
from ..AbstractDeviceSupportsSet import AbstractDeviceSupportsSet
from ..AbstractDeviceSupportsStatus import AbstractDeviceSupportsStatus, StatusDataType


class DeviceInterface03(AbstractDeviceSupportsStatus, AbstractDeviceSupportsSet):
    """A base class for all the devices implementing the 'device type 03' interface"""

    device_type: str = "03"
    status_message_len_bytes: int = 2
    set_message_len_bytes: int = 3

    @staticmethod
    def _decode_status(raw_status_data: bytearray) -> StatusDataType:  # TODO: Testing required
        """
        A method for decoding the device's status from bytes.

        :param raw_status_data: A bytearray object containing the bytes, published by the device in the topic.
        :return: A device-specific dict, containing its status. For this device:
            {"unit_id": 3, "shutters_are_up": True, "shutters_are_down": False}
        """
        data_0, data_1 = raw_status_data
        return {
            "unit_id": data_0,
            "shutters_are_up": data_1 == int.from_bytes(b"\x00", byteorder="big"),
            "shutters_are_down": data_1 == int.from_bytes(b"\x01", byteorder="big"),
        }

    async def immediately_pull_up_the_shutters(self) -> None:  # TODO: Testing required
        """
        Immediately pulls up the shutters

        :return: None
        """
        data_0 = b"\x01"
        payload = bytearray(data_0)
        await self._publish_to_set_topic(payload)
        logger.info(f"Command to immediately pull up the shutters sent to the device {self.dev_id}")

    async def immediately_pull_down_the_shutters(self) -> None:  # TODO: Testing required
        """
        Immediately pulls down the shutters

        :return: None
        """
        data_0 = b"\x02"
        payload = bytearray(data_0)
        await self._publish_to_set_topic(payload)
        logger.info(f"Command to immediately pull down the shutters sent to the device {self.dev_id}")

    async def start_shutters_up(self) -> None:  # TODO: Testing required
        """
        Starts pulling the shutters up

        :return: None
        """
        data_0 = b"\x03"
        payload = bytearray(data_0)
        await self._publish_to_set_topic(payload)
        logger.info(f"Command to start pulling up the shutters sent to the device {self.dev_id}")

    async def stop_shutters_up(self) -> None:  # TODO: Testing required
        """
        Stops pulling the shutters up

        :return: None
        """
        data_0 = b"\x04"
        payload = bytearray(data_0)
        await self._publish_to_set_topic(payload)
        logger.info(f"Command to stop pulling up the shutters sent to the device {self.dev_id}")

    async def start_shutters_down(self) -> None:  # TODO: Testing required
        """
        Starts pulling the shutters down

        :return: None
        """
        data_0 = b"\x05"
        payload = bytearray(data_0)
        await self._publish_to_set_topic(payload)
        logger.info(f"Command to start pulling down the shutters sent to the device {self.dev_id}")

    async def stop_shutters_down(self) -> None:  # TODO: Testing required
        """
        Stops pulling the shutters down

        :return: None
        """
        data_0 = b"\x06"
        payload = bytearray(data_0)
        await self._publish_to_set_topic(payload)
        logger.info(f"Command to stop pulling down the shutters sent to the device {self.dev_id}")

    async def test_communication(self) -> None:  # TODO: Testing required
        """
        Make the device send a heartbeat to the 'connected' MQTT topic

        :return: None
        """
        data_0 = b"\x09"
        payload = bytearray(data_0)
        await self._publish_to_set_topic(payload)
        logger.info(f"Test communication command sent to the device {self.dev_id}")

    @staticmethod
    def _encode_time(time_seconds_int: int) -> bytes:
        """
        Encode the time in seconds to get the byte value accepted by the device

        :param time_seconds_int: A time value in seconds to be encoded
        :return: None
        """
        assert time_seconds_int >= 0, "A value must by greater or equal to zero"
        out_value = int(time_seconds_int / 0.06577)
        return out_value.to_bytes(length=2, byteorder="big")

    async def set_shutter_up_time(self, time_seconds: int) -> None:  # TODO: Testing required
        """
        Setting the time when the shutters pull up

        :param time_seconds: A time in seconds when the shutters will be pulled up
        :return: None
        """
        data_0 = b"\x07"
        raw_time_data = self._encode_time(time_seconds)
        payload = bytearray(data_0)
        payload.extend(bytearray(raw_time_data))
        await self._publish_to_set_topic(payload)
        logger.info(f"Shutter up time set to {time_seconds}s on the device {self.dev_id}")

    async def set_shutter_down_time(self, time_seconds: int) -> None:  # TODO: Testing required
        """
        Setting the time when the shutters pull down

        :param time_seconds: A time in seconds when the shutters will be pulled down
        :return: None
        """
        data_0 = b"\x08"
        raw_time_data = self._encode_time(time_seconds)
        payload = bytearray(data_0)
        payload.extend(bytearray(raw_time_data))
        await self._publish_to_set_topic(payload)
        logger.info(f"Shutter down time set to {time_seconds}s on the device {self.dev_id}")
