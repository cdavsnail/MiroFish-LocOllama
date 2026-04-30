import sqlite3
import json

conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

cursor.execute("CREATE TABLE trace(user_id INT, action TEXT, info TEXT)")
cursor.execute("CREATE TABLE post(post_id INT, user_id INT, content TEXT, original_post_id INT, quote_content TEXT)")
cursor.execute("CREATE TABLE user(user_id INT, agent_id INT, name TEXT, user_name TEXT)")
cursor.execute("CREATE TABLE follow(follow_id INT, followee_id INT)")
cursor.execute("CREATE TABLE comment(comment_id INT, user_id INT, content TEXT)")

cursor.execute("INSERT INTO user VALUES (1, 100, 'Alice', '@alice')")
cursor.execute("INSERT INTO post VALUES (10, 1, 'Hello World', NULL, NULL)")
cursor.execute("INSERT INTO trace VALUES (2, 'LIKE_POST', '{\"post_id\": 10}')")

cursor.execute("""
            SELECT
                t.rowid, t.user_id, t.action, t.info,

                -- POST info
                p1.content as p_content, u1.agent_id as p_agent_id, u1.name as p_name, u1.user_name as p_uname,

                -- REPOST/QUOTE_POST (new_post_id) info
                p3.quote_content as p_quote_content,
                p4.content as rp_content, u4.agent_id as rp_agent_id, u4.name as rp_name, u4.user_name as rp_uname,

                -- QUOTED_POST info
                p2.content as q_content, u2.agent_id as q_agent_id, u2.name as q_name, u2.user_name as q_uname,

                -- FOLLOW info
                u5.agent_id as f_agent_id, u5.name as f_name, u5.user_name as f_uname,

                -- MUTE info
                u6.agent_id as m_agent_id, u6.name as m_name, u6.user_name as m_uname,

                -- COMMENT info
                c.content as c_content, u7.agent_id as c_agent_id, u7.name as c_name, u7.user_name as c_uname

            FROM trace t
            LEFT JOIN post p1 ON json_extract(t.info, '$.post_id') = p1.post_id
            LEFT JOIN user u1 ON p1.user_id = u1.user_id

            LEFT JOIN post p2 ON json_extract(t.info, '$.quoted_id') = p2.post_id
            LEFT JOIN user u2 ON p2.user_id = u2.user_id

            LEFT JOIN post p3 ON json_extract(t.info, '$.new_post_id') = p3.post_id
            LEFT JOIN post p4 ON p3.original_post_id = p4.post_id
            LEFT JOIN user u4 ON p4.user_id = u4.user_id

            LEFT JOIN follow f ON json_extract(t.info, '$.follow_id') = f.follow_id
            LEFT JOIN user u5 ON f.followee_id = u5.user_id

            LEFT JOIN user u6 ON COALESCE(json_extract(t.info, '$.user_id'), json_extract(t.info, '$.target_id')) = u6.user_id

            LEFT JOIN comment c ON json_extract(t.info, '$.comment_id') = c.comment_id
            LEFT JOIN user u7 ON c.user_id = u7.user_id

            WHERE t.rowid > 0
            ORDER BY t.rowid ASC
""")
print(cursor.fetchall())
