# Log MQTT messages from the broker to an SQLite database file
import time
import struct
import sqlite3
import paho.mqtt.client as mqtt

MQTT_BROKER = "en1-pi.eecs.tufts.edu"
DATABASE_FILE = "data.db"

def save_message(client, userdata, message):
  # Don't save retained messages since the timestamp would be meaningless
  if message.retain:
    return

  topicbits = message.topic.split('/')
  if len(topicbits) != 3:
    print(f"Unexpected topic: {message.topic}")
    return

  team = topicbits[1]
  nodeid = topicbits[2]

  # Timestamp when MQTT message was received
  rxtime = int(time.time())

  # Unpack the payload
  (timestamp, sensortemp, thermistortemp, battery) = struct.unpack_from("qiib", message.payload, 0)
  teamdata = message.payload[19:]
  
  #print(f"time: {timestamp}, temp: {sensortemp} therm: {thermistortemp}  batt: {battery}  data: {data}")

  conn = sqlite3.connect(DATABASE_FILE)
  c = conn.cursor()
  c.execute("INSERT INTO messages VALUES (?,?,?,?,?,?,?,?)", (rxtime, timestamp, team, nodeid, sensortemp, thermistortemp, battery, teamdata))
  conn.commit()
  conn.close()


def on_connect(client, userdata, flags, rc):
  # Subscribe to and record everything under nodes/
  client.subscribe('nodes/#')
  client.on_message = save_message


if __name__ == "__main__":
  client = mqtt.Client()
  client.on_connect = on_connect

  client.connect(MQTT_BROKER)
  print("Connected.")
  
  client.loop_forever()

