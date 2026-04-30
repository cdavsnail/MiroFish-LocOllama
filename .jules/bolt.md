## 2025-02-18 - Avoid SQLite json_extract Crashes on Malformed JSON
**Learning:** SQLite's `json_extract` function will crash the entire query and batch operation if it encounters a malformed JSON string in any evaluated row. This makes it dangerous to use directly on columns where data integrity isn't 100% guaranteed (e.g., text columns storing JSON logs).
**Action:** Always wrap `json_extract` calls with a `json_valid` check in a `CASE` statement: `CASE WHEN json_valid(info) THEN json_extract(info, '$.key') ELSE NULL END`. This ensures the query degrades gracefully and returns NULL instead of failing completely.

## 2025-02-18 - Fix N+1 Queries with JSON Joins in SQLite
**Learning:** When dealing with action logs (like `trace` tables) that store foreign keys inside a JSON payload column, extracting those keys procedurally in Python and then querying the database row-by-row creates massive N+1 query bottlenecks.
**Action:** Use `LEFT JOIN` combined with the guarded `json_extract` technique to join the related tables directly in SQL. This consolidates data retrieval into a single query and significantly improves performance. Example: `LEFT JOIN post ON CASE WHEN json_valid(t.info) THEN json_extract(t.info, '$.post_id') ELSE NULL END = post.id`.
