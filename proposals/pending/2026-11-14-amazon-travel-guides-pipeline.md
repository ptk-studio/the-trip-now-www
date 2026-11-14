# Proposal: reusable 88eggs ebook tasks and pipeline, first used for TheTripNow travel guides on Amazon

- **Status:** pending (Thomas asked for it, 2026-11-14; revised the same day: built from reusable 88eggs tasks so other projects can make ebooks too)
- **Author:** web-manager1
- **Project:** thetripnow. **Pipeline home:** 88eggs creator project `4d8vz_x_4O3gf9aubwWcH` (Web:TheTripNow)
- **Decision needed from:** Thomas (approval, budget cap, Amazon account)

## Goal

**Two goals:**
1. **Reusable ebook building blocks in 88eggs:** generic tasks and a
   pipeline template that *any* project can use to make and sell ebooks.
   Thomas, 2026-11-14: "built with 88eggs tasks so that we can create
   ebooks to sell for other projects". Nothing in the tasks is specific to
   travel or to TheTripNow.
2. **The first use:** TheTripNow travel guides on Amazon KDP, described
   below.

**Later uses** of the same tasks, each its own decision:
- all-printable planners or workbooks;
- songbooks or lyric books for the music channels;
- low-content journals.

**The first use, in detail:**

A second revenue line for TheTripNow: short, accurate travel guides sold on
Amazon KDP, as a Kindle ebook and a paperback. 88eggs produces them on a
schedule, the same way it makes store designs and memes today. Success is
measured as **royalties per month** (KDP Reports), which feeds the project's
`Revenue:` line.

## What we'd sell

**Pocket itinerary guides:** one destination, 3–5 days, about 60–90 pages
at 6×9 in. For example, "Kyoto in 3 Days: a TheTripNow Pocket Itinerary".
Each one contains:
- day-by-day routes;
- neighbourhoods and where to stay;
- food to try, with budget tiers;
- getting around, seasonal tips, a packing list, and some blank planner
  pages at the back.

**Why this format:**
- Narrow itineraries are easier to keep accurate than full guidebooks.
- They're a known KDP niche.
- The planner pages add value that doesn't go out of date.

**Pricing to start:**
- **Ebook:** $4.99. KDP's 70% royalty band is $2.99–$9.99.
- **Paperback:** $9.99–$12.99. The royalty is 60% of the list price minus
  printing cost; it's computed per title in the KDP form.

## The main risk: quality

Amazon has removed and buried low-quality AI travel guides, and readers
review them harshly. This pipeline only works if every guide is
**accurate and useful**. So:
- **No invented facts.** Every venue, opening detail, price range and
  transport fact must come from a source recorded in the row. Anything that
  can't be sourced is cut, not guessed.
- **A fact-check step** reads the draft against those sources and lists
  every claim it can't confirm. A guide with any unconfirmed claim doesn't
  move on.
- **A dated "last checked" line** in each guide, and a refresh every 12
  months (or the title is unpublished).
- **No borrowed brands or images.** We don't use other guidebook series'
  names or maps. All images are generated or licensed.
- **AI disclosure:** KDP asks whether content is AI-generated, and we
  answer truthfully (yes).
- **Start small:** a pilot of 3 titles. We decide on volume only after real
  reviews and sales.

## Design: reusable tasks + a pipeline template (88eggs)

### New generic 88eggs tasks

They're built like the existing task catalog (`ptk-studio/*-task` in
`public.tasks`, e.g. text-generator, image-generator, table-update-row).
Each takes plain inputs and knows nothing about any one project.

| Task | Inputs | Outputs |
|---|---|---|
| **`ptk-studio/web-research-task`** | questions or a fact list; optional allowed domains | an answer per fact, with source URL, quote and fetch date; "not found" when unsourced |
| **`ptk-studio/fact-check-task`** | draft text and the sources from web-research | each claim marked confirmed or unconfirmed, with the source; pass/fail |
| **`ptk-studio/book-builder-task`** | Markdown chapters, images, metadata (title, author, ISBN or none), format settings (trim size, bleed, fonts, ebook and/or paperback) | Kindle EPUB, print interior PDF, cover PDF (spine width from page count, KDP paper type); a validation report against KDP file rules |
| **`ptk-studio/book-cover-task`** | front art, title text, back text, spine width | a full wrap cover PDF and a Kindle front-cover JPG at KDP sizes |
| **`ptk-studio/kdp-listing-task`** | book summary, audience, category hints | listing copy: description, 7 keywords, 2–3 categories, price suggestion, AI-disclosure answer. Drafted for review, never submitted |

**Existing tasks reused:** text-generator (Claude Sonnet 5.5),
image-generator (Nano Banana), table-list/get/insert/update-row,
start-pipeline, email-sender (optional "ready for review" notice).

### The pipeline template: `Ebook1`

A template any creator project can copy. A project fills in only:
- a **book-type brief:** genre, length, voice, page layout, which sections
  need sourced facts;
- a **style** for art.

It keeps one row per book in a project table, and each step claims rows by
`status`, like Songs1:

| # | Step | Task | Row status after |
|---|---|---|---|
| 0 | Ideas from the brief (demand, competition, fit) | text-generator | `IDEA` |
| 1 | Outline, plus the list of facts to source | text-generator | `OUTLINE_READY` |
| 2 | Source the facts (skipped when the brief needs none) | **web-research-task** | `SOURCED` |
| 3 | Write the chapters from the outline and sources only | text-generator | `DRAFTED` |
| 4 | Fact check; failures go back to `SOURCED` | **fact-check-task** | `CHECKED` |
| 5 | Art: cover and section images | image-generator → **book-cover-task** | `ART_READY` |
| 6 | Build the files | **book-builder-task** | `BUILT` |
| 7 | Listing copy | **kdp-listing-task** | `LISTING_READY` |
| 8 | Review against the checklist (facts, layout, spelling, disclosure) | manual: the manager | `APPROVED` |
| 9 | Publish on KDP from the upload packet | **the worker in Thomas's signed-in Chrome**, after his per-title yes (see "Publishing") | `PUBLISHED` |

### First instance: `[Guides1] TheTripNow Pocket Itineraries`

- Copied from `Ebook1` into creator project `4d8vz_x_4O3gf9aubwWcH`.
- **Brief:** pocket itinerary format; facts required for every venue, price
  and transport detail.
- **Art:** the TheTripNow style.
- **Format:** 6×9 paperback plus Kindle.

**All code goes through reviewed 88eggs-backend PRs, one task each.** Each
task comes with tests and a sample run.

## Publishing (KDP has no API)

Amazon KDP has no public API for publishing or for sales reports, so
there's no 88eggs connector. Storing Thomas's KDP password in 88eggs to
script the site is ruled out: it risks the account, and agents never
handle his password. Instead:

- **The upload packet:** step 7 produces each book's files and every
  listing field, ready to paste: title, subtitle, description, keywords,
  categories, price, and the AI-disclosure answer.
- **Signing in:** Thomas signs in to kdp.amazon.com in his own Chrome and
  handles any 2-step verification or CAPTCHA himself.
- **The worker publishes** (web-worker1, Claude in Chrome) in that
  signed-in session:
  - **Fills** the KDP forms from the packet and uploads the files.
  - **Checks** the KDP previewer and its error report, and posts a
    screenshot on the book's issue.
  - **Clicks "Publish"** only after Thomas's yes in the worker's session,
    naming the exact titles (e.g. "publish Kyoto in 3 Days and Lisbon in
    3 Days"). A yes covers only the titles it names.
- **Decisions that stay with Thomas,** each a separate yes:
  - account setup, tax and bank details;
  - accepting KDP terms;
  - KDP Select (Kindle exclusivity) enrollment;
  - prices outside the approved range.
- **Sales reports:** the worker reads KDP Reports read-only in the same
  signed-in session, for the metrics review and the `Revenue:` line.

## What needs Thomas

- **Approve this proposal**, or change the format, prices or pilot size.
- **An Amazon KDP account**, his own: sign-up, the tax interview and bank
  details are his alone. Agents never enter those.
- **A budget cap for the pilot.** Model and image costs are billed through
  88eggs credits and OpenRouter. They're measured on the first guide, and
  the pilot stops if the cap is reached. Proposed: **$15** for the 3 pilot
  titles.
- **Publishing:** sign in to KDP in his Chrome, then a yes per title (named)
  in the worker's session. The worker fills the forms and clicks Publish.

## Milestones

1. **Approved:** this proposal moves to `proposals/approved/`.
2. **Tasks:** the 5 new tasks merged and deployed, one PR each. First
   `book-builder-task`, proven with a sample book that passes KDP's
   previewer. Then `book-cover-task`, `web-research-task`,
   `fact-check-task` and `kdp-listing-task`.
3. **Template:** the `Ebook1` pipeline template, documented so another
   project can copy it.
4. **First instance:** `Guides1` in TheTripNow. The first guide is built
   and reviewed, and its real cost is recorded.
5. **Pilot:** 3 approved guides, published by the worker after Thomas's yes.
6. **30-day check:** units, royalties and reviews per title. Then decide:
   stop, fix, or scale (for example, 2 titles a week).

## Metrics

- **Titles published**, and their "last checked" dates.
- **Units and royalties per month** (KDP Reports), recorded in the
  project's `Revenue:` line and its 2-week metrics review.
- **Average review rating.** Below 4.0 means we pause and fix quality.
- **Cost per title**, against royalties per title.

## Not in this proposal

- Paid ads (Amazon Ads) or any outreach.
- Other marketplaces.
- Translated editions.

Each would be its own proposal later. So would using `Ebook1` in another project.
