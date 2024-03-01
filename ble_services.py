#
#    Credits to https://github.com/Heerkog/MicroPythonBLEHID/blob/master/hid_services.py
#

import struct
import bluetooth
from bluetooth import UUID
from micropython import const
import time
import gc
_ADV_TYPE_FLAGS = const(0x01)
_ADV_TYPE_NAME = const(0x09)
_ADV_TYPE_UUID16_COMPLETE = const(0x3)
_ADV_TYPE_UUID32_COMPLETE = const(0x5)
_ADV_TYPE_UUID128_COMPLETE = const(0x7)
_ADV_TYPE_UUID16_MORE = const(0x2)
_ADV_TYPE_UUID32_MORE = const(0x4)
_ADV_TYPE_UUID128_MORE = const(0x6)
_ADV_TYPE_APPEARANCE = const(0x19)

class Advertiser:
    # Generate a payload to be passed to gap_advertise(adv_data=...).
    def advertising_payload(self, limited_disc=False, br_edr=False, name=None, services=None, appearance=0):
        payload = bytearray()

        def _append(adv_type, value):
            nonlocal payload
            payload += struct.pack("BB", len(value) + 1, adv_type) + value

        _append(
            _ADV_TYPE_FLAGS,
            struct.pack("B", (0x01 if limited_disc else 0x02) + (0x18 if br_edr else 0x04)),
        )

        if name:
            _append(_ADV_TYPE_NAME, name)

        if services:
            for uuid in services:
                b = bytes(uuid)
                if len(b) == 2:
                    _append(_ADV_TYPE_UUID16_COMPLETE, b)
                elif len(b) == 4:
                    _append(_ADV_TYPE_UUID32_COMPLETE, b)
                elif len(b) == 16:
                    _append(_ADV_TYPE_UUID128_COMPLETE, b)

        # See org.bluetooth.characteristic.gap.appearance.xml
        if appearance:
            _append(_ADV_TYPE_APPEARANCE, struct.pack("<h", appearance))

        return payload


    def decode_field(self, payload, adv_type):
        i = 0
        result = []
        while i + 1 < len(payload):
            if payload[i + 1] == adv_type:
                result.append(payload[i + 2 : i + payload[i] + 1])
            i += 1 + payload[i]
        return result


    def decode_name(self, payload):
        n = self.decode_field(payload, _ADV_TYPE_NAME)
        return str(n[0], "utf-8") if n else ""


    def decode_services(self, payload):
        services = []
        for u in self.decode_field(payload, _ADV_TYPE_UUID16_COMPLETE):
            services.append(bluetooth.UUID(struct.unpack("<h", u)[0]))
        for u in self.decode_field(payload, _ADV_TYPE_UUID32_COMPLETE):
            services.append(bluetooth.UUID(struct.unpack("<d", u)[0]))
        for u in self.decode_field(payload, _ADV_TYPE_UUID128_COMPLETE):
            services.append(bluetooth.UUID(u))
        return services

    # (960 = generic HID appearance value)
    def __init__(self, services=[UUID(0x1809)], appearance=const(768), name="hell0 w0rld"):
        self._ble = bluetooth.BLE()
        self._ble.active(True)

        print("Server started")
        self._payload = self.advertising_payload(name=name, services=services, appearance=appearance)

        self.advertising = False
        print("Advertiser created: ", self.decode_name(self._payload), " with services: ", self.decode_services(self._payload))

    # Start advertising at 100000 interval
    def start_advertising(self):
        if not self.advertising:
            self._ble.gap_advertise(100000, adv_data=self._payload)
            print("Started advertising")

    # Stop advertising by setting interval of 0
    def stop_advertising(self):
        if self.advertising:
            self._ble.gap_advertise(0, adv_data=self._payload)
            print("Stopped advertising")
            
"""
    iOS so smart it will see "MPY ESP32" instead of a custom name 
    - UPDATE: in iOS 17.3.1 not appearing at all probably because of 
    the new exploit that led people to connect 
    to other's iphones and execute payloads via BLE keyboard,
    use this on Android device instead
"""

advertise_payloads=[
    (UUID(0x1804), const(961),"temp/mimikatz.ps1"),
    (UUID(0x1812), const(964), "not game pad.."),
    (UUID(0x1812), const(960), "connect ur mom.."),
    (UUID(0x1812), const(960), "hackmeifyoucan"),
    (UUID(0x180F), const(961), "stealmydata"),
    (UUID(0x1809), const(962), "notavirus.exe"),
    (UUID(0x180D), const(963), "yourpcismine"),
    (UUID(0x180A), const(964), "sneakykeyboard"),
    (UUID(0x1810), const(965), "click4malware"),
    (UUID(0x1811), const(966), "freewifi(not)"),
    (UUID(0x1804), const(967), "spywareinside"),
    (UUID(0x1805), const(968), "evilmouse"),
    (UUID(0x1806), const(640), "iamwatchingu"),
    (UUID(0x1807), const(320), "gotcha"),
    (UUID(0x1808), const(448), "gimmeyourdata"),
    (UUID(0x1813), const(512), "tagged"),
    (UUID(0x1814), const(576), "keylogger"),
    (UUID(0x1815), const(640), "phisherman"),
    (UUID(0x1816), const(704), "scan4trouble"),
    (UUID(0x1818), const(768), "hotspot_trap"),
    (UUID(0x1819), const(832), "heartr8der"),
    (UUID(0x181A), const(896), "bp_monitor"),
    (UUID(0x181B), const(960), "trojanhorse"),
    (UUID(0x1800), const(64), "apple airwacks3"),
    (UUID(0x1801), const(128), "samsung failaxy"),
    (UUID(0x1802), const(192), "notarolex"),
    (UUID(0x1803), const(256), "googly home"),
    (UUID(0x1804), const(320), "amazoff echo"),
    (UUID(0x1805), const(384), "lg life's bad"),
    (UUID(0x1806), const(448), "fitbutt versa"),
    (UUID(0x1807), const(512), "huaweii spylite"),
    (UUID(0x1808), const(576), "sonny playless"),
    (UUID(0x1809), const(640), "microsoft surf"),
    (UUID(0x1812), const(960), "plz connect :)")
]

def _start():
    for pld, cst, nm in advertise_payloads:
        adv = Advertiser(services=[pld], appearance=cst, name=nm)
        adv.start_advertising()
        time.sleep(8)
        adv.stop_advertising()
    
def advertise_spoofer(name, callback=None):
    adv = Advertiser(name=name)
    adv.start_advertising()
    


