#!/usr/bin/env python3
"""Prototype book builder for the TheTripNow test ebook (the-trip-now-www#8).

It is the starting point for the 88eggs `book-builder-task`. From the chapter
Markdown and the images it produces:

  out/book.epub      Kindle/reflowable EPUB 3 (pandoc)
  out/interior.pdf   print interior, 6x9 in, KDP margins, fonts embedded (WeasyPrint)
  out/cover.pdf      wrap cover: back + spine + front, with bleed (WeasyPrint)
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
CITE = re.compile(r"\s*\[(?:[A-Z]\d+|(?:STAY|EAT)-[A-Z]+)\](?:\[(?:[A-Z]\d+|(?:STAY|EAT)-[A-Z]+)\])*")


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def need(tool):
    if not shutil.which(tool):
        sys.exit(f"missing tool: {tool}")


def reader_text(md: str) -> str:
    """Strip the [F#] fact citations, which are for checking, not for readers."""
    return CITE.sub("", md)


def chapters():
    for ch in CFG["chapters"]:
        md = reader_text((SRC / "chapters" / f"{ch['file']}.md").read_text(encoding="utf-8"))
        if ch.get("map"):
            # optional day map, placed at the end of the chapter (print and EPUB)
            md += f"\n\n![Map of {ch.get('map_title', 'the day')}]({ROOT / ch['map']}){{.day-map}}\n"
        yield ch, md


def md_to_html(md: str) -> str:
    r = run(["pandoc", "-f", "markdown-tex_math_dollars", "-t", "html5"], input=md)
    if r.returncode:
        sys.exit(r.stderr)
    return r.stdout


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


def back_page_md(link: bool) -> str:
    target = f"[thetripnow.com]({utm_url()})" if link else "**thetripnow.com**"
    return f"# {BACK_TITLE}\n\n{BACK_TEXT}\n\n{target}\n"


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
    for ch, md in chapters():
        title = re.search(r"^# (.+)$", md, re.M).group(1)
        toc.append(f"<li>{html.escape(title)}</li>")
        img = f'<img class="section-art" src="{ROOT / ch["image"]}" alt="">' if ch["image"] else ""
        body.append(f'<section class="chapter">{img}{md_to_html(md)}</section>')
    toc.append(f"<li>{BACK_TITLE}</li><li>Sources and credits</li><li>Trip planner</li>")
    parts.append("".join(toc) + "</ol></section>")
    parts += body
    parts.append(f'<section class="chapter back-page"><h1>{BACK_TITLE}</h1><p>{html.escape(BACK_TEXT)}</p>'
                 f'<p class="back-url">thetripnow.com</p></section>')
    sources = (SRC / "sources.md").read_text(encoding="utf-8")
    parts.append(f'<section class="chapter">{md_to_html(sources)}</section>')
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
def build_epub() -> Path:
    md = [f"% {CFG['title']}\n% {CFG['author']}\n"]
    for ch, text in chapters():
        if ch["image"]:
            text = re.sub(r"^(# .+)$", rf"\1\n\n![]({ROOT / ch['image']})", text, count=1, flags=re.M)
        md.append(text)
    md.append(back_page_md(link=True))
    md.append((SRC / "sources.md").read_text(encoding="utf-8"))
    src = OUT / "book.md"
    src.write_text("\n\n".join(md), encoding="utf-8")
    epub = OUT / "book.epub"
    r = run(["pandoc", "-f", "markdown-tex_math_dollars", str(src), "-o", str(epub), "--toc", "--split-level=1",
             "--css", str(STYLE / "epub.css"),
             "--epub-cover-image", str(ROOT / CFG["cover_image"]),
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
<div class="blurb">{html.escape(CFG['back_blurb'])}</div><div class="barcode"></div>
</body></html>"""
    src = OUT / "cover.html"
    src.write_text(doc, encoding="utf-8")
    pdf = OUT / "cover.pdf"
    r = run(["weasyprint", str(src), str(pdf)])
    if r.returncode:
        sys.exit(r.stderr)
    return pdf, spine


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
    for tool in ("pandoc", "weasyprint", "epubcheck", "pdfinfo", "pdffonts"):
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

    epub = build_epub()
    r = run(["epubcheck", str(epub)])
    tail = [l for l in (r.stdout + r.stderr).splitlines() if re.search(r"Messages:|ERROR|FATAL|No errors", l)]
    report += [f"book.epub: EPUBCheck exit {r.returncode}"] + [f"  {l}" for l in tail[-6:]]

    code = site_status()
    report.append(f"back page: {SITE} -> HTTP {code} ({'OK' if code == 200 else 'CHECK THE LINK'}); "
                  f"EPUB link {utm_url()}; print shows 'thetripnow.com'")
    (OUT / "report.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
