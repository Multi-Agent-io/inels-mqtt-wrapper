# Inels MQTT wrapper

A Python library to work with Inels smart home devices over MQTT (using Asyncio).

---

## Demo code

Below is a simple code snippet to demonstrate the basic interaction with this library.

```python
import asyncio

import asyncio_mqtt as aiomqtt

from inels_mqtt_wrapper import RFDAC71B, DeviceStatusUnknownError


async def main() -> None:
    """Entrypoint"""

    async with aiomqtt.Client("localhost") as client:
        device = RFDAC71B(
            mac_address="00:00:00:00:00:00",  # Your gateway's MAC address
            device_address="01207D",  # Your device's address (found on the device's top case)
            mqtt_client=client,  # An instance of asyncio_mqtt.Client
        )
        print("Connected:", device.is_connected)  # True

        try:
            print(device.status)  # A dict containing device-specific status data
        except DeviceStatusUnknownError as e:
            print(e)  # Print the error if the device status is unknown

        await device.set_brightness_percentage(50)  # Set the device's brightness to 50%
        await device.without_function()  # Apply the before set brightness percentage

        try:
            print(device.status)  # Check the device status again
        except DeviceStatusUnknownError as e:
            print(e)  # Print the error if the device status is unknown


if __name__ == "__main__":
    asyncio.run(main())
```
