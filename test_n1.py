import sqlite3
import json

def get_name(agent_id, user_id, name, user_name, agent_names):
    if agent_id is not None and agent_id in agent_names:
        return agent_names[agent_id]
    if name or user_name:
        return name or user_name or ''
    return ''

def fetch_new_actions_from_db_opt(db_path, last_rowid, agent_names):
    actions = []
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
        SELECT
            t.rowid, t.user_id, t.action, t.info,

            -- POST info (for LIKE_POST, DISLIKE_POST, CREATE_COMMENT)
            p_main.content, p_main.user_id, u_p_main.agent_id, u_p_main.name, u_p_main.user_name,

            -- REPOST info
            p_orig.content, p_orig.user_id, u_orig.agent_id, u_orig.name, u_orig.user_name,

            -- QUOTE_POST info
            p_quoted.content, p_quoted.user_id, u_quoted.agent_id, u_quoted.name, u_quoted.user_name,
            p_quote_new.quote_content,

            -- FOLLOW info
            u_follow.agent_id, u_follow.name, u_follow.user_name,

            -- MUTE info
            u_mute.agent_id, u_mute.name, u_mute.user_name,

            -- COMMENT info
            c.content, c.user_id, u_c.agent_id, u_c.name, u_c.user_name

        FROM trace t

        LEFT JOIN post p_main ON json_extract(t.info, '$.post_id') = p_main.post_id
            AND t.action IN ('like_post', 'dislike_post', 'create_comment')
        LEFT JOIN user u_p_main ON p_main.user_id = u_p_main.user_id

        LEFT JOIN post p_repost ON json_extract(t.info, '$.new_post_id') = p_repost.post_id
            AND t.action = 'repost'
        LEFT JOIN post p_orig ON p_repost.original_post_id = p_orig.post_id
        LEFT JOIN user u_orig ON p_orig.user_id = u_orig.user_id

        LEFT JOIN post p_quoted ON json_extract(t.info, '$.quoted_id') = p_quoted.post_id
            AND t.action = 'quote_post'
        LEFT JOIN user u_quoted ON p_quoted.user_id = u_quoted.user_id
        LEFT JOIN post p_quote_new ON json_extract(t.info, '$.new_post_id') = p_quote_new.post_id
            AND t.action = 'quote_post'

        LEFT JOIN follow f ON json_extract(t.info, '$.follow_id') = f.follow_id
            AND t.action = 'follow'
        LEFT JOIN user u_follow ON f.followee_id = u_follow.user_id

        LEFT JOIN user u_mute ON COALESCE(json_extract(t.info, '$.user_id'), json_extract(t.info, '$.target_id')) = u_mute.user_id
            AND t.action = 'mute'

        LEFT JOIN comment c ON json_extract(t.info, '$.comment_id') = c.comment_id
            AND t.action IN ('like_comment', 'dislike_comment')
        LEFT JOIN user u_c ON c.user_id = u_c.user_id

        WHERE t.rowid > ?
        ORDER BY t.rowid ASC
    """

    cursor.execute(query, (last_rowid,))
    rows = cursor.fetchall()
    print(f"Fetched {len(rows)} rows")
    for row in rows:
        print(row)

conn = sqlite3.connect('test.db')
c = conn.cursor()
c.execute("CREATE TABLE trace(user_id INT, action TEXT, info TEXT)")
c.execute("CREATE TABLE post(post_id INT, user_id INT, content TEXT, original_post_id INT, quote_content TEXT)")
c.execute("CREATE TABLE user(user_id INT, agent_id INT, name TEXT, user_name TEXT)")
c.execute("CREATE TABLE follow(follow_id INT, followee_id INT)")
c.execute("CREATE TABLE comment(comment_id INT, user_id INT, content TEXT)")

c.execute("INSERT INTO user VALUES (1, 100, 'Alice', '@alice')")
c.execute("INSERT INTO post VALUES (10, 1, 'Hello World', NULL, NULL)")
c.execute("INSERT INTO trace VALUES (2, 'like_post', '{\"post_id\": 10}')")
conn.commit()

fetch_new_actions_from_db_opt('test.db', 0, {100: "Alice Agent"})
