import asyncio
import re
from typing import Any, Callable

import asyncio_mqtt as aiomqtt

from ._logging import logger
from ._tasks import background_tasks


class AbstractDeviceInterface:
    """A base class for all the device interfaces"""

    device_type: str = "UNDEFINED"

    def __init__(self, mac_address: str, device_address: str, mqtt_client: aiomqtt.Client) -> None:
        assert self.device_type != "UNDEFINED", (
            f"Incomplete interface implementation for class '{self.__class__.__name__}': "
            "'device_type' class field must be overriden in inheriting class."
        )

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
        data_decoded = data.decode("ascii").strip()
        logger.debug(f"Received a new heartbeat for device {self.dev_id}: {data_decoded}")
        self.is_connected = True

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
