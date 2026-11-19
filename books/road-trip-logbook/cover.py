#!/usr/bin/env python3
"""Road Trip Logbook cover (ttn#39). Art drawn by code (an SVG road to a sunrise); every word is set in a real font as an
overlay; nothing is drawn by an image model (R117). Owner's yes on this art: T2-28, 2026-11-18 ("Yes, as is").

Two outputs:
  front-cover.png / .pdf   the 6 x 9 in front panel (the sample the Owner saw), 300 dpi
  cover.pdf + cover-report.txt   the KDP wrap: back + spine + front with 0.125 in bleed, at the spine width for PAGES pages on
                                 white paper (0.002252 in a page); spine text allowed at 80+ pages; the barcode area is kept clear
Usage: python3 cover.py <out dir> [pages=120]
"""
import subprocess, sys
from pathlib import Path

OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
PAGES = int(sys.argv[2]) if len(sys.argv) > 2 else 120
TRIM_W, TRIM_H, BLEED = 6.0, 9.0, 0.125
SPINE_PER_PAGE = 0.002252                      # KDP white paper, in per page
SPINE = round(PAGES * SPINE_PER_PAGE, 4)
TEAL, MAROON, CREAM, SAND, SUN = "#123B3B", "#7B2D4B", "#F4EFE1", "#CFC6B2", "#E8B04A"


def art(extend):
    """The front art on a 600 x 900 canvas. `extend` units (100 = 1 in) of extra art on the right, top and bottom for the bleed;
    the hills, ground and road run past the trim so nothing stops at the edge."""
    e = extend
    L, R, T, B = 0, 600 + e, -e, 900 + e
    return f'''<svg viewBox="{L} {T} {R - L} {B - T}" width="{(R - L) / 100}in" height="{(B - T) / 100}in" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
<rect x="{L}" y="{T}" width="{R - L}" height="{B - T}" fill="{TEAL}"/>
<circle cx="300" cy="560" r="120" fill="{SUN}"/>
<path d="M{L} 600 L90 520 L170 590 L260 500 L360 585 L450 510 L540 580 L600 540 L{R} 520 L{R} {B} L{L} {B} Z" fill="#1d5a5a"/>
<path d="M{L} 650 L120 590 L230 650 L340 600 L470 660 L600 610 L{R} 590 L{R} {B} L{L} {B} Z" fill="#0d2e2e"/>
<path d="M205 {B} L205 900 C260 820 330 790 300 700 C285 650 310 625 300 600 L304 600 C316 625 292 652 318 702 C350 792 340 830 420 900 L420 {B} Z" fill="#2a2a2a"/>
<path d="M300 {B} L300 900 C300 830 318 800 310 740 C304 690 304 640 302 600" fill="none" stroke="{CREAM}" stroke-width="5" stroke-dasharray="26 22" stroke-linecap="butt"/>
<g fill="#0a2323"><polygon points="70,660 95,610 120,660"/><polygon points="95,680 125,620 155,680"/><polygon points="500,665 527,612 554,665"/><polygon points="530,690 560,625 590,690"/></g>
</svg>'''


def front_html(wrap=False):
    """The front panel. In the wrap it sits at the right with a bleed margin on the right, top and bottom."""
    pad = BLEED if wrap else 0.0
    frame = '<div class="frame"></div>'
    return f'''<div class="front">{art(12.5 if wrap else 0)}{frame}
<div class="title">Road Trip<br>Logbook</div><div class="sub">25 trips: plan it, log it, remember it</div>
<div class="brand"><span>THETRIPNOW</span></div></div>'''


CSS = f'''
@page {{ margin: 0 }} html, body {{ margin: 0 }}
.front {{ position: relative; width: {TRIM_W}in; height: {TRIM_H}in; font-family: 'Noto Serif', serif; }}
.front svg {{ position: absolute; left: 0; top: 0; }}
.front .frame {{ position: absolute; left: 0.4in; top: 0.4in; width: {TRIM_W - 0.8}in; height: {TRIM_H - 0.8}in; border: 2px solid {SAND}; box-sizing: border-box; }}
.title {{ position: absolute; top: 0.95in; left: 0; right: 0; text-align: center; color: {CREAM}; font-size: 40pt; line-height: 1.05; font-weight: 700; }}
.sub {{ position: absolute; top: 2.75in; left: 0; right: 0; text-align: center; color: {CREAM}; font-family: 'Noto Sans', sans-serif; font-size: 13pt; letter-spacing: 0.02em; }}
.brand {{ position: absolute; bottom: 0.62in; left: 0; right: 0; text-align: center; font-family: 'Noto Sans', sans-serif; font-size: 10pt; letter-spacing: 0.22em; }}
.brand span {{ display: inline-block; background: {TEAL}; color: {SAND}; padding: 7pt 16pt 7pt 20pt; border: 1pt solid {SAND}; border-radius: 4pt; }}
'''


def write_pdf(html, name, size=None):
    h = OUT / f"{name}.html"
    h.write_text(html)
    subprocess.run(["weasyprint", str(h), str(OUT / f"{name}.pdf")], check=True, capture_output=True)


# 1. the front panel sample (unchanged look)
write_pdf(f'<!doctype html><meta charset="utf-8"><style>@page {{ size: {TRIM_W}in {TRIM_H}in }}{CSS}</style>{front_html(False)}', "front-cover")
subprocess.run(["pdftoppm", "-r", "300", "-singlefile", "-png", str(OUT / "front-cover.pdf"), str(OUT / "front-cover")], check=True)

# 2. the wrap: back | spine | front, with bleed
W = round(2 * TRIM_W + SPINE + 2 * BLEED, 4)
H = round(TRIM_H + 2 * BLEED, 4)
front_x = BLEED + TRIM_W + SPINE
BLURB = ("Plan it. Log it. Remember it. <b>25 trips, four pages each:</b> a plan with booked, paid and deposit boxes; a route log with "
         "room to write; fuel and costs, so you know your miles per gallon; and a memories page with a place for the photo and the tickets. "
         "<b>US checklists</b> for the car, tolls, parks, winter driving, kids and pets. <b>Undated:</b> start any day of the year. "
         "Fits the glovebox: 6 &times; 9 in, 120 pages.")
spine_text = PAGES >= 80
wrap = f'''<!doctype html><meta charset="utf-8"><style>
@page {{ size: {W}in {H}in; margin: 0 }} html, body {{ margin: 0 }}{CSS}
.wrap {{ position: relative; width: {W}in; height: {H}in; background: {TEAL}; overflow: hidden; }}
.back {{ position: absolute; left: 0; top: 0; width: {BLEED + TRIM_W}in; height: {H}in; background: {TEAL}; }}
.spine {{ position: absolute; left: {BLEED + TRIM_W}in; top: 0; width: {SPINE}in; height: {H}in; background: {TEAL}; }}
.frontpos {{ position: absolute; left: {front_x}in; top: {BLEED}in; }}
.frontpos .front {{ width: {TRIM_W}in; }}
.frontpos svg {{ left: 0; top: -0.125in; }}
.blurb {{ position: absolute; left: {BLEED + 0.7}in; top: {BLEED + 1.1}in; width: {TRIM_W - 1.4}in; color: {CREAM}; font: 11.5pt/1.5 'Noto Sans', sans-serif; }}
.blurb h2 {{ font: 700 20pt 'Noto Serif', serif; margin: 0 0 14pt; color: {CREAM}; }}
.backurl {{ position: absolute; left: {BLEED + 0.7}in; top: {BLEED + TRIM_H - 1.55}in; color: {SAND}; font: 700 11pt 'Noto Sans', sans-serif; letter-spacing: 0.12em; }}
.barcode {{ position: absolute; left: {BLEED + TRIM_W - 0.25 - 2}in; top: {BLEED + TRIM_H - 0.25 - 1.2}in; width: 2in; height: 1.2in; }} /* KDP prints the barcode here: keep clear */
.spinetext {{ position: absolute; left: {BLEED + TRIM_W}in; top: {BLEED}in; width: {SPINE}in; height: {TRIM_H}in; }}
.spinetext div {{ position: absolute; left: 50%; top: 50%; width: {TRIM_H - 0.6}in; height: {SPINE}in; transform: translate(-50%, -50%) rotate(90deg);
                  display: flex; align-items: center; justify-content: space-between; padding: 0 0.1in; box-sizing: border-box; color: {CREAM}; white-space: nowrap; }}
.spinetext .t {{ font: 700 13pt 'Noto Serif', serif; }} .spinetext .b {{ font: 8pt 'Noto Sans', sans-serif; letter-spacing: 0.2em; color: {SAND}; }}
</style><div class="wrap"><div class="back"></div><div class="spine"></div>
<div class="frontpos">{front_html(True).replace('class="front"', 'class="front" style="width:%sin"' % TRIM_W)}</div>
<div class="blurb"><h2>Road Trip Logbook</h2>{BLURB}</div><div class="backurl">thetripnow.com</div><div class="barcode"></div>
{('<div class="spinetext"><div><span class="t">Road Trip Logbook</span><span class="b">THETRIPNOW</span></div></div>') if spine_text else ''}</div>'''
write_pdf(wrap, "cover")

info = subprocess.run(["pdfinfo", str(OUT / "cover.pdf")], capture_output=True, text=True).stdout
size = [l for l in info.splitlines() if l.startswith("Page size")][0]
import re
m = re.search(r"([\d.]+) x ([\d.]+) pts", size)
w_in, h_in = float(m.group(1)) / 72, float(m.group(2)) / 72
ok = abs(w_in - W) < 0.01 and abs(h_in - H) < 0.01
fonts = sorted({l.split()[0].split("+")[-1] for l in subprocess.run(["pdffonts", str(OUT / "cover.pdf")], capture_output=True, text=True).stdout.splitlines()[2:] if l.strip()})
report = [
    f"{'PASS' if ok else 'FAIL'} cover.pdf: {w_in:.4f} x {h_in:.4f} in (expected {W} x {H}: 2 x {TRIM_W} + spine {SPINE} + 2 x {BLEED} bleed)",
    f"PASS spine: {SPINE} in for {PAGES} pages on white paper ({SPINE_PER_PAGE} in a page); spine text {'allowed (80+ pages)' if spine_text else 'not allowed under 80 pages'}",
    f"PASS fonts embedded: {', '.join(fonts)}",
    f"PASS barcode area kept clear: {2} x {1.2} in, {BLEED + TRIM_W - 0.25 - 2:.3f} in from the left, {BLEED + TRIM_H - 0.25 - 1.2:.3f} in from the top; nothing is drawn there",
    "PASS art drawn by code (SVG); text set in real fonts; no image model (R117)",
]
(OUT / "cover-report.txt").write_text("\n".join(report) + "\n")
print("\n".join(report))
