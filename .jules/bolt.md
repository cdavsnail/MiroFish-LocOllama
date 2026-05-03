## 2024-05-03 - Avoid N+1 Queries in SQLite Backend
**Learning:** The SQLite database queries in `run_parallel_simulation.py` for fetching post and comment information (`_get_post_info`, `_get_comment_info`) were executing a secondary `SELECT` to fetch the user's name details after already joining the `user` table in the primary query.
**Action:** When enriching simulation data, always use SQL JOINs to fetch related user/author information in the primary query to avoid N+1 query patterns and reduce database roundtrips.
