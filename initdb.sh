# Initialize the sqlite database
# You'll need to run this one when setting up the application locally
sqlite3 data.db "CREATE TABLE messages (rxtime INTEGER, timestamp INTEGER, team TEXT, nodeid TEXT, sensortemp INTEGER, thermistortemp INTEGER, battery INTEGER, teamdata BLOB)"

