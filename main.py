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


@app.route('/status/<team>/<nodeid>')
def status(team, nodeid):
  # Just grab the latest payload on every topic
  # The JS code on the page is going to request the temperature sensor readings separately
  conn = sqlite3.connect(dbFile)
  c = conn.cursor()

  # TODO: error handling if team/node isn't valid

  # Note: this use of a "bare column" select is a sqlite-specific feature
  #result = c.execute("SELECT max(timestamp),subtopic,message FROM messages WHERE student = ?  GROUP BY subtopic", (student,))
  #lastreport = [{"timestamp":time2str(r[0]), "subtopic":r[1], "message":r[2]} for r in result]

  return render_template('node.html', lastreport = {}, team = team, nodeid = nodeid)


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


