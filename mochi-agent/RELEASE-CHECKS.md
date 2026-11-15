# Release checks: thetripnow

Pre-release and post-release validation for this project (ptk-studio handbook, `mochi-factory/project-groups/AGENTS.md`
→ "Release validation"; task #16). Project type: **web + content**. The worker (web-worker1) runs every check
unless a row says the Owner. This file is excluded from the Pages build.

Every release PR lists the pre-release results (the scorecard: one row per step, with pass/fail, evidence and
date). Every release gets a post-release report on its issue.

## What counts as a release here

| Kind | Release event | Rollback |
|---|---|---|
| **S. Site** (thetripnow.com, GitHub Pages) | a merge to `main` (Pages deploys it) | revert PR, merged after the manager's "cleared to merge" |
| **C. Content pipeline** (88eggs project `Web:TheTripNow`) | turning a schedule on, or changing a schedule, pipeline, task input or data table that a schedule uses (Meme1 → Instagram; Product1/2 → Printify store) | pause the schedule; restore the previous pipeline version or table rows |
| **B. Book** (KDP: paperback or Kindle) | clicking **Publish** (the Owner's yes, typed in the session) | KDP **Unpublish** (Bookshelf → … → Unpublish), decided by the Owner |

---

## S. Site (a merge to `main`)

### Pre-release (on the PR branch)

| # | Step | Expected result |
|---|---|---|
| S1 | `tools/release-check.sh pre` | every line `PASS`, exit 0: every top-level path is public (`CNAME`, `index.html`, `_config.yml`) or in `_config.yml` `exclude:`; no secret-like strings in the diff; `index.html` keeps the title and the store link |
| S2 | New internal folder or file? It is added to `exclude:` **in the same PR** | S1 catches a miss |
| S3 | UI change: open `index.html` locally in Chrome (desktop width, then 390 px) | layout intact; store and footer links work; **screenshots in the PR** |
| S4 | Links changed: `curl -s -o /dev/null -w '%{http_code}' <url>` for each new or changed link | 200 (or 301 → 200) |

### Post-release (right after the merge, then again within 24h)

| # | Step | Expected result |
|---|---|---|
| S5 | `tools/release-check.sh post` (wait for the Pages build, usually 1–2 min) | Pages build `built` on the merged commit; `https://thetripnow.com/` 200 with "The Trip Now"; every `exclude:` path 404; store page 200 |
| S6 | The HEALTH-CHECK.md sign-in-free checks | all pass |
| S7 | Re-run S5 within 24h | all `PASS` |

**Watch:** the Pages build status, and the health check at each manager sweep for 24h. **Rollback:** if S5 or S7 fails,
open a revert PR at once and say so on the issue; the manager clears it. An internal file served by mistake
(an `exclude:` path returning 200) counts as a failure even if the site looks fine.

---

## C. Content pipeline (88eggs)

### Pre-release

| # | Step | Expected result |
|---|---|---|
| C1 | Make the change on a **clone** (pipeline) or as new rows (table); the live version stays as the fallback | the old version is unchanged |
| C2 | **Test run** of the clone with outputs **held**: Meme1 not posted (no `x-poster`/Instagram step, or a held status); Product designs not uploaded to Printify | run `Completed`; nothing published; the run ID is in the issue |
| C3 | Review the test output: image legible and on-brief, text spelled right, the destination and facts correct, the format right (Meme1 square, Product1 vertical, Product2 horizontal) | pass, with a screenshot on the issue |
| C4 | Cost per run from the run page, against the budget | within budget (Owner's yes for any new spend) |
| C5 | Connections valid: 88eggs Connections shows Instagram and Printify connected (no `invalid_grant`) | connected |
| C6 | Table rows: the text format matches the existing rows; the length is within the step's limit; the Status follows R9 | pass |

### Post-release (the first scheduled run, then within 24h)

| # | Step | Expected result |
|---|---|---|
| C7 | The first scheduled run after the change: 88eggs Pipeline Runs | `Completed`; no charge-then-refund in the ledger (that means it failed) |
| C8 | The item appears: Instagram post count up / new store product (HEALTH-CHECK.md new-item signals) | count up within one cadence |
| C9 | No failed runs in the project in 24h (Task Runs, filter Failed) | none new |

**Rollback:** pause the schedule or switch it back to the previous pipeline; report on the issue. No paid re-runs
of failed output without approval.

---

## B. Book (KDP)

### Pre-release

| # | Step | Expected result |
|---|---|---|
| B1 | `python3 books/build.py books/<book>` | the report: interior 6×9 in; ≥ 24 pages; fonts embedded; every photo, map and cover image ≥ 300 dpi; the cover size matches the spine; EPUBCheck 0 errors; the back-page link 200 |
| B2 | Facts: every fact sentence cites a checked fact id; the fact pack has 2+ sources per item and the Owner confirmed the `[check]` items | every cite resolves; no uncited claims |
| B3 | Rights: every photo is PD, CC0 or CC BY, with credits on the "Sources and credits" page; maps carry "© OpenStreetMap contributors" | pass |
| B4 | Page screenshots and the cover in the PR | reviewed by the manager |
| B5 | KDP form: metadata, AI-content disclosure, categories, price; **Previewer** shows no errors (margins, bleed, fonts) | Previewer clean; stop before Publish |
| B6 | **Publish:** the Owner's yes typed in the session; the Owner signs in | recorded on the issue |

### Post-release

| # | Step | Expected result |
|---|---|---|
| B7 | KDP Bookshelf: **In review** → **Live** (usually within 72h); check every 4h | Live |
| B8 | The Amazon page: title, cover, price, "Look inside" or preview; the /dp/ link and ASIN on the issue | correct |
| B9 | The site/store lists the book (when a Books section exists) | the link works (200) |

**Rollback:** fix and resubmit through KDP (a new review), or the Owner unpublishes.

---

## Who runs what

- **The worker:** every step above, except B6.
- **The Owner:** B6 (the yes, and the KDP sign-in), any new spend (C4), and the decision to unpublish a book.
- **The manager:** reviews the scorecard, and gives "cleared to merge" (S) or the go-ahead (C, B).
