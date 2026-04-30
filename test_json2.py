import sqlite3
print(sqlite3.sqlite_version)
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()
cursor.execute("SELECT json_extract('{\"a\": 1}', '$.a')")
print(cursor.fetchone())
