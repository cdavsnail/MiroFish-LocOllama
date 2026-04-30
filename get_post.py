import sqlite3
import json

def get_simulation_posts(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, u.agent_id as author_agent_id, u.name as author_name, u.user_name as author_username
        FROM post p
        LEFT JOIN user u ON p.user_id = u.user_id
        ORDER BY p.created_at DESC
        LIMIT 10
    """)
    posts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return posts
