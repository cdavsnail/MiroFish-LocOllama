
## 2025-02-23 - Resolve N+1 queries in `run_parallel_simulation.py` by using SQL JOINs
**Learning:** Found N+1 query patterns inside `_get_post_info` and `_get_comment_info` in `backend/scripts/run_parallel_simulation.py` where a `SELECT` statement loop was querying user names sequentially.
**Action:** Used SQL `LEFT JOIN` in the initial post/comment query to extract the related `user.name` and `user.user_name` properties, eliminating the N+1 loop and improving the execution time and database load.
