## 2024-05-24 - Resolve N+1 Queries in Simulation Context Fetching
**Learning:** Extracting extra related tables via inner SELECTs inside helper functions called in a loop over dataset rows creates an N+1 queries performance bottleneck.
**Action:** When enriching logging or simulation data, prefer fetching all related data via a SQL JOIN in the primary query (e.g. extending an existing `LEFT JOIN` to pull user names directly) to eliminate sequential secondary query dispatches inside loops.
