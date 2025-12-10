# Initialize the sqlite database
# You'll need to run this one when setting up the application locally
sqlite3 data.db "CREATE TABLE measurements (rxtime INTEGER, timestamp INTEGER, team TEXT, nodeid TEXT, sensortemp FLOAT)"
sqlite3 data.db "CREATE TABLE heartbeats (rxtime INTEGER, timestamp INTEGER, team TEXT, nodeid TEXT, status INTEGER, battery_percent FLOAT, rssi INTEGER, fulltext TEXT)"

