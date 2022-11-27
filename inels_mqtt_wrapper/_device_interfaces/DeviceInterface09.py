from typing import Literal

from .._logging import logger
from ..AbstractDeviceSupportsSet import AbstractDeviceSupportsSet
from ..AbstractDeviceSupportsStatus import AbstractDeviceSupportsStatus, StatusDataType

# FIXME: The set methods currently reset some settings while setting the other.
# For now there is no documented way to obtain the current setting of the
# "Open window" feature to avoid resetting it's settings by sending the
# already applied value. Same goes for the communication interval.


class DeviceInterface09(AbstractDeviceSupportsStatus, AbstractDeviceSupportsSet):
    """A base class for all the devices implementing the 'device type 09' interface"""

    device_type: str = "09"
    status_message_len_bytes: int = 5
    set_message_len_bytes: int = 3

    @staticmethod
    def _decode_status(raw_status_data: bytearray) -> StatusDataType:  # TODO: Testing required
        """
        A method for decoding the device's status from bytes.

        :param raw_status_data: A bytearray object containing the bytes, published by the device in the topic.
        :return: A device-specific dict, containing its status. For this device:
            {
                "valve_open_state_percentage": 50,
                "temperature": 40,
                "battery_empty": False,
                "required_temperature": 50,
                "regular_traffic": ?,
            }
        """
        data_0, data_1, data_2, data_3, data_4 = raw_status_data
        return {
            "valve_open_state_percentage": data_0 * 0.5,
            "temperature": data_1 * 0.5,
            "battery_empty": data_2 == 8,
            "required_temperature": data_3 * 0.5,
            "regular_traffic": data_4,
        }

    async def set_elan_communication_interval(self, interval_sec: int = 350) -> None:  # TODO: Testing required
        """
        Set the communication interval with the eLAN gateway.

        :param interval_sec: The communication interval with the gateway
            in seconds. Must be a multiple of 70. Defaults to 350.
        :return: None
        """
        assert interval_sec >= 70, "The communication interval cannot be less than 70 seconds"
        assert interval_sec % 70 == 0 and interval_sec, "The communication interval must be a multiple of 70"
        payload = bytearray(
            [
                int(interval_sec // 70),
                self.status["required_temperature"],
                0,  # FIXME: Resets the "Open window" feature settings
            ]
        )
        await self._publish_to_set_topic(payload)
        logger.info(f"eLAN gateway communication interval set to {interval_sec}s on the device {self.dev_id}")

    async def set_required_temperature(self, required_temperature_c: float) -> None:  # TODO: Testing required
        """
        Set the desired room temperature.

        :param required_temperature_c: The desired room temperature in degrees C.
            Must be a multiple of 0.5.
        :return: None.
        """
        assert required_temperature_c > 0, "The required temperature must be more than 0"
        assert not required_temperature_c % 0.5, "The required temperature must be a multiple of 0.5"
        payload = bytearray(
            [
                0,  # FIXME: Resets the communication interval
                int(required_temperature_c // 0.5),
                0,  # FIXME: Resets the "Open window" feature settings
            ]
        )
        await self._publish_to_set_topic(payload)
        logger.info(f"Required temperature set to {required_temperature_c} C on the device {self.dev_id}")

    async def set_open_window_parameters(
        self,
        sensitivity: Literal["off", "low", "medium", "high"],
        duration_min: int,
    ) -> None:  # TODO: Testing required
        """
        Set the sensitivity of detection for the 'Open window' feature.

        :param sensitivity: The detection sensitivity level.
            The options are:
            "off" - disable the feature;
            "low" - trigger when the 1.2 degrees C temperature drop is detected;
            "medium" - trigger when the 0.8 degrees C temperature drop is detected;
            "high" - trigger when the 0.4 degrees C temperature drop is detected.
        :param duration_min: The 'Open window' feature duration in minutes.
            The duration must be a multiple of 10 between 0 and 60.
            Value 0 disables the feature.
        :return: None
        """
        duration_options = {
            0: b"000",
            10: b"001",
            20: b"010",
            30: b"011",
            40: b"100",
            50: b"101",
            60: b"110",
        }
        assert duration_min in duration_options, "'Open window' duration must be a multiple of 10 between 0 and 60"

        sensitivity_options = {
            "off": b"00",
            "low": b"01",
            "medium": b"10",
            "high": b"11",
        }
        assert (
            sensitivity in sensitivity_options
        ), f"Sensitivity parameter must equal one of the following options: {list(sensitivity_options.keys())}"

        settings = b"00" + b"0" + sensitivity_options[sensitivity] + duration_options[duration_min]
        assert len(settings) == 8

        payload = bytearray(
            [
                0,  # FIXME: Resets the communication interval
                self.status["required_temperature"],
                int(settings, 2),
            ]
        )
        await self._publish_to_set_topic(payload)
        logger.info(
            f"Open window feature parameters set to: {sensitivity=}; {duration_min=} on the device {self.dev_id}"
        )
