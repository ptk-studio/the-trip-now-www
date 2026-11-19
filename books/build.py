#!/usr/bin/env python3
"""Prototype book builder for the TheTripNow test ebook (the-trip-now-www#8).

It is the starting point for the 88eggs `book-builder-task`. From the chapter
Markdown and the images it produces:

  out/book.epub      Kindle/reflowable EPUB 3 (pandoc)
  out/interior.pdf   print interior, 6x9 in, KDP margins, fonts embedded (WeasyPrint)
  out/cover.pdf      wrap cover: back + spine + front, with bleed (WeasyPrint)
  out/kindle-cover.jpg  front panel with title, for the KDP Kindle cover and the EPUB cover
  out/report.txt     checks: EPUBCheck, page size, page count, fonts, image dpi, spine

Tools (all open source): pandoc, WeasyPrint, EPUBCheck, poppler (pdfinfo, pdffonts).
Fonts: Noto Serif and Noto Sans (SIL Open Font License), installed on the system;
they are not copied into the repo.

Usage:  python3 books/build.py books/<guide>     (e.g. books/big-sur)

Every guide gets a standard back page: "Plan your next trip" with https://thetripnow.com/
(printed plain; a live UTM link in the EPUB), checked to return HTTP 200 at build time.
"""
import html
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent / "test"
SRC, OUT, STYLE = ROOT / "src", ROOT / "out", ROOT / "style"
CFG = json.loads((SRC / "book.json").read_text(encoding="utf-8"))
TRIM_W, TRIM_H = CFG["trim_in"]
BLEED = CFG["bleed_in"]
# Citation tags ([N5], [STAY-NAPA], [STAY-STHELENA-CALISTOGA]) are stripped
# from the book. Ids may have several hyphenated words (#9: Napa & Sonoma).
CITE = re.compile(r"\s*\[(?:[A-Z]\d+|(?:STAY|EAT)-[A-Z]+(?:-[A-Z]+)*)\](?:\[(?:[A-Z]\d+|(?:STAY|EAT)-[A-Z]+(?:-[A-Z]+)*)\])*")


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def need(tool):
    if not shutil.which(tool):
        sys.exit(f"missing tool: {tool}")


def reader_text(md: str) -> str:
    """Strip the [F#] fact citations, which are for checking, not for readers.
    book.json "nowrap_prices": keep price marks like $$ or $$–$$$ on one line (#9 review)."""
    md = CITE.sub("", md)
    if CFG.get("nowrap_prices"):
        md = re.sub(r"(?<![\w\]\[])(\$+(?:–\$+)?)(?![\d\w])", r"[\1]{.nowrap}", md)
    return md


# ---------------------------------------------------------------- photo credits (book.json "photo_credits": true)
LICENCE_URL = {"CC BY 4.0": "https://creativecommons.org/licenses/by/4.0/", "CC BY-SA 4.0": "https://creativecommons.org/licenses/by-sa/4.0/",
               "CC0": "https://creativecommons.org/publicdomain/zero/1.0/", "CC BY 3.0": "https://creativecommons.org/licenses/by/3.0/",
               "CC BY 2.0": "https://creativecommons.org/licenses/by/2.0/"}


def credits() -> dict:
    """images/credits.json -> {file name: entry}; used for a credit under each photo and the credits page."""
    f = ROOT / "images" / "credits.json"
    return {c["file"]: c for c in json.loads(f.read_text(encoding="utf-8"))} if CFG.get("photo_credits") and f.exists() else {}


def short_credit(image: str) -> str:
    c = credits().get(Path(image).name)
    if not c:
        return ""
    cap = f"Photo: {c['artist']} · {c['license']} · Wikimedia Commons"
    if c.get("changes"):      # CC BY: changes must be stated ("cropped")
        cap += f" ({c['changes']})"
    return f"{c['place']}. {cap}" if c.get("place") else cap


def credits_md() -> str:
    """The printed 'Sources and credits' page when book.json sets "sources_note" (the full source list lives online)."""
    out = ["# Sources and credits", "", CFG["sources_note"], "", "## Photo credits", ""]
    for c in credits().values():
        lic = c["license"]
        lic_txt = f"[{lic}]({LICENCE_URL[lic]})" if lic in LICENCE_URL else lic
        by = f"{c['artist']} ({c['changes']})" if c.get("changes") else c["artist"]
        page = f"<{c['page']}>" if CFG.get("autolink_credits") else c["page"]   # <url>: underscores in the address are not read as italics
        out.append(f"- *{c['title'].rsplit('.', 1)[0]}* by {by}, {lic_txt}, via Wikimedia Commons: {page}")
    if CFG.get("map_credit"):
        out += ["", "## Maps", "", CFG["map_credit"]]
    return "\n".join(out) + "\n"


def chapters():
    for ch in CFG["chapters"]:
        md = reader_text((SRC / "chapters" / f"{ch['file']}.md").read_text(encoding="utf-8"))
        if ch.get("map"):
            # optional day map, placed at the end of the chapter (print and EPUB)
            fig = f"![Map of {ch.get('map_title', 'the day')}]({ROOT / ch['map']}){{.day-map}}"
            if CFG.get("map_after_title"):   # opt-in: the map right under the chapter title, so the text flows after it and no page is left half empty
                head, sep, rest = md.partition("\n\n")
                md = f"{head}\n\n{fig}\n\n{rest}"
            else:
                md += f"\n\n{fig}\n"
        if CFG.get("day_recap") and ch.get("recap"):   # opt-in: an "at a glance" box and a ruled Notes area at the end of the chapter (text already in the chapter)
            rec = reader_text((SRC / "chapters" / f"{ch['recap']}.md").read_text(encoding="utf-8"))
            md += f"\n\n::: {{.recap}}\n{rec}\n:::\n\n::: {{.notes-area}}\n**Notes**\n\n" + "\n\n".join(["::: {.rule}\n&nbsp;\n:::"] * int(ch.get("notes_lines", 8))) + "\n:::\n"
        yield ch, md


def md_to_html(md: str) -> str:
    r = run(["pandoc", "-f", "markdown-tex_math_dollars", "-t", "html5"], input=md)
    if r.returncode:
        sys.exit(r.stderr)
    return r.stdout


def addr_nohyphen(h: str) -> str:
    """Opt-in (book.json "no_hyphen_addresses"): never hyphenate a web address in the print interior ('skiheav-enly.com')."""
    if not CFG.get("no_hyphen_addresses"):
        return h
    pat = r"(?<![\w@/.=-])((?:[A-Za-z0-9-]+\.)+(?:com|org|gov|net)(?:/[\w./-]*)?)"
    return re.sub(pat + r"(?![^<]*>)", r'<span style="hyphens: none">\1</span>', h)


def image_px(path: Path):
    r = run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)])
    w = re.search(r"pixelWidth: (\d+)", r.stdout)
    h = re.search(r"pixelHeight: (\d+)", r.stdout)
    return (int(w.group(1)), int(h.group(1))) if w and h else (0, 0)


# ---------------------------------------------------------------- back page (standard)
SITE = "https://thetripnow.com/"


def site_status() -> int:
    req = urllib.request.Request(SITE, headers={"User-Agent": "Mozilla/5.0 (TheTripNow book builder)"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status
    except Exception as e:  # noqa: BLE001
        return getattr(e, "code", 0) or 0


def utm_url() -> str:
    campaign = CFG.get("utm_campaign", "book")
    return f"{SITE}?utm_source=book&utm_medium=print&utm_campaign={campaign}"


BACK_TITLE = "Plan your next trip"
BACK_TEXT = ("More pocket itineraries, maps and travel ideas from TheTripNow, plus prints and gifts "
             "from the places in this book.")
# R58: books get feedback through their built-in reviews; ask for one on the back page.
REVIEW_TEXT = ("Enjoyed this guide? A short review on Amazon helps other travelers find it. "
               "Spotted something that changed? Tell us at thetripnow.com and we'll fix it in the next edition.")


# R58 (honeystorm-backend#52, 2026-11-17): every book asks for feedback on the brand site, which has the Feedback button.
FEEDBACK_TEXT = "Tell us what you think: we read every message. Visit thetripnow.com and press the Feedback button."


def back_note() -> str:
    """The back page's last line (R58): book.json `back_note` "review" asks for an Amazon review (Napa & Sonoma, #9,
    as the Owner approved it); the default is the feedback line (Big Sur, #44)."""
    return REVIEW_TEXT if CFG.get("back_note") == "review" else FEEDBACK_TEXT


def back_page_md(link: bool) -> str:
    target = f"[thetripnow.com]({utm_url()})" if link else "**thetripnow.com**"
    return f"# {BACK_TITLE}\n\n{BACK_TEXT}\n\n{target}\n\n{back_note()}\n"


# ---------------------------------------------------------------- interior PDF
def build_interior() -> Path:
    t = html.escape(CFG["title"])
    parts = [f"""
<section class="title-page"><h1 class="book-title">{t}</h1>
<p class="book-subtitle">{html.escape(CFG['subtitle'])}</p><p class="imprint">{html.escape(CFG['author'])}</p></section>
<section class="copyright"><p>{html.escape(CFG['rights'])}</p>
<p>Prices, opening hours and rules change. Every fact was checked on {html.escape(CFG.get('checked', '14 November 2026'))}; check before you go.</p></section>
<section class="toc"><h1>Contents</h1><ol>"""]
    toc = []
    body = []
    pg = bool(CFG.get("toc_pages"))      # opt-in: page numbers in the Contents (WeasyPrint target-counter)
    def li(label: str, anchor: str) -> str:
        return f'<li><a href="#{anchor}">{html.escape(label)}</a></li>' if pg else f"<li>{html.escape(label)}</li>"
    for n, (ch, md) in enumerate(chapters()):
        title = re.search(r"^# (.+)$", md, re.M).group(1)
        toc.append(li(title, f"ch{n}"))
        img = f'<img class="section-art" src="{ROOT / ch["image"]}" alt="">' if ch["image"] else ""
        if ch["image"] and short_credit(ch["image"]):
            img += f'<p class="photo-credit">{html.escape(short_credit(ch["image"]))}</p>'
        body.append(f'<section class="chapter" id="ch{n}">{img}{addr_nohyphen(md_to_html(md))}</section>')
    extras = (li(BACK_TITLE, "back") + li("Sources and credits", "credits") + li("Trip planner", "planner0")) if pg \
        else f"<li>{BACK_TITLE}</li><li>Sources and credits</li><li>Trip planner</li>"
    if CFG.get("toc_extras_unnumbered"):   # #9 review: the back pages aren't chapters
        parts.append("".join(toc) + f'</ol><ul class="toc-extra">{extras}</ul></section>')
    else:
        parts.append("".join(toc) + extras + "</ol></section>")
    if CFG.get("at_a_glance"):             # one page after the contents (src/<file>.md)
        glance = (SRC / f"{CFG['at_a_glance']}.md").read_text(encoding="utf-8")
        parts.append(f'<section class="chapter glance">{addr_nohyphen(md_to_html(reader_text(glance)))}</section>')
    parts += body
    def nb(t: str) -> str:  # never hyphenate the brand or the address ("TheT-ripNow", "thet-ripnow.com")
        t = html.escape(t)
        for w in ("thetripnow.com", "TheTripNow"):
            t = t.replace(w, f'<span style="hyphens: none; white-space: nowrap">{w}</span>')
        return t
    parts.append(f'<section class="chapter back-page" id="back"><h1>{BACK_TITLE}</h1><p>{nb(BACK_TEXT)}</p>'
                 f'<p class="back-url">thetripnow.com</p><p class="review-ask">{nb(back_note())}</p></section>')
    sources = credits_md() if CFG.get("sources_note") else (SRC / "sources.md").read_text(encoding="utf-8")
    parts.append(f'<section class="chapter credits" id="credits">{addr_nohyphen(md_to_html(sources))}</section>')
    if CFG.get("planners"):                # #9 re-score: one page per day, grey example hints (R100)
        for pi, p in enumerate(CFG["planners"]):
            hints = "".join(f'<div class="line example">{html.escape(x)}</div>' for x in p.get("examples", []))
            lines = "".join('<div class="line"></div>' for _ in range(22 - len(p.get("examples", []))))
            parts.append(f'<section class="planner" id="planner{pi}"><h2>{html.escape(p["title"])}</h2>'
                         f'{"<p class=planner-row>Date ____________</p>" if p.get("date", True) else ""}{hints}{lines}</section>')
        for _ in range(CFG.get("notes_pages", 0)):
            lines = "".join('<div class="line"></div>' for _ in range(24))
            parts.append(f'<section class="planner"><h2>Notes</h2>{lines}</section>')
    else:
        for i in range(CFG["planner_pages"]):
            lines = "".join('<div class="line"></div>' for _ in range(22))
            parts.append(f'<section class="planner"><h2>Trip planner {i + 1}</h2>'
                         f'<p class="planner-row">Day ______ &nbsp; Date ____________</p>{lines}</section>')
    doc = (f'<!doctype html><html lang="{CFG["lang"]}"><head><meta charset="utf-8">'
           f'<title>{t}</title><link rel="stylesheet" href="{STYLE / "print.css"}"></head>'
           f'<body>{"".join(parts)}</body></html>')
    src = OUT / "interior.html"
    src.write_text(doc, encoding="utf-8")
    pdf = OUT / "interior.pdf"
    r = run(["weasyprint", str(src), str(pdf)])
    if r.returncode:
        sys.exit(r.stderr)
    return pdf


# ---------------------------------------------------------------- EPUB
def epub_image(path) -> str:
    """For the EPUB only: a downscaled JPEG copy when book.json sets epub_image_max_px (print keeps the originals)."""
    mx = CFG.get("epub_image_max_px")
    if not mx:
        return str(path)
    path = Path(path)
    dst = OUT / "epub-img" / (path.stem + ".jpg")
    dst.parent.mkdir(exist_ok=True)
    r = run(["sips", "-Z", str(mx), "--setProperty", "format", "jpeg",
             "--setProperty", "formatOptions", str(CFG.get("epub_jpeg_quality", 70)), str(path), "--out", str(dst)])
    if r.returncode:
        sys.exit(r.stderr)
    return str(dst)


def build_epub() -> Path:
    md = [f"% {CFG['title']}\n% {CFG['author']}\n"]
    if CFG.get("at_a_glance"):
        md.append(reader_text((SRC / f"{CFG['at_a_glance']}.md").read_text(encoding="utf-8")))
    for ch, text in chapters():
        if ch["image"]:
            cap = f"\n\n*{short_credit(ch['image'])}*" if short_credit(ch["image"]) else ""
            text = re.sub(r"^(# .+)$", rf"\1\n\n![]({ROOT / ch['image']}){cap}", text, count=1, flags=re.M)
        md.append(text)
    md.append(back_page_md(link=True))
    md.append(credits_md() if CFG.get("sources_note") else (SRC / "sources.md").read_text(encoding="utf-8"))
    text = "\n\n".join(md)
    text = re.sub(r"\]\((/[^)]+\.(?:png|jpe?g))\)", lambda m: "](" + epub_image(m.group(1)) + ")", text)
    src = OUT / "book.md"
    src.write_text(text, encoding="utf-8")
    epub = OUT / "book.epub"
    r = run(["pandoc", "-f", "markdown-tex_math_dollars", str(src), "-o", str(epub), "--toc", "--split-level=1",
             "--css", str(STYLE / "epub.css"),
             "--epub-cover-image", epub_image(OUT / "kindle-cover.jpg"),
             "--metadata", f"lang={CFG['lang']}",
             "--metadata", f"rights={CFG['rights']}",
             "--metadata", f"subtitle={CFG['subtitle']}"])
    if r.returncode:
        sys.exit(r.stderr)
    return epub


# ---------------------------------------------------------------- wrap cover
def build_cover(pages: int) -> tuple[Path, float]:
    spine = round(pages * CFG["spine_in_per_page"][CFG["paper"]], 4)
    w = 2 * TRIM_W + spine + 2 * BLEED
    h = TRIM_H + 2 * BLEED
    front_x = BLEED + TRIM_W + spine
    t, sub = html.escape(CFG["title"]), html.escape(CFG["subtitle"])
    art = ROOT / CFG["cover_image"]
    # book.json "back_url": print the site on the back cover (#9 review)
    back_url = f'<p style="margin-top:0.3in;font-family:Noto Sans;font-weight:700;font-size:14pt">{html.escape(CFG["back_url"])}</p>' if CFG.get("back_url") else ""
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size: {w}in {h}in; margin: 0; }}
body {{ margin: 0; font-family: 'Noto Sans'; }}
.back  {{ position: absolute; left: 0; top: 0; width: {BLEED + TRIM_W}in; height: {h}in; background: #F1E7D0; }}
.spine {{ position: absolute; left: {BLEED + TRIM_W}in; top: 0; width: {spine}in; height: {h}in; background: #123B3B; }}
.front {{ position: absolute; left: {front_x}in; top: 0; width: {TRIM_W + BLEED}in; height: {h}in;
          background: url('{art}') center / cover no-repeat; }}
.title {{ position: absolute; left: {front_x + 0.5}in; top: {BLEED + 0.6}in; width: {TRIM_W - 1}in;
          color: #123B3B; font-family: 'Noto Serif'; font-weight: 700; font-size: 30pt; line-height: 1.1; text-align: center;
          background: rgba(241, 231, 208, 0.88); padding: 14pt 10pt; border-radius: 4pt; }}
.subtitle {{ display: block; font-family: 'Noto Sans'; font-weight: 400; font-size: 12pt; margin-top: 8pt; }}
.blurb {{ position: absolute; left: {BLEED + 0.6}in; top: {BLEED + 1.2}in; width: {TRIM_W - 1.2}in;
          color: #123B3B; font-family: 'Noto Serif'; font-size: 12pt; line-height: 1.5; }}
.barcode {{ position: absolute; left: {BLEED + TRIM_W - 0.25 - 2}in; top: {BLEED + TRIM_H - 0.25 - 1.2}in;
            width: 2in; height: 1.2in; }}   /* KDP prints the barcode here: keep clear */
</style></head><body>
<div class="back"></div><div class="spine"></div><div class="front"></div>
<div class="title">{t}<span class="subtitle">{sub}</span></div>
<div class="blurb">{html.escape(CFG['back_blurb'])}{back_url}</div><div class="barcode"></div>
</body></html>"""
    src = OUT / "cover.html"
    src.write_text(doc, encoding="utf-8")
    pdf = OUT / "cover.pdf"
    r = run(["weasyprint", str(src), str(pdf)])
    if r.returncode:
        sys.exit(r.stderr)
    return pdf, spine


# ---------------------------------------------------------------- kindle cover
def build_kindle_cover(spine: float) -> Path:
    """The Kindle/EPUB front cover: the paperback's front panel (title and art), cut at the trim.
    KDP shows this as the Kindle cover, so it must carry the title (the bare photo did not)."""
    dpi = 300
    full = OUT / "cover-full"
    r = run(["pdftoppm", "-r", str(dpi), "-jpeg", "-jpegopt", "quality=92", "-singlefile", str(OUT / "cover.pdf"), str(full)])
    if r.returncode:
        sys.exit(r.stderr)
    x = round((BLEED + TRIM_W + spine) * dpi)
    y = round(BLEED * dpi)
    w, h = round(TRIM_W * dpi), round(TRIM_H * dpi)
    dst = OUT / "kindle-cover.jpg"
    r = run(["sips", "-c", str(h), str(w), "--cropOffset", str(y), str(x), str(full) + ".jpg", "--out", str(dst)])
    if r.returncode:
        sys.exit(r.stderr)
    (OUT / "cover-full.jpg").unlink(missing_ok=True)
    # Guard (Big Sur 2026-11-15 went live with a bare-photo Kindle cover): the front panel we cut must carry the title.
    pts = 72
    txt = run(["pdftotext", "-x", str(round((BLEED + TRIM_W + spine) * pts)), "-y", str(round(BLEED * pts)),
               "-W", str(round(TRIM_W * pts)), "-H", str(round(TRIM_H * pts)), str(OUT / "cover.pdf"), "-"]).stdout
    first = CFG["title"].split()[0:3]
    if not all(w.lower() in txt.lower() for w in first):
        sys.exit(f"kindle cover check FAILED: the front panel has no title text (looked for {first!r})")
    return dst


# ---------------------------------------------------------------- checks
def pdf_info(pdf: Path) -> dict:
    out = run(["pdfinfo", str(pdf)]).stdout
    pages = int(re.search(r"Pages:\s+(\d+)", out).group(1))
    size = re.search(r"Page size:\s+([\d.]+) x ([\d.]+) pts", out)
    return {"pages": pages, "w_in": float(size.group(1)) / 72, "h_in": float(size.group(2)) / 72}


def fonts_embedded(pdf: Path) -> tuple[bool, str]:
    out = run(["pdffonts", str(pdf)]).stdout
    rows = [r for r in out.splitlines()[2:] if r.strip()]
    names = sorted({r.split()[0].split("+")[-1] for r in rows})
    # columns end with: emb sub uni object ID  -> "emb" is the 5th from the end
    emb = bool(rows) and all(r.split()[-5] == "yes" for r in rows)
    return emb, ", ".join(names)


def main():
    for tool in ("pandoc", "weasyprint", "epubcheck", "pdfinfo", "pdffonts", "pdftoppm", "pdftotext", "sips"):
        need(tool)
    OUT.mkdir(exist_ok=True)
    report = []

    interior = build_interior()
    info = pdf_info(interior)
    emb, names = fonts_embedded(interior)
    report += [
        f"interior.pdf: {info['pages']} pages, {info['w_in']:.3f} x {info['h_in']:.3f} in "
        f"({'OK' if abs(info['w_in'] - TRIM_W) < 0.01 and abs(info['h_in'] - TRIM_H) < 0.01 else 'WRONG SIZE'})",
        f"  KDP paperback minimum 24 pages: {'OK' if info['pages'] >= 24 else 'TOO FEW'}",
        f"  fonts embedded: {'yes' if emb else 'NO'} ({names})",
    ]

    maps = [{"file": "map", "image": c["map"]} for c in CFG["chapters"] if c.get("map")]
    for ch in [c for c in CFG["chapters"] if c["image"]] + maps + [{"file": "cover", "image": CFG["cover_image"]}]:
        w, h = image_px(ROOT / ch["image"])
        width_in = (TRIM_W + 2 * BLEED) if ch["file"] == "cover" else TRIM_W - 1.25
        report.append(f"  image {ch['image']}: {w}x{h}px -> {w / width_in:.0f} dpi at {width_in:.2f} in wide "
                      f"({'OK' if w / width_in >= 300 else 'below 300 dpi'})")

    cover, spine = build_cover(info["pages"])
    cinfo = pdf_info(cover)
    want_w = 2 * TRIM_W + spine + 2 * BLEED
    report += [
        f"cover.pdf: {cinfo['w_in']:.4f} x {cinfo['h_in']:.4f} in; spine {spine} in for {info['pages']} pages "
        f"on {CFG['paper']} paper (expected {want_w:.4f} x {TRIM_H + 2 * BLEED:.4f}: "
        f"{'OK' if abs(cinfo['w_in'] - want_w) < 0.01 else 'MISMATCH'})",
        f"  spine text: {'allowed' if info['pages'] > 79 else 'not allowed under 80 pages (KDP), spine left plain'}",
    ]

    kc = build_kindle_cover(spine)
    kw, kh = image_px(kc)
    report.append(f"kindle-cover.jpg: {kw}x{kh}px, front panel; title text found on it: OK (upload this as the KDP Kindle cover; "
                  f"{'OK' if kh >= 2500 else 'under 2500 px tall'})")

    epub = build_epub()
    r = run(["epubcheck", str(epub)])
    tail = [l for l in (r.stdout + r.stderr).splitlines() if re.search(r"Messages:|ERROR|FATAL|No errors", l)]
    size_mb = epub.stat().st_size / 1e6
    report += [f"book.epub: {size_mb:.2f} MB ({'OK' if size_mb < 2 else 'over 2 MB: set epub_image_max_px'}); EPUBCheck exit {r.returncode}"] + [f"  {l}" for l in tail[-6:]]

    code = site_status()
    report.append(f"back page: {SITE} -> HTTP {code} ({'OK' if code == 200 else 'CHECK THE LINK'}); "
                  f"EPUB link {utm_url()}; print shows 'thetripnow.com'")
    if CFG.get("relative_paths"):           # no machine paths in out/book.md, interior.html, cover.html
        for f in ("book.md", "interior.html", "cover.html"):
            t = (OUT / f).read_text(encoding="utf-8")
            (OUT / f).write_text(t.replace(f"{OUT}/", "").replace(f"{ROOT}/", "../"), encoding="utf-8")
    (OUT / "report.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
