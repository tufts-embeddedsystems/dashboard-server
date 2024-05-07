import paho.mqtt.publish as publish
import time

MQTT_BROKER = "en1-pi.eecs.tufts.edu"

now = int(time.time())

publish.single("teamA/node0/tempupdate", f"{now},26.2,89.4", hostname=MQTT_BROKER)

publish.single("teamA/node0/properties", '{"name":"NODE ZERO", "location":"Behind the SEC?"}', hostname=MQTT_BROKER)

# 
#publish.single("teamA/node0/properties", "(THIS WOULD BE JSON IF WE WERE DOING THIS RIGHT.)", hostname=MQTT_BROKER)

#publish.single("teamA/node0/firmware", "1234", hostname=MQTT_BROKER)
