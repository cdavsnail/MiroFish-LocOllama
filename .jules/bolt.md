
## 2025-05-01 - Fix N+1 SQLite queries when parsing simulation log output
**Learning:** When retrieving contextual information for events in the backend parallel simulation loop (like fetching author's user names for posts or comments), doing additional nested `SELECT` queries inside `_get_post_info` loop creates N+1 query patterns that severely degrade the log parsing performance.
**Action:** When enriching simulation data (e.g., in `run_parallel_simulation.py`), use SQL JOINs to fetch related user/author information in the primary query to avoid N+1 query patterns.
