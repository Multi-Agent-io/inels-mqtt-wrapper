import asyncio
import contextlib
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import asyncio_mqtt as aiomqtt

from ._logging import logger
from .exceptions import DeviceDisconnectedError, DeviceStatusUnknownError

# TODO: Add logging throughout the library


class AbstractDeviceInterface:
    """A base class for all the device interfaces"""

    device_type: str = "UNDEFINED"

    def __init__(self, mac_address: str, device_address: str, mqtt_client: aiomqtt.Client) -> None:
        mac_address = mac_address.capitalize()
        mac_address_pattern = r"([A-F0-9]{2}:){5}[A-F0-9]{2}"
        assert re.fullmatch(
            mac_address_pattern, mac_address
        ), f"Invalid MAC address: {mac_address}. Valid pattern: {mac_address_pattern}"

        device_address = device_address.capitalize()
        device_address_pattern = r"[A-F0-9]{6}"
        assert re.fullmatch(
            device_address_pattern, device_address
        ), f"Invalid device address: {device_address}. Valid pattern: {device_address_pattern}"

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

        :return: None
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
        self._status_updated_event: asyncio.Event = asyncio.Event()

        asyncio.create_task(self._listen_on_status_topic())

    async def await_state_change(self, timeout_sec: int = 10) -> bool:
        """
        Wait for a status update to occur within the timeout period.
        Exits returning True immediately as the state change has been
        detected, exits returning False if the given time ran out.

        :param timeout_sec: Timeout duration in seconds. Defaults to 10s
        :return: True if the state change occurred, False if it timed out
        """
        if self._status_updated_event.is_set():
            self._status_updated_event.clear()
        with contextlib.suppress(asyncio.TimeoutError):
            await asyncio.wait_for(self._status_updated_event.wait(), timeout_sec)
        if state_changed := self._status_updated_event.is_set():
            logger.debug(f"State change received on device {self.dev_id}")
        else:
            logger.warning(f"State change await timed out in {timeout_sec}s")
        return state_changed

    @property
    def status(self) -> StatusDataType:
        """
        A property for getting the last known device status as a dictionary with
        device-specific keys. Example of the device-specific status dict can be found
        in the docstring of the concrete implementation's _decode_status() method.

        Raises DeviceStatusUnknownError if the device's last status is unknown.

        :return: None
        """
        if self._last_known_status is None:
            raise DeviceStatusUnknownError(f"Unknown device status for device {self.__class__.__name__}")
        return self._last_known_status

    async def _listen_on_status_topic(self) -> None:
        """
        A task for subscribing to the device's 'status' MQTT topic
        and updating its '_last_known_status' field accordingly.

        :return: None
        """
        client = self._mqtt_client

        async with client.filtered_messages(self._status_topic_name) as messages:
            await client.subscribe(self._status_topic_name)
            async for message in messages:
                raw_status_data: bytearray = message.payload
                decoded_status = self._decode_status(raw_status_data)
                self._last_known_status = decoded_status
                self._status_updated_event.set()

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
        :return: None
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
        logger.debug(f"Payload {payload} published to the MQTT topic {self._set_topic_name}")
