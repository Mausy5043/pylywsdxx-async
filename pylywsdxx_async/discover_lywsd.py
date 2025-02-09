#!/usr/bin/env python3

"""Discover LYWSDxx devices and display them on the console."""

import asyncio

from bleak import BleakScanner


async def discover() -> None:
    """Discover LYWSDxx devices and display them on the console."""
    async with BleakScanner() as scanner:
        device_list = await scanner.discover(timeout=60)
        for device in device_list:
            if "LYWS" in str(device):
                print(f"Address: {device.address} - Name: {device.name}.")
            else:
                print(f"-------  Name: {device.name}.")

def main():
    print("Scanning for LYWSDxx devices...(max 60s)")
    asyncio.run(discover())

if __name__ == "__main__":
    main()
