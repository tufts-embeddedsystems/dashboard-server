# Put some fake data into the database for testing purposes

import numpy as np
import time
import sqlite3

now = time.time()

N_POINTS = 72
DATABASE_FILE = "data.db"

t = np.array(range(N_POINTS)) * 3600 + int(now) - (N_POINTS * 3600) # Make data up to present
temp = 12 + 7*np.sin(2*np.pi * t / (24*3600))
sensortemp = temp + 1.2*np.random.random(N_POINTS)
thermistor = temp + 3*np.random.random(N_POINTS)

#import matplotlib.pyplot as plt
#plt.plot(t, sensortemp, t, thermistor)
#plt.show()

conn = sqlite3.connect(DATABASE_FILE)
c = conn.cursor()

for i in range(N_POINTS):
  # Logger will split sbell03/hw5/ic_temp into "sbell03" and "ic_temp"
  # Even though the timestamp is stored as an integer, the query is a string, so we have to convert it!
  c.execute("INSERT INTO messages VALUES (?,?,?,?)", (str(t[i]), "sbell03", "ic_temp", sensortemp[i]))
  c.execute("INSERT INTO messages VALUES (?,?,?,?)", (str(t[i]), "sbell03", "thermistor_temp", thermistor[i]))
  c.execute("INSERT INTO messages VALUES (?,?,?,?)", (str(t[i]), "sbell03", "uptime", i*3600))
  c.execute("INSERT INTO messages VALUES (?,?,?,?)", (str(t[i]), "sbell03", "battery", 4.1))
  conn.commit()

conn.close()

