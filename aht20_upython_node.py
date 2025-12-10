# Minimal node using an AHT20 temperature sensor and Lolin S2 Pico ESP32 board,
# which reports using the class-wide standard protocol.
# This has no power-saving features and should be plugged into the wall.
# It also has no recovery features should it get disconnected from the network.

from time import sleep, time
from machine import Pin, I2C
import network
from umqttsimple import MQTTClient
import json
import ahtx0


wlan = network.WLAN(network.STA_IF)

# If the network isn't already connected, try to connect
if not wlan.isconnected():
    wlan.active(True)

    # Try to connect to Tufts_Wireless:
    ssid = "Tufts_Wireless"
    print("Connecting to {}...".format(ssid))
    wlan.connect(ssid)
    while not wlan.isconnected():
        sleep(1)
        print('.')

print("Connected!")
print("IP address:", wlan.ifconfig()[0])

# Note that this server is only accessible from the Tufts network
mqtt_server = "bell-mqtt.eecs.tufts.edu"

clientId = "esp32-sbell"

client = MQTTClient(clientId, mqtt_server)
client.connect()

i2c = I2C(1, scl=Pin(2), sda=Pin(1))
sensor = ahtx0.AHT20(i2c)


while True:
    temp = sensor.temperature
    humidity = sensor.relative_humidity
    
    print(f"\nTemperature: {temp:0.2f} C")
    print(f"Humidity: {humidity:0.2f}% RH")
    
    now = time()
    rssi = wlan.status('rssi')
    
    update = {"measurements": [[now, temp]],
              "board_time": now,
              "heartbeat": {"status": 0, "rssi": rssi, "battery_percent": 100.0, "humidity": humidity}}
    
    client.publish("teamX/node1/update", json.dumps(update))    
    sleep(5*60)
