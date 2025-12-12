from flask import Flask, render_template, request, session, redirect, url_for, flash, make_response
import time
import sqlite3
import json

dbFile = 'data.db'

app = Flask(__name__)

def time2str(epochtime):
  """ Return a string in local time, or "stale" if invalid. """
  if epochtime == 0:
    return "(unknown)"
  else:
    return time.strftime("%a, %m/%d %I:%M%p", time.localtime(epochtime))

# Main page
# Show all of the devices with their hostname / IP address
@app.route('/')
def index():

  conn = sqlite3.connect(dbFile)
  c = conn.cursor()

  # Get all of the teams represented in the database
  #result = c.execute("SELECT DISTINCT team FROM heartbeats")
  #teams = [r[0] for r in result]

  # Or just hard-code the teams, which saves a query
  teams = ["teamK", "teamL", "teamM", "teamN", "teamO", "teamP", "teamQ", "teamR", "teamX"]
  nodes = {}

  now = int(time.time())

  # Get the list of nodes for each team
  for t in teams:
    nodes[t] = {}
    result = c.execute("SELECT DISTINCT nodeid FROM heartbeats WHERE team IS ?", (t,))
    nodeids = [n[0] for n in result]

    # Get the most recent heartbeat from each node
    for n in nodeids:
      result = c.execute("SELECT * FROM heartbeats WHERE team IS ? AND nodeid IS ? ORDER BY timestamp DESC LIMIT 1", (t, n))
      heartbeat = result.fetchone()

      result = c.execute("SELECT sensortemp FROM measurements WHERE team IS ? AND nodeid IS ? ORDER BY timestamp DESC LIMIT 1", (t, n))
      temp = result.fetchone()

      # If a node has published a heartbeat but never a temperature update, the
      # query will return None
      if temp is None:
        temp = ("N/A",)

      nodes[t][n] = {
        "timestamp": time2str(heartbeat[0]),
        "timestamp-age": now - heartbeat[0],
        "status": heartbeat[4],
        "rssi": heartbeat[6],
        "battery": heartbeat[5],
        "temp": temp[0]
      }

  conn.close()

  return render_template('index.html', nodes = nodes)


@app.route('/status/<team>/<nodeid>')
def status(team, nodeid):
  # Just grab the latest payload on every topic
  # The JS code on the page is going to request the temperature sensor readings separately
  conn = sqlite3.connect(dbFile)
  c = conn.cursor()

  # TODO: error handling if team/node isn't valid

  result = c.execute("SELECT timestamp, fulltext FROM heartbeats WHERE team IS ? AND nodeid IS ? ORDER BY timestamp DESC LIMIT 1", (team, nodeid))
  heartbeat = result.fetchone()

  try:
    lastreport = json.loads(heartbeat[1])
    timestamp = time2str(heartbeat[0])
  except Exception as e:
    lastreport = {}
    timestamp = ""

  return render_template('node.html', lastreport = lastreport, timestamp = timestamp, team = team, nodeid = nodeid)


@app.route('/data/<team>/<nodeid>')
def data(team, nodeid):
  conn = sqlite3.connect(dbFile)
  c = conn.cursor()
  result = c.execute("SELECT * FROM measurements WHERE team IS ? AND nodeid IS ? ORDER BY timestamp", (team, nodeid))

  headers = "timestamp,temp\n"
  blob = "\n".join(["{},{}".format(r[1], r[4]) for r in result])

  conn.close()

  response = make_response(headers + blob)
  #response.headers['Content-Type'] = 'text/plain'
  response.headers['Content-Type'] = 'text/csv'
  return response

@app.route('/time')
def localtime():
  return time.localtime()

@app.route('/errorlog')
def errorlog():
  with open("errors.log", "r") as errorlog:
    errorlog.seek(0, 2) # Jump to EOF
    fsize = errorlog.tell() # How many bytes is the file?
    errorlog.seek(max(fsize-5000, 0), 0) # Jump back a bit

    response = make_response(errorlog.read())
    response.headers["Content-Type"] = "text"
    return response


