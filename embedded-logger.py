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

  student = topicbits[0]
  subtopic = "/".join(topicbits[2:]) # Put the rest back together

  # Timestamp when MQTT message was received
  rxtime = int(time.time())

  try:
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO messages VALUES (?,?,?,?)", (rxtime, student, subtopic, message.payload.decode()))
    conn.commit()
    conn.close()
  except Exception as e:
    print("Error unpacking payload / inserting into sqlite database")
    print(f"  {message.topic} : {message.payload}")
    print(f"  {e}")


def on_connect(client, userdata, flags, reason_code, properties):
  # Subscribe to and record everything with hw5 as part of the topic
  client.subscribe("+/hw5/#")
  client.message_callback_add("+/hw5/#", save_message)

  # Ignore everything else!

if __name__ == "__main__":
  client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
  client.on_connect = on_connect

  client.connect(MQTT_BROKER)
  print("Connected.")
  
  client.loop_forever()

