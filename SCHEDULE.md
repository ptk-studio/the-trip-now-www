# SCHEDULE: The Trip Now (thetripnow.com, poster store, Instagram)

Everything that runs on a schedule for this project (R93; the standard is in the hub's `project-groups/AGENTS.md` → 'Scheduled work'). **Read from what runs, not memory:** 88eggs schedules listed with `schedules list` and mm1-worker1's session crons, on 2026-11-18. A change to a job updates its row in the same PR or commit.

| What | When (ET) | Where it runs | Owner (agent) | Approval | Cost | Status | Last checked |
|---|---|---|---|---|---|---|---|
| Travel meme source generator (AI image) | every 4 h at :17 (`17 */4 * * *` PT) | 88eggs `cDMDcQF--NP4B6BrMAoT2` → [Meme1] #0.0 (Web:TheTripNow) | mm1-worker1 | the Owner's goal 2026-11-13: new content for the store and Instagram | ≈ $0.07 an image | on | 2026-11-18 |
| Post 1 meme to Instagram | every 4 h at :47 (`47 */4 * * *` PT) | 88eggs `CiwW6KgSW1_tKnN_WO7G8` → [Meme1] #2.0 Instagram Publish | mm1-worker1 | the same goal (2026-11-13) | $0 | on | 2026-11-18 |
| Design generation (Product1, Product2) | every 12 h (`0 */12 * * *` PT) | 88eggs `U3smbP8TCMI8aFe-i80Vh`, `UxifWMWd_nADQIZlYdy_r` | mm1-worker1 | the same goal | AI per design | on | 2026-11-18 |
| Printify uploads: tee, mug, notebook/journal, lunch bag, framed poster, mixing glass (Product1 + Product2, 12 schedules) | every 5 min (`*/5 * * * *` PT; each claims a waiting design) | 88eggs `eTnv6gdhTomQ1jbWgCZJO`, `c5MKEkqCmr43Vcf9_GlND`, `Uf-hGaqFGjsWeeLtZ3_UQ`, `Jn0VFpbaUKVJKZjUx6HI-`, `rqcLfvt7P134_d5aOo9Fl`, `sEkK374JivyZERz3uaC3U`, `DHPw_EyqxtMAWUBNw7D8t`, `cvYH_5g3OLbiQgJbFsneC`, `eF2taYJipPVph4-_8kIbl`, `mStCC4CDJL2sqvgB2tXLK`, `se8E01iFEBtn0AihqoYXL` | mm1-worker1 | the same goal | $0 | on | 2026-11-18 |
| Printify storefront sync | daily 23:00 (`0 4 * * *` UTC) | 88eggs `i2haOFxWQLqJxfRA9P2ti` | mm1-worker2 | the same goal | $0 | on | 2026-11-18 |
| Napa guide: Mondavi photo retry (one-shot) | 2026-11-18 13:27 | a session cron of mm1-worker1 (re-created by `/mochi-session-mm1-worker1` from `project-groups/web1/worker-checks.md`), job 652f2e59 | mm1-worker1 | Q261 | $0 | one-shot | 2026-11-18 |
