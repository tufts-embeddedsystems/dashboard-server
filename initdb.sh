# Initialize the sqlite database
# You'll need to run this one when setting up the application locally
sqlite3 data.db "CREATE TABLE updates (rxtime INTEGER, timestamp INTEGER, team TEXT, nodeid TEXT, sensortemp FLOAT, battery FLOAT)"
sqlite3 data.db "CREATE TABLE properties (rxtime INTEGER, team TEXT, nodeid TEXT, blob TEXT)"

