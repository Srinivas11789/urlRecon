import sqlite3
handle = sqlite3.connect("urlInformation.db")
cur = handle.cursor()
all = cur.execute("SELECT * FROM urlData")
for r in all:
    print r
