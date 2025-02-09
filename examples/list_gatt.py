#!/usr/bin/env python3

# pylywsdxx-async
# Copyright (C) 2025  Maurice (mausy5043) Hendrix
# AGPL-3.0-or-later  - see LICENSE

import asyncio
import platform

from bleak import BleakClient

MAC_ADDRESS_OR_UUID = ""
if platform.system() == "Windows":
    MAC_ADDRESS_OR_UUID = "A4:C1:38:6F:E7:CA"
if platform.system() == "Darwin":
    MAC_ADDRESS_OR_UUID = "A05DCB20-0769-C0EB-BD4D-13A26C847B4A"
if platform.system() == "Linux":
    MAC_ADDRESS_OR_UUID = "A4:C1:38:6F:E7:CA"


async def main(address) -> None:
    async with BleakClient(address, timeout=60) as client:
        services = await client.get_services()
        for s in services:
            print(f"Service: {s}")

            for c in s.characteristics:
                print(f"\tCh: {c}")
                print(f"\t\t{c.properties}")
                for d in c.descriptors:
                    x = await client.read_gatt_descriptor(d.handle)
                    print(f"\t\t handle: {d.handle} {x}")


if MAC_ADDRESS_OR_UUID:
    asyncio.run(main(MAC_ADDRESS_OR_UUID))
