#!/usr/bin/env python3

# pylywsdxx-async
# Copyright (C) 2025  Maurice (mausy5043) Hendrix
# AGPL-3.0-or-later  - see LICENSE

import asyncio
import os
import platform
import sys

# fmt:off
# add the path to the package in order to import it
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pylywsdxx_async.device_async import Lywsd03  # noqa: E402

# fmt: on


# room 1.1
MAC_ADDRESS_OR_UUID = ""
if platform.system() == "Windows":
    MAC_ADDRESS_OR_UUID = "A4:C1:38:6F:E7:CA"
if platform.system() == "Darwin":
    MAC_ADDRESS_OR_UUID = "A05DCB20-0769-C0EB-BD4D-13A26C847B4A"
if platform.system() == "Linux":
    MAC_ADDRESS_OR_UUID = "A4:C1:38:6F:E7:CA"


async def main(address) -> None:
    async with Lywsd03(address, notification_timeout=60) as client:
        lywsd03mmc_data = await client.get_data()
        print(lywsd03mmc_data)


asyncio.run(main(MAC_ADDRESS_OR_UUID))
