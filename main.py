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
  result = c.execute("SELECT DISTINCT team FROM updates")
  teams = [r[0] for r in result]

  # Or just hard-code the teams, which saves a query
  #teams = ["eccentric-egret", "floundering-flamingo"]
  nodes = {}

  # Get the list of nodes for each team
  for t in teams:
    nodes[t] = {}
    result = c.execute("SELECT DISTINCT nodeid FROM updates WHERE team IS ?", (t,))
    nodeids = [n[0] for n in result]

    # Get the most recent update from each node
    for n in nodeids:
      result = c.execute("SELECT * FROM updates WHERE team IS ? AND nodeid IS ? ORDER BY timestamp DESC LIMIT 1", (t, n))
      nodes[t][n] = result.fetchone()

  conn.close()

  return render_template('index.html', nodes = nodes)

# TODO: not sure if we need to exclude teamF from URL '/node/<team>/<nodeid>'
@app.route('/node/teamF/<nodeid>')
def node(team, nodeid):
  conn = sqlite3.connect(dbFile)
  c = conn.cursor()
  result = c.execute(
    "SELECT * FROM updates WHERE team IS ? AND nodeid IS ? ORDER BY timestamp",
    (team, nodeid)
  )

# create a json object
  jsondata = []
  for r in result:
    # Convert data into a list of dictionaries
    jsondata.append({'time': r[1], 'temp': r[4], 'battery': r[5]})
  print(f"jsondata:\n\t{jsondata}")

  conn.close()
  return render_template(
    'dashboard.html',
    data=json.dumps(jsondata),
    team=team, nodeid=nodeid,
    # also parse latest data for display
    time=time2str(jsondata[-1]['time']),
    temp=jsondata[-1]['temp'],
    battery=jsondata[-1]['battery']
  )

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


