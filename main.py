from flask import Flask, render_template, request, session, redirect, url_for, flash, make_response
import time
import sqlite3

dbFile = 'data.db'

app = Flask(__name__)
app.config.from_envvar("DASHBOARD_CONFIG")

def time2str(epochtime):
  """ Return a string in local time, or "stale" if invalid. """
  if epochtime == 0:
    return "(unknown)"
  else:
    return time.strftime("%A, %m/%d %I:%M%p", time.localtime(epochtime))

# Main page
# Show a list of all students, with most recent temperature reading and a link to their sub-page
@app.route('/')
def index():
  ids = app.config['STUDENT_IDS']

  conn = sqlite3.connect(dbFile)
  c = conn.cursor()
  students = {utln: {"temperature":None, "lastseen":None} for utln in ids}

  for s in ids:
    # Last seen: get the most recent message on this topic
    result = c.execute("SELECT * FROM messages WHERE student = ? ORDER BY timestamp DESC LIMIT 1", (s,)).fetchone()
    if result is not None:
      students[s]["lastseen"] = time2str(result[0])
    # Otherwise leave as None
    
    # Current temperature
    result = c.execute("SELECT * FROM messages WHERE student = ? AND subtopic = 'ic_temp' ORDER BY timestamp DESC LIMIT 1", (s,)).fetchone()
    if result is not None:
      students[s]["temperature"] = result[3]
    # Otherwise leave as None
 
  conn.close()

  return render_template('index.html', students = students)

 
@app.route('/data/<student>/<subtopic>')
def data(student, subtopic):
  # Return a CSV file with the appropriate data
  conn = sqlite3.connect(dbFile)
  c = conn.cursor()

  result = c.execute('SELECT timestamp,message FROM messages WHERE student = ? AND subtopic = ? ORDER BY timestamp', (student, subtopic,))
  headers = "timestamp,value\n"
  blob = "\n".join(["{},{}".format(r[0], r[1]) for r in result])

  response = make_response(headers + blob)
  #response.headers['Content-Type'] = 'text/plain'
  response.headers['Content-Type'] = 'text/csv'
  #response.headers['Content-Disposition'] = 'attachment; filename={}.csv'.format(subtopic)
  return response

@app.route('/status/<student>')
def node(student):
  # Just grab the latest payload on every topic
  # The JS code on the page is going to request the temperature sensor readings separately
  conn = sqlite3.connect(dbFile)
  c = conn.cursor()

  # TODO: error handling if student isn't valid

  # Note: this use of a "bare column" select is a sqlite-specific feature
  result = c.execute("SELECT max(timestamp),subtopic,message FROM messages WHERE student = ?  GROUP BY subtopic", (student,))
  lastreport = [{"timestamp":time2str(r[0]), "subtopic":r[1], "message":r[2]} for r in result]

  return render_template('node.html', lastreport = lastreport, student = student)

 
# @app.route('/time')
# def time():
#   return time.localtime()


