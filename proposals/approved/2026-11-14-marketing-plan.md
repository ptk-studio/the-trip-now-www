# Marketing and promotion plan: TheTripNow

Issue: [#6](https://github.com/ptk-studio/the-trip-now-www/issues/6). Written 2026-11-14 by web-worker1 (Claude).
Status: **approved** (prj-manager1, 2026-11-14 11:23 ET). **Every action here is the worker's alone.** Anything that needs
Thomas is at the end, under "Not in this plan".

## TL;DR

- **Baseline:** 748 products and no new ones since Sep 8. No Instagram posts since Sep 8. Store traffic is
  counted only from today. **Orders and revenue are unknown:** checkout is Printify's pop-up store, which
  this session can't read.
- **The biggest free lever:** the store page is invisible to search. Every store page is titled **"88eggs"**
  with the description **"88eggs frontend"**. There's no canonical link, `shop.88eggs.com/robots.txt`
  redirects to the login page, and there's no sitemap. Fixing that is a few hours of work.
- **Goal:** first sale by **2026-12-31**, then **$100/month by 2027-03-31**. Both are reviewed when the
  first real order data arrives.
- **First 30 days:** restart the content (Meme1 is fixed now, #324). Fix the store's SEO. Turn thetripnow.com
  into a landing page with tracked links. Then add a weekly reading.

## 1. Baseline (read 2026-11-14, read-only; details on #6)

| Reading | Value | Source |
|---|---|---|
| Orders, last 30 days | **unknown** (assumed $0) | Printify Pop-Up Store; not signed in from this session |
| Revenue, last 30 days | **unknown** (assumed $0) | same |
| Products | 748 | shop.88eggs.com/store/the-trip-now |
| Product mix on page 1 | 26 tees, 10 mugs, 4 journals, 4 posters, 2 mixing glasses, 2 lunch bags | store page links |
| Prices (examples) | mug $14.99, tee $24.99 | the-trip-now.printify.me product pages |
| Top tags on page 1 | OceanLife, GreatBarrierReef, UkiyoE, Vietnam, NewZealand, HaLongBay, Galapagos, Australia, Patagonia, Swiss/Italian Alps, ArtDeco, WPAStyle | store page |
| Newest product | 2026-09-08 | #3 |
| Instagram | 153 posts, 20 followers (2026-11-13); **0 posts since Sep 8** | instagram.com/thetripnow, 88eggs Meme1 queue |
| Store traffic | GA4 property 564337074 from 2026-11-14 only. Each page view is counted twice until 88eggs-backend#328 is fixed | GA4 |
| thetripnow.com traffic | not measured (no analytics tag) | page source |
| Store SEO | title "88eggs", description "88eggs frontend", no canonical; `robots.txt` → 307 to `/creator/login`; `sitemap.xml` → 307 | signed-out fetch |

## 2. Revenue goal

- **Milestone 1: the first order by 2026-12-31.** With unknown and probably zero sales, no traffic, and no
  new content for two months, the first order is the honest first target. December is gift season, and
  posters and mugs are gift items.
- **Goal: $100/month in sales by 2027-03-31.** That's about 5 orders a month at a $20 average (mug $14.99,
  tee $24.99). It's revenue, not profit: Printify's base cost comes out of it.
- **Why that number:** a small print-on-demand store with steady free traffic (search plus a social feed)
  typically converts well under 1% of visits. 5 orders a month needs roughly 500–1,000 store visits a month.
  That's reachable only if the store gets indexed and the content runs again.
- **Review:** at each 2-week metrics review. Re-set it when the first real order data arrives (see "Not in
  this plan": Printify reading).

**For the STATUS.md `Revenue:` line**, once approved:
`Revenue: goal first order by 2026-12-31, $100/mo by 2027-03-31 · source Printify Pop-Up Store
(the-trip-now.printify.me) · last 30 days unknown, not readable without a Printify sign-in (2026-11-14)`.

## 3. Who buys and why

1. **The traveller who's been there (or is about to go):** 25–55, buying a souvenir or a reminder of a trip,
   for themselves or as a gift. **Fits:** destination posters and mugs for named places (Ha Long Bay, Great
   Barrier Reef, Galápagos, Dolomites, Patagonia). They search by the place: "Ha Long Bay poster", "Dolomites
   art print", "Galapagos mug".
2. **The vintage-poster home-decor buyer:** buys for the style first (Ukiyo-e, Art Deco, WPA national-park
   posters), the place second. **Fits:** posters and framed posters in a consistent style, grouped as
   collections ("Ukiyo-e travel posters", "WPA-style national parks").

Tees are 26 of 40 items on page 1, but neither customer's first pick. Lead with posters and mugs.

## 4. Channels and actions, ranked by expected sales per hour

Free only. Each action is something the worker can do and verify.

| # | Action | Where | Hours | Why it ranks here | How it's verified |
|---|---|---|---|---|---|
| 1 | **Restart content.** Meme1 #0.0 → #2.0 posts images to Instagram again. Product1/2 make new designs. | 88eggs (already fixed in #324; #3 for products) | 0–1 (monitoring) | Without new posts and products nothing else moves | A new Instagram post after 08:47 PT; new products after the 20:00 PT sync (#3) |
| 2 | **Store SEO fix:** a per-store `<title>` and description ("The Trip Now: travel posters, mugs and tees for …"); per-tag titles ("Vietnam travel posters & mugs, The Trip Now"); canonical links; `robots.txt` served (not redirected) for the shop host; a sitemap of the store and its tag pages | `88eggs-frontend` PR (manager review) | 3–5 | Search is the only free traffic that compounds. Today Google sees 748 products under the title "88eggs" | A signed-out fetch shows the new title, description and canonical; robots.txt returns 200; the sitemap lists the tag pages; Search Console later (needs Thomas, below) |
| 3 | **Collections by style and place:** turn the top tags (UkiyoE, ArtDeco, WPAStyle; Vietnam, NewZealand, Galápagos, Dolomites, Patagonia) into linked collection pages with an intro line each | `88eggs-frontend` store page, or tag descriptions in the 88eggs project | 2–3 | Gives each customer a landing page that matches a search | The tag pages render with an intro and a unique title |
| 4 | **thetripnow.com as a landing page:** replace the links-only page with 6–8 featured products (posters and mugs first), each with UTM links (`utm_source=thetripnow&utm_medium=site&utm_campaign=landing`), plus links to the collections | this repo, PR | 2 | Gives Instagram's bio link somewhere to land that sells | Page live; each link returns 200 and carries UTMs |
| 5 | **Instagram captions point at the bio link:** Meme1 #0.0's caption ends with a short call to action, "Prints and mugs of <place>: link in bio". Caption URLs aren't clickable, so there's no link in the caption. The bio link is already **thetripnow.com** (action 4's landing page; read 2026-11-14) | 88eggs Meme1 caption prompt (a pipeline content change, recorded on #6) | 1 | Turns the reborn feed into landing-page visits, then store visits | The next captions end with the line; GA4 shows thetripnow.com → store visits with `utm_source=thetripnow` |
| 6 | **Analytics on thetripnow.com:** add the same GA4 measurement as the store, so the landing page's clicks are counted | this repo, PR | 0.5 | Measurement for #4 | GA4 Realtime shows a thetripnow.com hit |

**Not ranked (wrong channel for now):** Pinterest. It's the strongest channel for posters, but it needs a new
account, which isn't in this plan.

## 5. Measurement

- **Store visits:** GA4 property 564337074, page path `/store/the-trip-now*`, weekly. Halve it until #328
  is fixed.
- **Traffic by channel:** GA4 sessions by `utm_source`. Instagram traffic arrives through the bio link → thetripnow.com, so it shows as `utm_source=thetripnow` on the store, plus thetripnow.com's own referrer (`instagram.com`) once action 6 is in.
- **Product clicks out to Printify:** not counted today. The store's outbound clicks to
  `the-trip-now.printify.me` could be sent as a GA4 event (`select_item`) in the action 2 PR.
- **Orders and revenue:** only Printify can say. Until Thomas allows a Printify reading, record "unknown".
- **Content:** Instagram post count, signed out, and the store's product count (both already in the
  readings file).
- **Weekly reading on #6**, Mondays: store visits (7 days), visits by source, Printify click events, new
  Instagram posts, new products, and orders (or "unknown").

## 6. First 30 days

| Date (2026) | Milestone |
|---|---|
| Nov 15 | Instagram posting again (#324) and new products after the sync (#3), both verified |
| Nov 20 | Action 2, the store SEO fix, PR merged and verified signed out |
| Nov 24 | Action 4, the thetripnow.com landing page, and action 6, its analytics, merged |
| Nov 27 | Action 5, the "link in bio" call to action, live on new posts |
| Dec 1 | Action 3, collection pages for 3 styles and 5 places |
| Every Monday from Nov 17 | The weekly reading on #6 |
| Dec 14 | 30-day review: visits, clicks out, orders if known. Re-rank the actions |

## Not in this plan (would need Thomas)

- **Read Printify orders:** a one-time Printify sign-in in Chrome, or a pasted 30-day order count. Payoff: a
  real baseline and order counting. Without it, the revenue goal can't be measured.
- **Google Search Console for shop.88eggs.com:** verify the domain and submit the sitemap. Payoff: shows
  whether action 2 works, and which searches find the store.
- **Pinterest business account:** pin the posters with UTM links. Payoff: likely the biggest poster channel,
  but it takes 1–3 months to ramp.
- **Etsy listings linking to the store:** a new seller account and listing fees. Payoff: Etsy's own search
  traffic for "travel poster".
