# Minimal script for testing queries on the messages database
# See the SQLite documentation for details on how to construct a query:
# https://sqlite.org/lang_select.html
import sqlite3

dbFile = 'data.db'

conn = sqlite3.connect(dbFile)
c = conn.cursor()

messages = c.execute("SELECT * FROM messages WHERE student IS 'sbell03'")

for m in messages:
  print(m)

