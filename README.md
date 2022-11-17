# Inels MQTT wrapper

A Python library to work with Inels smart home devices over MQTT (using Asyncio).

> **WARNING**: THIS PACKAGE IS PUBLISHED ONLY FOR TESTING AND IS NOT READY FOR PRODUCTION USE. 
> MOST OF THE FEATURES HAVE NOT RECEIVED ANY TESTING YET.

---

## Interface

The library provides a set of Python classes to interact with devices. Some devices share the same MQTT 
command interface according to the specification. All the interfaces share some common code. Thus, the following 
class hierarchy:

AbstractDeviceInterface -> AbstractDeviceSupportsStatus, AbstractDeviceSupportsSet -> DeviceInterfaceXX -> Concrete 
device class

The users are meant to work with one of the following in their code:
1. Concrete device class (e.g. RFDAC71B and others);
2. Concrete DeviceInterface (e.g. DeviceInterface05 and others).

Concrete device classes inherit from the concrete device interface implementations without any changes. Concrete device 
classes are meant to be a convenient way for a developer to find the needed implementation to work with by the name 
of the device's model. It might not always be clear which interface (device type) the device implements, so using the 
concrete device class is recommended.

> Later in this documentation both device interfaces and concrete devices will be referred to as "device classes" as 
> there is no practical difference between them.

All the device classes have a set of public methods unique to each device type for interaction with it. The public 
methods are made to be as user-friendly as possible having clear names and accepting human-readable values. Each 
method has a detailed docstring describing the method itself and each of its parameters as well as the return value. 
The library is type annotated throughout.

## Technical details

Device types, that are able to work through MQTT use 3 topics for that. The first topic is 'connected' - the device 
sends heartbeats in it. Device reads commands and settings from the 'set' topic. Topic 'status' is used by the 
device to publish its status - the measurements of the sensors, current settings, etc.

According to the specification, all the devices support the 'connected' topic. 'Status' topic is known to be 
implemented for most of the devices. Some devices lack support for the 'set' topic as it is not necessary 
since they do not accept any commands (sensors and such).

Any device class will subscribe to the 'connected' channel asynchronously and start a listener process in the 
background Immediately after it is initialized. No additional actions required. As soon as the first heartbeat is 
received - the `is_connected` field of the device class will be set to `True`. 

Same applies to the device classes, supporting the communication via the 'status' topic. The latest known status of 
the device can be accessed from the 'status' property of the device. The 'status' property holds a dictionary with  
device-specific keys. Accessing this attribute before the first status message is received will raise 
DeviceStatusUnknownError. Example of the device-specific status dict can be found in the docstring of the concrete 
implementation's `_decode_status()` method. Devices that support the 'status' topic publishing inherit from the 
'AbstractDeviceSupportsStatus' base class. `await_state_change` async method is also provided to wait for a status 
update with a timeout. Returns `True` if the state changes within the set timeout or `False` if the timeout occurs 
earlier.

Finally, device classes, that support the communication via the 'set' MQTT topic provide public methods to send 
commands and settings to the device. All such device classes inherit from the 'AbstractDeviceSupportsSet' base class 
or from both 'AbstractDeviceSupportsSet' and  'AbstractDeviceSupportsStatus' if they support all three MQTT topics.

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
        await asyncio.sleep(3)  # Wait for 3 seconds
        await device.toggle_switch()  # Switch off the device

        try:
            print(device.status)  # Check the device status again
        except DeviceStatusUnknownError as e:
            print(e)  # Print the error if the device status is unknown


if __name__ == "__main__":
    asyncio.run(main())
```

## Contribution

Create issues in this repository if there are any problems with this app or if you want to communicate a feature 
request. Fork this repository and file a pull request to contribute to the app development.

This project complies with the code formatting guidelines defined in the provided .pre-commit-config.yaml file.

This repository uses semantic versioning and conventional commits to describe its updates.
