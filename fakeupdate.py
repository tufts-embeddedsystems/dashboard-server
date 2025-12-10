import paho.mqtt.publish as publish
import json
import random
import time

MQTT_BROKER = "bell-mqtt.eecs.tufts.edu"

now = int(time.time())
temp = round(25 + 3 * random.random(), 1) # Fake indoor temperature, fabricated to 0.1 C

update = {"measurements": [ [now, temp] ],
          "board_time": now,
          "heartbeat": {
              "status":0,
              "rssi":-30,
              "battery_percent":100.0
            }
          }

publish.single("teamX/node0/update", json.dumps(update), hostname=MQTT_BROKER)


