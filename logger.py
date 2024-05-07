# Log MQTT messages from the broker to an SQLite database file
import time
import sqlite3
import paho.mqtt.client as mqtt
import json

MQTT_BROKER = "en1-pi.eecs.tufts.edu"
DATABASE_FILE = "data.db"

def save_message(client, userdata, message):

  topicbits = message.topic.split('/')
  if len(topicbits) != 3:
    # This should not happen if we're subscribed to the right things
    print(f"Unexpected topic: {message.topic}")
    return

  team = topicbits[0]
  nodeid = topicbits[1]
  updatetype = topicbits[2]

  # Timestamp when MQTT message was received
  rxtime = int(time.time())

  try:
    payload = message.payload.decode()
  except Exception as e:
      print(f"Error decoding payload as character string {e}")
      print(f"Problem message was {message.topic}: {payload}\n")

  if updatetype == "tempupdate":
    updatebits = payload.split(',')
    if len(updatebits) != 3:
      print(f"Invalid update (expected three columns)! {message.topic}: {payload}")
      return

    try:
      timestamp = int(updatebits[0])
      temp = float(updatebits[1])
      battery = float(updatebits[2])

      print(f"{team}/{nodeid}  time: {timestamp}, temp: {temp}, batt: {battery}")
      conn = sqlite3.connect(DATABASE_FILE)
      c = conn.cursor()
      c.execute("INSERT INTO updates VALUES (?,?,?,?,?,?)", \
          (rxtime, timestamp, team, nodeid, temp, battery))
      conn.commit()
      conn.close()

    except ValueError as e:
      print(f"Error converting values to numbers: {e}")
      print(f"Problem message was {message.topic}: {payload}\n")
    except Exception as e:
      print(f"Uh, oh: {e}")
      print(f"Problem message was {message.topic}: {payload}\n")


  elif updatetype == "properties":
    try:
      # Validate JSON, but we'll just insert the original text
      json.loads(payload)

      print(f"{team}/{nodeid}  properties: {payload}")

      conn = sqlite3.connect(DATABASE_FILE)
      c = conn.cursor()
      c.execute("INSERT INTO properties VALUES (?,?,?,?)", (rxtime, team, nodeid, payload))
      conn.commit()
      conn.close()

    except json.JSONDecodeError as e:
      print(f"JSON validation failed: {e}")
      print(f"Problem message was {message.topic}: {payload}\n")
    except Exception as e:
      print(f"Uh, oh: {e}")
      print(f"Problem message was {message.topic}: {payload}\n")


  else:
    # We shouldn't end up here unless we subscribed to the wrong thing!
    print(f"Ignoring subtopic {updatetype} ({message.topic}: {payload}")

  
def on_connect(client, userdata, flags, reason_code, properties):
  # Subscribe to and record all of the tempupdates
  client.subscribe('+/+/tempupdate')
  client.subscribe('+/+/properties')
  client.on_message = save_message


if __name__ == "__main__":
  client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

  client.on_connect = on_connect
  client.connect(MQTT_BROKER)
  print("Connected.")
  
  client.loop_forever()

