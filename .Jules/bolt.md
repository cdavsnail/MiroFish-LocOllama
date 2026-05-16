## 2024-05-16 - Eliminate N+1 SQL Queries in Action Simulation Log Fetching

**Learning:** `fetch_new_actions_from_db` previously suffered from a severe N+1 problem: iterating through `trace` logs and dispatching sequential queries via helper methods to fetch related objects (users, posts, quotes). For a high-frequency polling script in an agentic simulation, this caused massive unneeded database I/O overhead. SQLite's `json_extract` makes it entirely feasible to construct comprehensive `LEFT JOIN` relations via embedded dynamic IDs.

**Action:** Whenever iterating through a log table that records actions using embedded reference IDs (such as within a JSON `info` payload), do not perform supplementary scalar lookups within the application loop. Write a unified SQL `LEFT JOIN` referencing variables mapped dynamically using `CASE WHEN json_valid(col) THEN json_extract(col, '$.key') ELSE NULL END`.
