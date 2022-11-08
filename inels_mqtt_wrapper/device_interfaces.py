from .interface import AbstractDeviceSupportsSet, AbstractDeviceSupportsStatus, StatusDataType


# TODO: Implement device interface
class DeviceInterface02(AbstractDeviceInterface):
    device_type: str = "02"


# TODO: Implement device interface
class DeviceInterface03(AbstractDeviceInterface):
    device_type: str = "03"


class DeviceInterface05(AbstractDeviceSupportsStatus, AbstractDeviceSupportsSet):
    device_type: str = "05"

    @staticmethod
    def _decode_status(raw_status_data: bytearray) -> StatusDataType:
        raw_value = 0xFFFF - int.from_bytes(raw_status_data, byteorder="big")
        brightness_percentage = int((raw_value - 10000) / 1000 * 5)
        return {"brightness_percentage": brightness_percentage}

    @staticmethod
    def _encode_brightness(brightness: int) -> bytes:
        out_real = 0xFFFF - (brightness / 5 * 1000 + 10000)
        return int(out_real).to_bytes(length=2, byteorder="big")

    @staticmethod
    def _encode_ramp_time(ramp_time_duration_sec: int) -> bytes:
        out_real = ramp_time_duration_sec / 0.065
        return int(out_real).to_bytes(length=2, byteorder="big")

    async def set_brightness_percentage(self, brightness_percentage: int) -> None:
        assert brightness_percentage in range(
            0, 110, 10
        ), "Brightness percentage must be an integer between 0 and 100 increased in 10% steps"
        data_0 = b"\x01"
        payload = bytearray(data_0)
        brightness_encoded = self._encode_brightness(brightness_percentage)
        payload.extend(bytearray(brightness_encoded))
        assert len(payload) == 3
        await self._publish_to_set_topic(payload)

    async def ramp_up(self) -> None:
        data_0 = b"\x02"
        payload = bytearray(data_0)
        await self._publish_to_set_topic(payload)

    async def without_function(self) -> None:
        data_0 = b"\x04"
        payload = bytearray(data_0)
        await self._publish_to_set_topic(payload)

    async def set_ramp_up_time_seconds(self, ramp_duration_seconds: int) -> None:
        assert ramp_duration_seconds >= 0, "Ramp duration must be an integer greater or equal to zero"
        data_0 = b"\x05"
        payload = bytearray(data_0)
        brightness_encoded = self._encode_ramp_time(ramp_duration_seconds)
        payload.extend(bytearray(brightness_encoded))
        assert len(payload) == 3
        await self._publish_to_set_topic(payload)

    async def set_ramp_down_time_seconds(self, ramp_duration_seconds: int) -> None:
        assert ramp_duration_seconds >= 0, "Ramp duration must be an integer greater or equal to zero"
        data_0 = b"\x06"
        payload = bytearray(data_0)
        brightness_encoded = self._encode_ramp_time(ramp_duration_seconds)
        payload.extend(bytearray(brightness_encoded))
        assert len(payload) == 3
        await self._publish_to_set_topic(payload)

    async def test_communication(self) -> None:
        data_0 = b"\x07"
        payload = bytearray(data_0)
        await self._publish_to_set_topic(payload)


# TODO: Implement device interface
class DeviceInterface09(AbstractDeviceInterface):
    device_type: str = "09"


# TODO: Implement device interface
class DeviceInterface10(AbstractDeviceInterface):
    device_type: str = "10"


# TODO: Implement device interface
class DeviceInterface12(AbstractDeviceInterface):
    device_type: str = "12"


# TODO: Implement device interface
class DeviceInterface19(AbstractDeviceInterface):
    device_type: str = "19"
