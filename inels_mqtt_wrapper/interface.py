import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import asyncio_mqtt as aiomqtt

from .exceptions import DeviceDisconnectedError, DeviceStatusUnknownError

# TODO: Add logging throughout the library


class AbstractDeviceInterface:
    """A base class for all the device interfaces"""

    device_type: str = "UNDEFINED"

    def __init__(self, mac_address: str, device_address: str, mqtt_client: aiomqtt.Client) -> None:
        self.mac_address: str = mac_address
        self.device_address: str = device_address

        self._status_topic_name: str = f"inels/status/{mac_address}/{self.device_type}/{device_address}"
        self._set_topic_name: str = f"inels/set/{mac_address}/{self.device_type}/{device_address}"
        self._connected_topic_name: str = f"inels/connected/{mac_address}/{self.device_type}/{device_address}"

        self.is_connected: bool = False

        self._mqtt_client: aiomqtt.Client = mqtt_client

        asyncio.create_task(self._listen_on_connected_topic())

    async def _listen_on_connected_topic(self) -> None:
        """
        A task for subscribing to the device's 'connected' MQTT topic
        and updating its 'is_connected' field accordingly
        :return: No return
        """
        client = self._mqtt_client

        async with client.filtered_messages(self._connected_topic_name) as messages:
            await client.subscribe(self._connected_topic_name)
            async for message in messages:
                device_is_connected = bool(message.payload)
                self.is_connected = device_is_connected


StatusDataType = Dict[str, Any]


class AbstractDeviceSupportsStatus(AbstractDeviceInterface, ABC):
    """A base class for all the device interfaces supporting communication via the 'status' MQTT topic"""

    def __init__(self, mac_address: str, device_address: str, mqtt_client: aiomqtt.Client) -> None:
        super().__init__(
            mac_address=mac_address,
            device_address=device_address,
            mqtt_client=mqtt_client,
        )

        self._last_known_status: Optional[StatusDataType] = None

        asyncio.create_task(self._listen_on_status_topic())

    @property
    def status(self) -> StatusDataType:
        """
        A property for getting the last known device status as a dictionary with device-specific keys.

        Raises DeviceStatusUnknownError if the device's last status is unknown.
        :return: No return
        """
        if self._last_known_status is None:
            raise DeviceStatusUnknownError(f"Unknown device status for device {self.__class__.__name__}")
        return self._last_known_status

    async def _listen_on_status_topic(self) -> None:
        """
        A task for subscribing to the device's 'status' MQTT topic
        and updating its '_last_known_status' field accordingly.
        :return: No return
        """
        client = self._mqtt_client

        async with client.filtered_messages(self._status_topic_name) as messages:
            await client.subscribe(self._status_topic_name)
            async for message in messages:
                raw_status_data: bytearray = message.payload
                decoded_status = self._decode_status(raw_status_data)
                self._last_known_status = decoded_status

    @staticmethod
    @abstractmethod
    def _decode_status(raw_status_data: bytearray) -> StatusDataType:
        """
        An abstract method for decoding the device's status from bytes.
        :param raw_status_data: A bytearray object containing the bytes, published by the device in the topic.
        :return: Decoded device status as a dictionary with device-specific keys.
        """
        raise NotImplementedError


class AbstractDeviceSupportsSet(AbstractDeviceInterface):
    """A base class for all the device interfaces supporting communication via the 'set' MQTT topic"""

    async def _publish_to_set_topic(self, payload: bytearray) -> None:
        """
        A method for publishing the provided payload to the device's 'set' MQTT topic.
        :param payload: A bytearray object containing the bytes to be published
        :return: No return
        """
        if not self.is_connected:
            raise DeviceDisconnectedError(
                f"Device '{self.__class__.__name__}' is disconnected. "
                "Cannot publish new messages to the device's set topic unless the device is connected"
            )

        client = self._mqtt_client
        await client.publish(
            topic=self._set_topic_name,
            payload=payload,
        )
