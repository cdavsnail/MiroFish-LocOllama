
## 2024-05-24 - Fix N+1 Query in Simulation Data Enrichment
**Learning:** Found an N+1 query bottleneck in `run_parallel_simulation.py` where the code was doing a `LEFT JOIN` on the `user` table to fetch the `agent_id`, but then issuing a separate `SELECT name, user_name FROM user WHERE user_id = ?` query for each row to get the user's name if `agent_id` wasn't mapped. This is a classic N+1 anti-pattern when enriching simulation data.
**Action:** When enriching data from SQLite (like getting author info for posts/comments), always fetch all required fields in the initial SQL JOIN rather than making subsequent single-row queries in a loop or helper function.
