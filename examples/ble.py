#!/usr/bin/env python3

import asyncio

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice


async def discover_ble_devices() -> list[BLEDevice]:
    print("Scanning for BLE devices...")
    return await BleakScanner.discover(timeout=10)


# Do have one async main function that does everything.
async def main() -> None:
    devices = await discover_ble_devices()
    for device in devices:
        # print(f"Device: {device}")
        print(f"Address: {device.address}, Device: {device.name}")
        try:
            async with BleakClient(device, timeout=5.0) as client:
                mydata = await client.services()  # type: ignore
                print(f"-->   Received: {mydata}")
        except BaseException:
            pass

asyncio.run(main())
