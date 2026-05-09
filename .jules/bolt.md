## 2024-05-17 - Optimize Context Fetching in Parallel Simulation Manager
**Learning:** In backend simulation manager scripts, secondary queries executed inside data extraction functions (like `_get_post_info` fetching `name` and `user_name` for fallback display names) create an N+1 query bottleneck because they loop over every post or comment event.
**Action:** Use SQL JOINs to fetch related user and author information in the primary query to avoid N+1 query patterns.
