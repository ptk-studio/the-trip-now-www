# Proposal: an 88eggs pipeline that makes TheTripNow travel guides to sell on Amazon

- **Status:** pending (Thomas asked for it, 2026-11-14)
- **Author:** web-manager1
- **Project:** thetripnow. **Pipeline home:** 88eggs creator project `4d8vz_x_4O3gf9aubwWcH` (Web:TheTripNow)
- **Decision needed from:** Thomas (approval, budget cap, Amazon account)

## Goal

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

## Pipeline design (88eggs)

A data table **`Guides1`** holds one row per guide. Each step claims rows
by `status`, like Songs1. All steps are on existing 88eggs tasks unless
marked **new**.

| # | Step | Task | Row status after |
|---|---|---|---|
| 0 | Pick destinations: seasonal demand, low competition, fits the brand | text-generator (Claude Sonnet 5.5) | `IDEA` |
| 1 | Outline: days, sections, the list of facts to source | text-generator | `OUTLINE_READY` |
| 2 | Source facts: official sites and transit authorities, with URL and date per fact | **new: web research step** (88eggs has no web-fetch task today) | `SOURCED` |
| 3 | Write the chapters from the outline and sourced facts only | text-generator | `DRAFTED` |
| 4 | Fact check: every claim against the sources; unconfirmed claims are listed | text-generator, second pass | `CHECKED`, or back to `SOURCED` |
| 5 | Cover and section art in the TheTripNow style (no maps of real streets) | image-generator (Nano Banana) | `ART_READY` |
| 6 | Build files: Kindle EPUB, print interior PDF (6×9, bleed), cover PDF with spine width from page count | **new: book-builder task** | `BUILT` |
| 7 | Review: the manager checks the files against a checklist (facts, layout, spelling, disclosure) | manual | `APPROVED` |
| 8 | Publish on KDP | **manual by Thomas** (KDP has no publishing API) | `PUBLISHED` |

**New code** (88eggs-backend, through reviewed PRs):
1. **`book-builder-task`:** Markdown and images in; EPUB, interior PDF and
   cover PDF out. It checks KDP's file rules (trim, bleed, margins, page
   count limits).
2. **A web research step**, so step 2 can fetch and cite pages. This could
   be a model with web access through OpenRouter, or a fetch task. Its
   design comes with the first implementation issue.

## What needs Thomas

- **Approve this proposal**, or change the format, prices or pilot size.
- **An Amazon KDP account**, his own: sign-up, the tax interview and bank
  details are his alone. Agents never enter those.
- **A budget cap for the pilot.** Model and image costs are billed through
  88eggs credits and OpenRouter. They're measured on the first guide, and
  the pilot stops if the cap is reached. Proposed: **$15** for the 3 pilot
  titles.
- **Publishing each title** on KDP (step 8): he uploads the approved files,
  or tells us how he wants that step done.

## Milestones

1. **Approved:** this proposal moves to `proposals/approved/`.
2. **Code:** the `book-builder-task` and web-research PRs merged and
   deployed, with a test build of one sample book that passes KDP's
   previewer.
3. **Pipeline:** the `Guides1` table and steps 0–7 in 88eggs. The first
   guide is built and reviewed, and its real cost is recorded.
4. **Pilot:** 3 approved guides, published by Thomas.
5. **30-day check:** units, royalties and reviews per title. Then decide:
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

Each would be its own proposal later.
