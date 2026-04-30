import sqlite3
import json
conn = sqlite3.connect('test.db')
c = conn.cursor()
c.execute("""
            SELECT
                p.post_id, p.content, u.name, u.user_name, u.agent_id
            FROM post p
            LEFT JOIN user u ON p.user_id = u.user_id
        """)
print(c.fetchall())
