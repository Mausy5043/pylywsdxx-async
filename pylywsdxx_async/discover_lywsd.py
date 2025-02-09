#!/usr/bin/env python3

"""Discover LYWSDxx devices and display them on the console."""

import asyncio

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.exc import BleakDBusError


async def discover() -> None:
    """Discover LYWSDxx devices and display them on the console."""
    retry_attempts: int = 3
    for attempt in range(retry_attempts):
        try:
            device_list: list[BLEDevice] = await BleakScanner().discover(timeout=60)
            for device in device_list:
                if "LYWS" in str(device):
                    print(f"Address: {device.address} - Name: {device.name}.")
                else:
                    print(f"-------  Name: {device.name}.")
            break
        except BleakDBusError as her:
            if "InProgress" in str(her):
                print(f"Attempt {attempt + 1} failed: {her}. Retrying...")
                await asyncio.sleep(5)
            else:
                raise her


def main() -> None:
    print("Scanning for LYWSDxx devices...(max 60s)")
    asyncio.run(discover())


if __name__ == "__main__":
    main()
