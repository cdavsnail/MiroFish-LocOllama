import sqlite3
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()
cursor.execute("CREATE TABLE trace(info TEXT)")
cursor.execute("INSERT INTO trace VALUES ('{\"post_id\": 123}')")
cursor.execute("SELECT json_extract(info, '$.post_id') FROM trace")
print(cursor.fetchall())
