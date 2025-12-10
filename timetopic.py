import paho.mqtt.publish as publish
import time

MQTT_BROKER = "bell-mqtt.eecs.tufts.edu"

while True:
    now = int(time.time()) # Discard fractions of a second, we're not that precise
    publish.single("time/epoch", f"{now}", hostname = MQTT_BROKER, retain = True)

    # Publish formatted time as well; this is mostly useful for debugging
    publish.single("time/local", time.strftime("%Y-%m-%d %H:%M:%S %z"), hostname = MQTT_BROKER, retain = True)
    time.sleep(60)

