#!/usr/bin/env python3

# pylywsdxx-async
# Copyright (C) 2025  Maurice (mausy5043) Hendrix
# AGPL-3.0-or-later  - see LICENSE

import os
import platform
import sys

# fmt:off
# add the path to the package in order to import it
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pylywsdxx_async as pyly  # noqa: E402

MAC_ADDRESS_OR_UUID = ""
if platform.system() == "Windows":
    MAC_ADDRESS_OR_UUID = "A4:C1:38:6F:E7:CA"
if platform.system() == "Darwin":
    MAC_ADDRESS_OR_UUID = "A05DCB20-0769-C0EB-BD4D-13A26C847B4A"
if platform.system() == "Linux":
    MAC_ADDRESS_OR_UUID = "A4:C1:38:6F:E7:CA"


def main(address) -> None:
    with pyly.PyLyManager(debug=True) as pylyman:
        pylyman.subscribe_to(mac=address, dev_id="test", version=2)
        pylyman.update_all()
        # dct = pylyman.get_state_of("test")
        # print(dct)


if MAC_ADDRESS_OR_UUID:
    main(MAC_ADDRESS_OR_UUID)
