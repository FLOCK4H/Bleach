"""
    Credits to metachris
    https://github.com/metachris/micropython-captiveportal/blob/master/main.py
    
"""


import gc
import sys
import network
import socket
import ujson
import uasyncio as asyncio

SERVER_SSID = 'Free WiFi'
SERVER_IP = '10.0.0.1'
SERVER_SUBNET = '255.255.255.0'

def wifi_start_access_point():
    wifi = network.WLAN(network.AP_IF)
    wifi.active(True)
    wifi.ifconfig((SERVER_IP, SERVER_SUBNET, SERVER_IP, SERVER_IP))
    wifi.config(essid=SERVER_SSID, authmode=network.AUTH_OPEN)

def _handle_exception(loop, context):
    sys.print_exception(context["exception"])
    sys.exit()

class DNSQuery:
    def __init__(self, data):
        self.data = data
        self.domain = ''
        ini = 12
        lon = data[ini]
        while lon != 0:
            self.domain += data[ini + 1:ini + lon + 1].decode('utf-8') + '.'
            ini += lon + 1
            lon = data[ini]

    def response(self, ip):
        if self.domain:
            packet = self.data[:2] + b'\x81\x80' + self.data[4:6] + self.data[4:6] + b'\x00\x00\x00\x00' + self.data[12:]
            packet += b'\xC0\x0C' + b'\x00\x01\x00\x01\x00\x00\x00\x3C\x00\x04' + bytes(map(int, ip.split('.')))
        return packet

class MyApp:
    def __init__(self, callback=None, template=None):
        self.template = template
        self.callback = callback
        self.tasks = [] 
        self.running = True 
    async def check_callback(self):
        while True:
            if self.callback and self.callback():
                print("Callback condition met, stopping...")
                await self.stop()
                break
            await asyncio.sleep(1)

    async def stop(self):
        self.running = False
        
        await asyncio.sleep(0.1)

        # If you have tasks that don't check self.running and you still want to cancel:
        try:
            for task in self.tasks:
                task.cancel()
        except Exception as e:
            print(str(e))
        # A brief sleep to allow tasks to acknowledge cancellation
        await asyncio.sleep(0)
        # No direct loop.stop() in MicroPython, but cancelling tasks should suffice

    async def start(self):
        loop = asyncio.get_event_loop()


        loop.set_exception_handler(_handle_exception)

        wifi_start_access_point()

        server = loop.create_task(asyncio.start_server(self.handle_http_connection, "0.0.0.0", 80))
        self.tasks.append(server)

        dns_task = loop.create_task(self.run_dns_server())
        self.tasks.append(dns_task)

        callback_task = loop.create_task(self.check_callback())
        self.tasks.append(callback_task)

        while self.running:
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break

    async def handle_http_connection(self, reader, writer):
        gc.collect()
        
        request_line = await reader.readline()
        method, path, _ = request_line.decode().strip().split(' ')
        print(method, path)
        
        content_length = 0
        while True:
            line = await reader.readline()
            if line.lower().startswith(b'content-length'):
                content_length = int(line.decode().strip().split(' ')[1])
            if line == b'\r\n':
                break

        body = await reader.read(content_length) if content_length > 0 else b''
        
        if path == '/device-info' and method == 'POST':
            gc.collect()
            print("Received device info!")
            device_info = ujson.loads(body)
            print(device_info)
            gc.collect()

            response_body = ujson.dumps({'status': 'success'})
            headers = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            "Access-Control-Allow-Origin: *\r\n"
            "Access-Control-Allow-Methods: POST, GET, OPTIONS\r\n"
            "Access-Control-Allow-Headers: Content-Type\r\n\r\n"
            )
            await writer.awrite(headers + response_body)

        elif method == 'OPTIONS':
            gc.collect()
            # Handle preflight CORS request
            headers = (
                "HTTP/1.1 204 No Content\r\n"
                "Access-Control-Allow-Origin: *\r\n"
                "Access-Control-Allow-Methods: POST, GET, OPTIONS\r\n"
                "Access-Control-Allow-Headers: Content-Type\r\n\r\n"
            )
            await writer.awrite(headers)
        else:
            # Serve the captive portal page or other content for GET requests or other paths
            gc.collect()
            response = 'HTTP/1.0 200 OK\r\n\r\n'
            print("Serving html...")
            await writer.awrite(response)
            if self.template:
                nTemplate = f"{self.template}.html"
                with open(nTemplate, 'rb') as f:
                    chunk = f.read(1024)
                    while chunk:
                        await writer.awrite(chunk)
                        chunk = f.read(1024)
        
        await writer.aclose()
    
    async def run_dns_server(self):
        udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udps.setblocking(False)
        udps.bind(('0.0.0.0', 53))

        while True:
            try:

                yield asyncio.core._io_queue.queue_read(udps)

                data, addr = udps.recvfrom(4096)

                DNS = DNSQuery(data)
                udps.sendto(DNS.response(SERVER_IP), addr)

            except Exception as e:
                await asyncio.sleep_ms(3000)

        udps.close()

def run_me(callback=None, template=None):
    try:
        myapp = MyApp(callback=callback, template=template)
        asyncio.run(myapp.start())

    except KeyboardInterrupt:
        print('Bye')
    finally:
        asyncio.new_event_loop()  # Clear retained state

