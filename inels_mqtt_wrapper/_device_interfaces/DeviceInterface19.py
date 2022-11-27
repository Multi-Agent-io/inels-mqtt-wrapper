from ..AbstractDeviceSupportsStatus import AbstractDeviceSupportsStatus, StatusDataType
from ..utils import extract_bits


class DeviceInterface19(AbstractDeviceSupportsStatus):
    """A base class for all the devices implementing the 'device type 19' interface"""

    device_type: str = "19"
    status_message_len_bytes: int = 5

    @staticmethod
    def _decode_status(raw_status_data: bytearray) -> StatusDataType:  # TODO: Testing required
        """
        A method for decoding the device's status from bytes.

        :param raw_status_data: A bytearray object containing the bytes, published by the device in the topic.
        :return: A device-specific dict, containing its status. For this device:
            {
            "learn_mode_on": False,
            "button_state_changed": True,
            "button_is_pressed": False,
            "battery_low": False,
            "last_button_pressed": 1,
        }
        """
        data_0, data_1, data_2, data_3, data_4 = raw_status_data
        button_codes = {1: 1, 2: 2, 3: 4, 4: 8}
        bits = extract_bits(data_0, target_len=8)
        bit_7, bit_6, bit_5, bit_4, bit_3, bit_2, bit_1, bit_0 = bits
        return {
            "learn_mode_on": bool(bit_7),
            "button_state_changed": bool(bit_5),
            "button_is_pressed": bool(bit_4),
            "battery_low": bool(bit_3),
            "last_button_pressed": button_codes[data_1],
        }
