from flask import Flask, render_template, request, session, redirect, url_for, flash, make_response
import time
import sqlite3

dbFile = 'data.db'

app = Flask(__name__)

def time2str(epochtime):
  """ Return a string in local time, or "stale" if invalid. """
  if epochtime == 0:
    return "(unknown)"
  else:
    return time.strftime("%A, %m/%d %I:%M%p", time.localtime(epochtime))

# Main page
# Show all of the devices with their hostname / IP address
@app.route('/')
def index():

  conn = sqlite3.connect(dbFile)
  c = conn.cursor()

  # Get all of the teams represented in the database
  result = c.execute("SELECT DISTINCT team FROM heartbeats")
  teams = [r[0] for r in result]

  # Or just hard-code the teams, which saves a query
  #teams = ["eccentric-egret", "floundering-flamingo"]
  nodes = {}

  # Get the list of nodes for each team
  for t in teams:
    nodes[t] = {}
    result = c.execute("SELECT DISTINCT nodeid FROM heartbeats WHERE team IS ?", (t,))
    nodeids = [n[0] for n in result]

    # Get the most recent update from each node
    for n in nodeids:
      result = c.execute("SELECT * FROM heartbeats WHERE team IS ? AND nodeid IS ? ORDER BY timestamp DESC LIMIT 1", (t, n))
      nodes[t][n] = result.fetchone()

  conn.close()

  return render_template('index.html', nodes = nodes)


@app.route('/node/<team>/<nodeid>')
def node(team, nodeid):
  conn = sqlite3.connect(dbFile)
  c = conn.cursor()
  result = c.execute("SELECT * FROM updates WHERE team IS ? AND nodeid IS ? ORDER BY timestamp", (team, nodeid))
  page = "time, temp, battery<br/>"
  for r in result:
    page += f"{r[1]}, {r[4]}, {r[5]}<br/>"
 
  conn.close()
  return page

@app.route('/time')
def time():
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


