# DAILY-CHECKS: The Trip Now (thetripnow.com, poster store, Instagram)

What is checked every day (R97; the standard is in the hub's `project-groups/AGENTS.md` → 'Daily checks'). The worker runs these in its first sweep of the day and writes the results into the manager's daily analytics; a major problem goes to the Owner the same sweep.

| Check | Where | Healthy looks like | If not, do this | Who |
|---|---|---|---|---|
| New user feedback (R64) | 88eggs Feedback inbox for this project; the hub feedback digest | every message read within a day | reply or file a Task; a bug report goes to the manager the same sweep | mm1-worker1 (first sweep of the day) · read by mm1-manager1 |
| AI cost yesterday (R83) | `mochi-factory/costs/<YYYY-MM>.csv` (hub), rows for this project | within its share of the $15/day, $300/month cap | flag to the manager; pause the costliest schedule if over (the manager's call) | mm1-worker1 (first sweep of the day) · read by mm1-manager1 |
| Published items 24 h / 7 d (R92) | `mochi-factory/published/<YYYY-MM>.csv` + `analytics/youtube/<date>.csv` (hub) | a reading for every item published 1 and 7 days ago | mark the missing reading; tell mm1-worker2 if the sync missed it | mm1-worker1 (first sweep of the day) · read by mm1-manager1 |
| Site up | `https://thetripnow.com/` and the guides' pages | HTTPS 200; certificate > 14 days | tell the manager; check Pages builds | mm1-worker1 (first sweep of the day) · read by mm1-manager1 |
| New Instagram posts and store products | the Meme1 and Product schedules' runs yesterday (88eggs) | ≥ 1 post and ≥ 1 new product a day; no failed runs | the error on the Task; never re-run without the manager | mm1-worker1 (first sweep of the day) · read by mm1-manager1 |
