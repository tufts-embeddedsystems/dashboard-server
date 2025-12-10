# Log MQTT messages from the broker to an SQLite database file
import time
import sqlite3
import paho.mqtt.client as mqtt
import json

MQTT_BROKER = "bell-mqtt.eecs.tufts.edu"
DATABASE_FILE = "data.db"
LOG_FILE = "errors.log" # This can be read by students so they can see their errors

def log_error(msg):
  try:
    log = open(LOG_FILE, "a")
    log.write(f"{time.asctime()}: {msg}\n\n")
    log.close()
  except Exception as e:
    print(f"Failed to write to error log: {e}")
    print(f"Original message was:\n{msg}")

def save_message(client, userdata, message):
  topicbits = message.topic.split('/')
  if len(topicbits) != 3:
    # This should not happen if we're subscribed to the right things
    log_error(f"Unexpected topic: {message.topic}")
    return

  team = topicbits[0]
  nodeid = topicbits[1]
  updatetype = topicbits[2]

  # Timestamp when MQTT message was received
  rxtime = int(time.time())

  try:
    payload_string = message.payload.decode()
  except Exception as e:
    log_error(f"Error decoding payload as character string {e}")
    log_error(f"Problem message was {message.topic}: {message.payload}")

  try:
    payload = json.loads(payload_string)
  except json.JSONDecodeError as e:
    log_error(f"Error decoding payload as JSON: {e}\n\npayload was {payload_string}")
    return # If we can't get the JSON out, we're toast!

  board_time = payload.get("board_time", rxtime)

  if "measurements" in payload:
    pass
  

  if "heartbeat" in payload:
    heartbeat = payload["heartbeat"]
    if "status" in heartbeat:
      try:
        status = int(heartbeat["status"]) # status is required for heartbeat to be valid
        battery_percent = float(heartbeat.get("battery_percent", -1)) # battery_percent is optional but supported by dashboard
        rssi = int(heartbeat.get("rssi", 0)) # rssi is optional but supported by dashboard
        # everything else is optional and not supported, so we'll save the whole thing

        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO heartbeats VALUES (?,?,?,?,?,?,?,?)", \
          (rxtime, board_time, team, nodeid, status, battery_percent, rssi, json.dumps(heartbeat)))
        conn.commit()
        conn.close()

      except ValueError as e:
        log_error(f"Error converting values to numbers: {e}")
        log_error(f"Problem message was {message.topic}: {payload}\n")
      # TODO: sqlite error, maybe try again?
      except Exception as e:
        log_error(f"Failed to save message: {e}")
        log_error(f"Problem message was {message.topic}: {payload}\n")

  
def on_connect(client, userdata, flags, reason_code): # Add properties arg for 2.x
  # Subscribe to and record all of the tempupdates
  client.subscribe('+/+/update')
  client.on_message = save_message


if __name__ == "__main__":
  client = mqtt.Client() # Use version 1.x for now
  #client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

  client.on_connect = on_connect
  client.connect(MQTT_BROKER)
  print("Connected.")
  
  client.loop_forever()

