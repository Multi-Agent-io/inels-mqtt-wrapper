from typing import AsyncGenerator

from .interface import AbstractDeviceInterface

import asyncio_mqtt as aiomqtt


# TODO: Implement device interface
class DeviceInterface02(AbstractDeviceInterface):
    device_type: str = "02"


# TODO: Implement device interface
class DeviceInterface03(AbstractDeviceInterface):
    device_type: str = "03"


# TODO: Implement device interface
class DeviceInterface05(AbstractDeviceInterface):
    device_type: str = "05"

    @staticmethod
    def _decode_brightness(status_message: bytes) -> int:
        data_0, data_1 = status_message.split()
        raw_value = 0xFFFF - int(f"{data_0}{data_1}", 16)
        return int((raw_value - 10000) / 1000 * 5)

    @staticmethod
    def _encode_brightness(brightness: int) -> bytes:
        out_real = 0xFFFF - (brightness / 5 * 1000 + 10000)
        return int(out_real).to_bytes(length=2, byteorder="big")

    async def read_brightness(self, client: aiomqtt.Client) -> AsyncGenerator[None, None, int]:
        """Subscribe to a topic yielding brightness values in percent"""
        async with client.unfiltered_messages() as messages:
            await client.subscribe(self._status_topic_name)
            async for message in messages:
                payload: bytes = message.payload  # TODO: Should it be decoded? Does it actually return a string instead?
                yield self._decode_brightness(payload)


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
