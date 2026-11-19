#!/usr/bin/env python3
"""Front cover SAMPLE for the Road Trip Logbook (ttn#39). Art drawn by code (an SVG road to a sunrise), text set in real
fonts as an overlay; nothing is drawn by an image model. 6 x 9 in front panel at 300 dpi (the wrap, with spine and back, is
built after the Owner's yes at KDP's spine width for 120 pages on white paper).
Usage: python3 cover.py <out dir>      writes front-cover.html, front-cover.pdf, front-cover.png
"""
import subprocess, sys
from pathlib import Path

OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
TEAL, MAROON, CREAM, SAND, SUN = "#123B3B", "#7B2D4B", "#F4EFE1", "#CFC6B2", "#E8B04A"
svg = f'''<svg viewBox="0 0 600 900" width="6in" height="9in" xmlns="http://www.w3.org/2000/svg">
<rect width="600" height="900" fill="{TEAL}"/>
<circle cx="300" cy="560" r="120" fill="{SUN}"/>
<path d="M0 600 L90 520 L170 590 L260 500 L360 585 L450 510 L540 580 L600 540 L600 900 L0 900 Z" fill="#1d5a5a"/>
<path d="M0 650 L120 590 L230 650 L340 600 L470 660 L600 610 L600 900 L0 900 Z" fill="#0d2e2e"/>
<path d="M205 900 C260 820 330 790 300 700 C285 650 310 625 300 600 L304 600 C316 625 292 652 318 702 C350 792 340 830 420 900 Z" fill="#2a2a2a"/>
<path d="M300 900 C300 830 318 800 310 740 C304 690 304 640 302 600" fill="none" stroke="{CREAM}" stroke-width="5" stroke-dasharray="26 22" stroke-linecap="butt"/>
<g fill="#0a2323"><polygon points="70,660 95,610 120,660"/><polygon points="95,680 125,620 155,680"/><polygon points="500,665 527,612 554,665"/><polygon points="530,690 560,625 590,690"/></g>
<rect x="40" y="40" width="520" height="820" fill="none" stroke="{SAND}" stroke-width="2"/>
</svg>'''
html = f'''<!doctype html><meta charset="utf-8"><style>
@page {{ size: 6in 9in; margin: 0 }} html, body {{ margin: 0 }}
.wrap {{ position: relative; width: 6in; height: 9in; font-family: 'Noto Serif', serif; }}
.wrap svg {{ position: absolute; left: 0; top: 0; }}
.title {{ position: absolute; top: 0.95in; left: 0; right: 0; text-align: center; color: {CREAM}; font-size: 40pt; line-height: 1.05; font-weight: 700; }}
.sub {{ position: absolute; top: 2.75in; left: 0; right: 0; text-align: center; color: {CREAM}; font-family: 'Noto Sans', sans-serif; font-size: 13pt; letter-spacing: 0.02em; }}
.brand {{ position: absolute; bottom: 0.62in; left: 0; right: 0; text-align: center; font-family: 'Noto Sans', sans-serif; font-size: 10pt; letter-spacing: 0.22em; }} .brand span {{ display: inline-block; background: {TEAL}; color: {SAND}; padding: 7pt 16pt 7pt 20pt; border: 1pt solid {SAND}; border-radius: 4pt; }}
</style><div class="wrap">{svg}<div class="title">Road Trip<br>Logbook</div><div class="sub">25 trips: plan it, log it, remember it</div><div class="brand"><span>THETRIPNOW</span></div></div>'''
(OUT / "front-cover.html").write_text(html)
subprocess.run(["weasyprint", str(OUT / "front-cover.html"), str(OUT / "front-cover.pdf")], check=True, capture_output=True)
subprocess.run(["pdftoppm", "-r", "300", "-singlefile", "-png", str(OUT / "front-cover.pdf"), str(OUT / "front-cover")], check=True)
