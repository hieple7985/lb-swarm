import sqlite3

conn = sqlite3.connect('db.sqlite3')

cursor = conn.cursor()

cursor.execute('''
               CREATE TABLE IF NOT EXISTS zim_status
               (id INTEGER PRIMARY KEY AUTOINCREMENT,
               name VARCHAR(256),
               size INTEGER,
               status VARCHAR(256),
               timestamp INTEGER)
               ''')

conn.commit()
conn.close