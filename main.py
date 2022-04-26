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
  result = c.execute("SELECT DISTINCT team FROM messages")
  teams = [r[0] for r in result]

  # Or just hard-code the teams, which saves a query
  #teams = ["eccentric-egret", "floundering-flamingo"]
  nodes = {}

  # Get the list of nodes for each team
  for t in teams:
    nodes[t] = {}
    result = c.execute("SELECT DISTINCT nodeid FROM messages WHERE team IS ? ORDER BY timestamp", (t,))
    nodeids = [n[0] for n in result]

    # Get the most recent update from each node
    for n in nodeids:
      result = c.execute("SELECT * FROM messages WHERE team IS ? AND nodeid IS ? ORDER BY timestamp LIMIT 1", (t, n))
      nodes[t][n] = result.fetchone()

  conn.close()

  return render_template('index.html', nodes = nodes)


@app.route('/node/<team>/<nodeid>')
def node(team, nodeid):
  conn = sqlite3.connect(dbFile)
  c = conn.cursor()
  result = c.execute("SELECT * FROM messages WHERE team IS ? AND nodeid IS ? ORDER BY timestamp", (team, nodeid))
  page = "time, temp1, temp2, battery, data<br/>"
  for r in result:
    page += f"{r[0]}, {r[4]}, {r[5]}, {r[6]}, {r[7]}<br/>"
 
  conn.close()
  return page

@app.route('/time')
def time():
  return time.localtime()


