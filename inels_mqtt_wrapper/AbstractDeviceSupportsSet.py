from ._logging import logger
from .AbstractDeviceInterface import AbstractDeviceInterface


class AbstractDeviceSupportsSet(AbstractDeviceInterface):
    """A base class for all the device interfaces supporting communication via the 'set' MQTT topic"""

    set_message_len_bytes: int = 0

    async def _publish_to_set_topic(self, payload: bytearray) -> None:
        """
        A method for publishing the provided payload to the device's 'set' MQTT topic.

        :param payload: A bytearray object containing the bytes to be published
        :return: None
        """
        assert self.set_message_len_bytes != 0, (
            f"Incomplete interface implementation for class '{self.__class__.__name__}': "
            "'set_message_len_bytes' class field must be overriden in inheriting class."
        )

        client = self._mqtt_client
        target_len = self.set_message_len_bytes

        if (l := len(payload)) < target_len:
            payload.extend(bytearray(0 for _ in range(target_len - l)))
        elif l > target_len:
            msg = (
                "Set message payload size exceeds the target length for interface "
                f"'{self.__class__.__name__}'. Expected {target_len} bytes, got {l} bytes instead."
            )
            raise ValueError(msg)

        payload_encoded = payload.hex(" ").upper()
        await client.publish(
            topic=self._set_topic_name,
            payload=payload_encoded,
        )
        logger.debug(f"Payload '{payload_encoded}' published to the MQTT topic {self._set_topic_name}")
