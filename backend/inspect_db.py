# backend/inspect_db.py
import sqlite3

conn = sqlite3.connect("interviewpilot.db")
cursor = conn.cursor()

# list tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", [row[0] for row in cursor.fetchall()])

# inspect one table's columns
cursor.execute("PRAGMA table_info(responses);")
for col in cursor.fetchall():
    print(col)

conn.close()