## 2025-05-15 - N+1 Query Problem in Simulation Script
**Learning:** Found N+1 query problem when fetching `author_name` for posts and comments. By joining the `user` table in the initial query, we avoid making a secondary query for each post/comment just to get the author's name. This pattern of secondary queries on a per-row basis in simulation loops creates significant DB overhead, since it runs many times in a simulation session.
**Action:** Always fetch needed related entity data via JOINs in the primary query, especially when enriching data sets in a loop.
