# Initialize the sqlite database
# You'll need to run this once when setting up the application locally
sqlite3 data.db "CREATE TABLE messages (timestamp INTEGER, student TEXT, subtopic TEXT, message TEXT)"

