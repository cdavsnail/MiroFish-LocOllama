## 2025-05-07 - Optimize N+1 Query in OASIS Simulation Log Fetching
**Learning:** Found an N+1 query pattern in backend/scripts/run_parallel_simulation.py (`_get_post_info` and `_get_comment_info`) where the `user` table was repeatedly queried to retrieve the user's name during action logging for parallel simulations.
**Action:** Combined queries using `LEFT JOIN` on the user table in the primary SQLite query to fetch `name` and `user_name` alongside the `content` in a single query.
