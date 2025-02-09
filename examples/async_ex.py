#!/usr/bin/env python3

import asyncio
import platform
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pylywsdxx_async.lywsd03mmc_client import Lywsd03mmcClient

# room 1.1
if platform.system() == "Darwin":
    MAC_ADDRESS_OR_UUID = "A05DCB20-0769-C0EB-BD4D-13A26C847B4A"
if platform.system() == "Linux":
    MAC_ADDRESS_OR_UUID = "A4:C1:38:6F:E7:CA"

async def main(address) -> None:
    async with Lywsd03mmcClient(address, timeout=60) as client:
        lywsd03mmc_data = await client.get_data()
        print(lywsd03mmc_data)


asyncio.run(main(MAC_ADDRESS_OR_UUID))
