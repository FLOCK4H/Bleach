# Bleach v1.5

Software for ESP32 with LCD 2x16 screen written in MicroPython

Bleach is designed as a pentesting device, and its setup requires substantial knowledge; 

`therefore, this project is not suitable for beginners`

## Real advantages
- Create captive portals (choose from 4 templates)
- Flood nearby WiFi environment with Beacon Frames
- Spoof BLE advertisement data to confuse or crash various devices
- Spoof ESP as other popular device
- BLE Keyboard, Mouse and Joystick Payload Injection (aka BLE Rubber Ducky)
- WiFi Packet fuzzer with burst technique
- Flood WiFi devices with Fake Access Points
- Scan for BSSID/ESSID of nearby WiFi and Bluetooth networks
- Play Starships
- Open-Source code:)

# Setup

Before we get started, here's what is necessary:
- ESP32 Devkit v1 WiFi+BT (https://botland.store/esp32-wifi-and-bt-modules/8893-esp32-wifi-bt-42-platform-with-module-5904422337438.html)
- LCD display 2x16 + I2C LCM1602 converter (https://botland.store/alphanumeric-and-graphic-displays/2351-lcd-display-2x16-characters-blue-i2c-lcm1602-5904422309244.html)
- Rotation Sensor Waveshare 9533 (https://botland.store/encoders/4483-rotation-sensor-encoder-with-button-module-waveshare-9533-5904422366582.html)
- 9 female-to-female jumper wires (2 black or GND, 2 red or VNC, 5 data (any color, e.g. purple))
- USB to Micro USB data cable
- Any power source
- Small box or a breadboard that can fit the components 

## Easy - This setup allows for BLE/Captive Portal attacks (wifi.send_raw_packet not accessible)
```
  $ git clone https://github.com/FLOCK4H/Bleach.git
```
1. Flash the MicroPython firmware onto the ESP32
2. Upload project files to the ESP
3. Disconnect ESP from the device in order to safely connect modules
4. Connect LCD to ESP32:
  - SCL: GPIO22
  - SDA: GPIO21
  - VCC: 5V
5. Connect rotary sensor:
  - SIA: GPIO4
  - SIB: GPIO5
  - SW: GPIO2
  - VCC: 3.3V
  * Do not forget to connect GND cables to both components:)
6. Plug the ESP to the power source
7. Take a screwdriver or any thin object and tweak the potentiometer on the back of the LCD screen until the text will be clear to read
8. By this time you should be fine to go, just without some WiFi features

## Advanced
1. Follow this process to the point where you have esp-idf and MicroPython repos: https://github.com/micropython/micropython/blob/master/ports/esp32/README.md
2. Inside the folder micropython/ports/esp32/ modify the file network_wlan.c

For the sake of educational purposes I'm only going to tell what declaration you will need to include:
```
esp_err_t esp_wifi_80211_tx(wifi_interface_t ifx, const void *buffer, int len, bool en_sys_seq);
```
3. Bind to MicroPython under name of `send_raw_packet`
4. Go back to the guide, build and flash the firmware onto the ESP
5. Upload project files to the ESP
6. Disconnect ESP from the device in order to safely connect modules
7. Connect LCD to ESP32:
  - SCL: GPIO22
  - SDA: GPIO21
  - VCC: 5V
8. Connect rotary sensor:
  - SIA: GPIO4
  - SIB: GPIO5
  - SW: GPIO2
  - VCC: 3.3V
  - Do not forget to connect GND cables to both components:)
9. Plug the ESP to the power source
10. Take a screwdriver or any thin object and tweak the potentiometer on the back of the LCD screen until the text will be clear to read
11. You are fully geared up

# Final Product
- Simple example made out of a carton box and a black tape
  
![IMG_2124](https://github.com/FLOCK4H/Bleach/assets/161654571/88caaca3-686a-4812-a5bf-5978b77bae0d)
![IMG_2127](https://github.com/FLOCK4H/Bleach/assets/161654571/6835bca4-46f2-4507-a989-9e3f6aa7f939)
![IMG_2128](https://github.com/FLOCK4H/Bleach/assets/161654571/593af1a3-dc4b-4f98-ba76-c1300977a2ea)


# DISCLAIMER & LEGAL NOTICE

The author is not responsible for any illegal, unauthorized or unethical use of the device, software or firmware provided. Always ensure you have the legal rights and authorization for using such tools. Misuse of Bleach may result in legal consequences; users are expected to comply with all applicable regulations and standards.

---

