import asyncio
import contextlib
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import asyncio_mqtt as aiomqtt

from ._logging import logger
from ._tasks import background_tasks
from .AbstractDeviceInterface import AbstractDeviceInterface
from .exceptions import DeviceStatusUnknownError

StatusDataType = Dict[str, Any]


class AbstractDeviceSupportsStatus(AbstractDeviceInterface, ABC):
    """A base class for all the device interfaces supporting communication via the 'status' MQTT topic"""

    status_message_len_bytes: int = 0

    def __init__(self, mac_address: str, device_address: str, mqtt_client: aiomqtt.Client) -> None:
        super().__init__(
            mac_address=mac_address,
            device_address=device_address,
            mqtt_client=mqtt_client,
        )
        assert self.status_message_len_bytes != 0, (
            f"Incomplete interface implementation for class '{self.__class__.__name__}': "
            "'status_message_len_bytes' class field must be overriden in inheriting class."
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
        status_data = bytearray(int(byte, 16) for byte in raw_status_data.split())

        if (l := len(status_data)) != self.status_message_len_bytes:
            msg = (
                f"Cannot decode device status. Wrong status message payload size: {l} bytes. "
                f"Expected: {self.status_message_len_bytes} bytes"
            )
            logger.error(msg)
            raise ValueError(msg)

        try:
            decoded_status = self._decode_status(status_data)
        except Exception as e:
            logger.error(f"An error occurred while decoding status message: {e}")
            raise e
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
