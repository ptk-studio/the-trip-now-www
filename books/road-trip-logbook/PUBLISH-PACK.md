# Road Trip Logbook: KDP publish pack (DRAFT; nothing is entered in KDP)

The Owner's yes on the page plan and the front cover: **T2-28, 2026-11-18** (*"Yes, as is"*, after the cover and pages 6 to 9 and 106). **The Publish yes and the proof come later (R51).** For the **January** paperback slot (t1-manager's queue). t2-worker1, ttn#39.

## Files (a draft GitHub release on this repo, so the Owner or t1-worker1 can upload from any machine)
- **`interior.pdf`**: 120 pages, 6 × 9 in, black and white, fonts embedded. `python3 books/road-trip-logbook/gen.py <out>`; checked by `check.py`.
- **`cover.pdf`**: the wrap, back + spine + front with 0.125 in bleed, **12.5202 × 9.25 in** at the spine width for 120 pages on white paper (0.2702 in). `python3 books/road-trip-logbook/cover.py <out> 120`.

## Checks (all PASS)
Interior: trim 6 × 9 in (432 × 648 pt); 120 pages, even, KDP minimum 24; fonts Noto Sans only, embedded; **nothing within 0.25 in of any trim edge** (the page-edge trip tabs included; pixel check on every page).
Cover: 12.5202 × 9.2500 in = 2 × 6 + 0.2702 + 2 × 0.125; spine text allowed (120 ≥ 80 pages) and set 0.0625 in or more from the spine edges; fonts embedded; **the barcode area (2 × 1.2 in, lower right of the back) is clear**; art drawn by code, no image model (R117).
Still to do at KDP (not now): open the files in **KDP's Previewer** (the Owner or t1-worker1 with the KDP sign-in) and read the **printed proof at 100 %** before any Publish. Re-check the spine width in KDP's cover calculator for 120 pages, white paper (a 0.01 in difference is fine).

## Listing (draft; for the KDP form later)
| Field | Value |
|---|---|
| Title | Road Trip Logbook |
| Subtitle | 25 Trips to Plan, Log and Remember: An Undated Glovebox Journal with Fuel, Cost and Booking Pages |
| Author | TheTripNow |
| Keywords (7) | road trip planner; road trip journal; travel log book; glovebox logbook; car trip planner; trip itinerary planner; mileage and fuel log |
| Categories | Books > Travel > Travel Journals (or the nearest KDP offers; pick from the form) |
| Trim / paper / ink / cover | 6 × 9 in, white paper, black and white, matte |
| Pages | 120 |
| Price | **$8.99**; royalty 60% × 8.99 − ($1.00 + 120 × $0.012) = **$2.95** (t2-manager's check; recompute in KDP's calculator) |
| Low-content box | tick it; no ISBN (KDP assigns an ASIN); no Expanded Distribution, no series, no Look Inside |
| Large print | not ticked |
| AI disclosure | Text: **Yes** (Claude, Anthropic); Images: **Yes** (cover art is code written by Claude; no image model); Translations: **No**. Wording as in the approved Napa pack (the manager's ruling). |
| Slot | January 2027 (paperback slots are full to 2027-01-09; 2 new paperbacks a week, resetting Saturday 19:00 ET) |

**Description** (about 150 words): see `cover-brief-and-listing.md`.
**AI answers, one more time:** never write "written by us" for AI-written work.
