import asyncio
import contextlib
import re
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional

import asyncio_mqtt as aiomqtt
from _tasks import background_tasks

from ._logging import logger
from .exceptions import DeviceStatusUnknownError


class AbstractDeviceInterface:
    """A base class for all the device interfaces"""

    device_type: str = "UNDEFINED"

    def __init__(self, mac_address: str, device_address: str, mqtt_client: aiomqtt.Client) -> None:
        mac_address = mac_address.upper()
        mac_address_pattern = r"([A-F0-9]{2}:){5}[A-F0-9]{2}"
        assert re.fullmatch(
            mac_address_pattern, mac_address
        ), f"Invalid MAC address: {mac_address}. Valid pattern: {mac_address_pattern}"

        device_address = device_address.upper()
        device_address_pattern = r"[A-F0-9]{6}"
        assert re.fullmatch(
            device_address_pattern, device_address
        ), f"Invalid device address: {device_address}. Valid pattern: {device_address_pattern}"

        self.mac_address: str = mac_address
        self.device_address: str = device_address

        mac_address = mac_address.replace(":", "")
        self._status_topic_name: str = f"inels/status/{mac_address}/{self.device_type}/{device_address}"
        self._set_topic_name: str = f"inels/set/{mac_address}/{self.device_type}/{device_address}"
        self._connected_topic_name: str = f"inels/connected/{mac_address}/{self.device_type}/{device_address}"

        self.is_connected: bool = False

        self._mqtt_client: aiomqtt.Client = mqtt_client

        task = asyncio.create_task(self._listen_on_connected_topic())
        background_tasks.append(task)

        logger.debug(f"Initialized Device interface at {id(self)} for device {self.dev_id}")

    @property
    def dev_id(self) -> str:
        return f"{self.device_type}:{self.device_address}"

    async def _listen_on_topic(self, topic_name: str, callback: Callable[[Any], None]) -> None:
        """
        A task for subscribing to a given MQTT topic
        and feeding the received data to the callback function

        :param topic_name: The name of the topic to subscribe to
        :param callback: Sync function to execute when a message is received
        :return: None
        """
        client = self._mqtt_client
        async with client.filtered_messages(topic_name) as messages:
            logger.debug(f"Attempting subscribing to the topic {topic_name}")

            try:
                await client.subscribe(topic_name)
            except Exception as e:
                logger.error(str(e))
                raise e

            logger.info(f"Started listening on the {topic_name} topic of the device {self.dev_id}")

            while True:
                try:
                    message = await messages.__anext__()
                except asyncio.CancelledError:
                    logger.warning(f"Task cancelled. Stopped listening on topic {topic_name}")
                    break

                payload = message.payload
                callback(payload)

    def _connected_callback(self, data: bytes) -> None:
        data_decoded = data.decode("ascii")
        logger.debug(f"Received a new heartbeat for device {self.dev_id}: {data_decoded}")
        device_is_connected = data_decoded == "on"
        self.is_connected = device_is_connected

    async def _listen_on_connected_topic(self) -> None:
        """
        A task for subscribing to the device's 'connected' MQTT topic
        and updating its 'is_connected' field accordingly

        :return: None
        """
        await self._listen_on_topic(
            topic_name=self._connected_topic_name,
            callback=self._connected_callback,
        )


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

        task = asyncio.create_task(self._listen_on_status_topic())
        background_tasks.append(task)

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

    def _status_callback(self, raw_status_data: bytes) -> None:
        message_str_repr = raw_status_data.decode("ascii").replace("\n", " ").strip()
        logger.debug(f"Status message '{message_str_repr}' received from device {self.dev_id}")
        status_data = [int(byte, 16) for byte in raw_status_data.split()]
        decoded_status = self._decode_status(bytearray(status_data))
        logger.debug(f"Status message '{message_str_repr}' decoded as {decoded_status}")
        self._last_known_status = decoded_status
        logger.debug(f"State of the device {self.dev_id} has changed")
        self._status_updated_event.set()

    async def _listen_on_status_topic(self) -> None:
        """
        A task for subscribing to the device's 'status' MQTT topic
        and updating its '_last_known_status' field accordingly.

        :return: None
        """
        await self._listen_on_topic(
            topic_name=self._status_topic_name,
            callback=self._status_callback,
        )

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

    set_message_len_bytes: int = 0

    async def _publish_to_set_topic(self, payload: bytearray) -> None:
        """
        A method for publishing the provided payload to the device's 'set' MQTT topic.

        :param payload: A bytearray object containing the bytes to be published
        :return: None
        """
        client = self._mqtt_client

        if (l := len(payload)) < self.set_message_len_bytes:
            payload.extend(bytearray(0 for _ in range(self.set_message_len_bytes - l)))

        payload_encoded = payload.hex(" ").upper()
        await client.publish(
            topic=self._set_topic_name,
            payload=payload_encoded,
        )
        logger.debug(f"Payload '{payload_encoded}' published to the MQTT topic {self._set_topic_name}")
