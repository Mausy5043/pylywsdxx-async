#!/usr/bin/env python3

# pylywsdxx-async
# Copyright (C) 2025  Maurice (mausy5043) Hendrix
# AGPL-3.0-or-later  - see LICENSE

import asyncio
import logging
import struct

from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic

LOGGER: logging.Logger = logging.getLogger(__name__)


class Lywsd03mmcData:
    def __init__(self, temperature_raw: int, humidity: int, bat_volt: int):
        self._temperature_raw = temperature_raw
        self._humidity = humidity
        self._bat_volt = bat_volt

    @property
    def temperature(self):
        return self._temperature_raw / 100

    @property
    def humidity(self):
        return self._humidity

    @property
    def bat_volt(self):
        return self._bat_volt

    @property
    def bat_perc(self):
        return min(int(round((self._bat_volt / 1000 - 2.1), 2) * 100), 100)

    def __str__(self):
        return (
            f"temperature_raw:    {self._temperature_raw}, "
            + f"temperature:        {self.temperature}, "
            + f"humidity:           {self.humidity}, "
            + f"battery_vol:        {self.bat_volt}, "
            + f"battery_percentage: {self.bat_perc}"
        )


class Lywsd03mmcOneHourHistoryData:
    def __init__(
        self,
        idx_num: int,
        timestamp: int,
        temperature_raw_max: int,
        humidity_max: int,
        temperature_raw_min: int,
        humidity_min: int,
    ):
        self.idx_num = idx_num
        self.timestamp = timestamp
        self.temperature_raw_max = temperature_raw_max
        self.humidity_max = humidity_max
        self.temperature_raw_min = temperature_raw_min
        self.humidity_min = humidity_min

    @property
    def temperature_max(self):
        return self.temperature_raw_max / 10

    @property
    def temperature_min(self):
        return self.temperature_raw_min / 10

    def __str__(self):
        return (
            f"idx_num: {self.idx_num}, "
            + f"timestamp: {self.timestamp}, "
            + f"temperature_raw_max: {self.temperature_max}, "
            + f"humidity_max: {self.humidity_max}, "
            + f"temperature_raw_min: {self.temperature_min}, "
            + f"humidity_min: {self.humidity_min}"
        )


class Lywsd03:
    BYTES_TO_TEMP_UNIT = {"1": "F", "0": "C"}

    COMMON_UUID = "7A0A-4B0C-8A1A-6FF2997DA3A6"
    UUID_TIME = f"EBE0CCB7-{COMMON_UUID}"  # _      5 or 4 bytes          READ WRITE
    UUID_NUM_RECORDS = f"EBE0CCB9-{COMMON_UUID}"  # 8 bytes               READ
    UUID_RECORD_IDX = f"EBE0CCBA-{COMMON_UUID}"  # _4 bytes               READ WRITE
    UUID_RECENT = f"EBE0CCBB-{COMMON_UUID}"
    UUID_HISTORY = f"EBE0CCBC-{COMMON_UUID}"  # _   Last idx 152          READ NOTIFY
    UUID_UNITS = f"EBE0CCBE-{COMMON_UUID}"  # _     Celsius(0) or Fahrenheit(1)
    UUID_DATA = f"EBE0CCC1-{COMMON_UUID}"  # _      3 bytes               READ NOTIFY
    UUID_BATTERY = f"EBE0CCC4-{COMMON_UUID}"  # _   1 byte                READ

    def __init__(self, mac_or_uuid: str, timeout: float):
        self.mac_or_uuid = mac_or_uuid
        self.client = BleakClient(address_or_ble_device=self.mac_or_uuid, timeout=timeout)

    async def connect(self) -> bool:
        return await self.client.connect()

    async def get_data(self) -> Lywsd03mmcData:
        # returns for example (2216, 23, 3001) -> (temp, humidity, battery_voltage)
        # temp = (22.16) integral and fractional parts
        res: bytearray = await self.__get_attribute(self.UUID_DATA)
        (temp, hum, bat_volt) = struct.unpack_from("<hBh", res)
        return Lywsd03mmcData(temperature_raw=temp, humidity=hum, bat_volt=bat_volt)

    async def get_battery(self):
        res: bytearray = await self.__get_attribute(self.UUID_BATTERY)
        return struct.unpack_from("b", res)[0]

    async def get_temp_unit(self):
        res: bytearray = await self.__get_attribute(self.UUID_UNITS)
        return self.BYTES_TO_TEMP_UNIT[str(res[0])]

    async def set_celsius(self):
        await self.__write_attribute(self.UUID_UNITS, b"\x00")

    async def set_fahrenheit(self):
        await self.__write_attribute(self.UUID_UNITS, b"\x01")

    async def get_timestamp(self):
        res: bytearray = await self.__get_attribute(self.UUID_TIME)
        timestamp = struct.unpack("I", res)[0]
        return timestamp

    async def set_timestamp(self, milliseconds: int):
        data: bytes = struct.pack("I", int(milliseconds))
        await self.__write_attribute(self.UUID_TIME, data)

    async def get_first_history_idx(self):
        res: bytearray = await self.__get_attribute(self.UUID_RECORD_IDX)
        _idx = 0 if len(res) == 0 else struct.unpack_from("I", res)[0]
        return _idx

    async def set_first_history_idx(self, idx: int):
        data: bytes = struct.pack("I", int(idx))
        await self.__write_attribute(self.UUID_RECORD_IDX, data)

    async def get_last_calculated_hour_idx_and_next_idx(self) -> tuple:
        # last_calc, last_idx
        res: bytearray = await self.__get_attribute(self.UUID_NUM_RECORDS)
        return struct.unpack_from("II", res)

    async def get_history_data(self):
        records = []
        last_rec_idx = (await self.get_last_calculated_hour_idx_and_next_idx())[1]

        def callback(sender: BleakGATTCharacteristic, data_bytes: bytearray):
            data_tuple = struct.unpack_from("<IIhBhB", data_bytes)
            data = Lywsd03mmcOneHourHistoryData(
                idx_num=data_tuple[0],
                timestamp=data_tuple[1],
                temperature_raw_max=data_tuple[2],
                humidity_max=data_tuple[3],
                temperature_raw_min=data_tuple[4],
                humidity_min=data_tuple[5],
            )
            records.append(data)

        await self.client.start_notify(self.UUID_HISTORY, callback)

        await asyncio.sleep(3.0)  # to get first record
        while records[-1].idx_num < last_rec_idx - 1:
            await asyncio.sleep(1.0)
            continue
        await self.client.stop_notify(self.UUID_HISTORY)

        return records

    async def get_last_hour_data(self):
        res: bytearray = await self.__get_attribute(self.UUID_RECENT)
        data = struct.unpack_from("<IIhBhB", res)
        return Lywsd03mmcOneHourHistoryData(
            idx_num=data[0],
            timestamp=data[1],
            temperature_raw_max=data[2],
            humidity_max=data[3],
            temperature_raw_min=data[4],
            humidity_min=data[5],
        )

    async def __get_attribute(self, attribute_name: str):
        return await self.client.read_gatt_char(attribute_name)

    async def __write_attribute(self, attribute_name: str, value: bytes):
        await self.client.write_gatt_char(attribute_name, value)

    async def close(self) -> None:
        if self.client.is_connected:
            await self.client.disconnect()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
