# Health check: thetripnow

The project's health-check list (ptk-studio handbook, `projects/AGENTS.md` → "Health checks"; type
definitions in `projects/PROJECT-TYPES.md`). Agents read the checks from **this file**. The repo root is
published by GitHub Pages, so this file is in `_config.yml`'s `exclude:` list and is never served.

Values checked against the live sites on 2026-11-13 (all passed). Change this file by PR, like any other
repo change.

## Properties

### Type `web`
- **Main repo:** `ptk-studio/the-trip-now-www`. **Deploy:** GitHub Pages (Jekyll) serves `main` from the
  repo root at https://thetripnow.com. A merge to `main` is a production deploy.
- **Traffic source:** none (the site has no analytics tag; the kickoff, #1, may propose one).
- **Smoke test:** none.

### Type `content`
- **Channels:**
  - Instagram https://www.instagram.com/thetripnow/
  - Store https://shop.88eggs.com/store/the-trip-now
- **Cadence:** not set yet (the kickoff, #1, sets it). Until then, the 7-day default applies to both
  channels.
- **Pipeline:** 88eggs project `Web:TheTripNow`,
  https://app.88eggs.com/creator/projects/4d8vz_x_4O3gf9aubwWcH.
  - Store: the `Product1/2 Design Generation v1` schedules (every 12h) plus the `Printify Upload v1`
    schedules (every 5 min).
  - Instagram: the `[Meme1]` schedules (every 4h).
- **Readings file:** `projects/thetripnow/content-readings.md` in `ptk-studio/ptk-studio`.

## Sign-in-free checks (manager, every sweep)

It passes when every row returns the expected status **and** the body contains the text. Read-only: one
request per URL.

### Pages

| URL | Expected status | Must contain |
|---|---|---|
| https://thetripnow.com/ | 200 | `The Trip Now` |
| https://www.instagram.com/thetripnow/ | 200 | `&#064;thetripnow` |
| https://shop.88eggs.com/store/the-trip-now | 200 | `TheTripNow` |

- **Instagram:** the `@` is HTML-encoded in the page, so match `&#064;thetripnow`, never a literal
  `@thetripnow`. If Instagram redirects a signed-out fetch to a login page, that counts as **unknown**, not
  down: report it once.

### New-item signals (compare with the last row of the readings file)

| Channel | Signal | Reading 2026-11-13 |
|---|---|---|
| Instagram | Post count in the profile's `og:description` ("N Followers, N Following, **N Posts**") | 153 posts, 20 followers |
| Store | "**N products**" on the store page, and the newest product's creation date: the max, over page 1, of the first 8 hex digits (unix seconds) of the Printify ids in `images-api.printify.com/mockup/<id>/…` | 748 products; newest `6a9fb3a4…`, 2026-09-08 07:05 UTC |

"New" means the post count went up, the product count went up, or the newest product date is later.

### How to run it

Pages:

```sh
curl -sL --max-time 15 -A 'Mozilla/5.0' -o /tmp/body -w '%{http_code}' <url>; grep -c -F '<must contain>' /tmp/body
```

Newest store product date:

```sh
curl -sL --max-time 15 https://shop.88eggs.com/store/the-trip-now \
  | grep -oE 'images-api\.printify\.com/mockup/[0-9a-f]{24}' | sed 's|.*/||' | sort -u \
  | while read id; do echo "$((16#${id:0:8})) $id"; done | sort -n | tail -1
```

A wrong status, a count of `0`, or no new item for longer than the cadence is a failure. Report it at
once. A stale channel opens a "No new items" investigation issue (PROJECT-TYPES.md, `content`).

## Signed-in checks (worker, at most once a day, read-only)

Record each reading with its date in `content-readings.md` / STATUS.md:

- **Instagram:** the newest post on @thetripnow and its date.
- **Pipeline:** the latest scheduled runs of 88eggs project `4d8vz_x_4O3gf9aubwWcH` succeeded (Pipeline
  Runs page). A failure with `Not enough credits to run this task.` is the 88eggs-backend#324 outage again.
