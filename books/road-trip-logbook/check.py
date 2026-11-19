#!/usr/bin/env python3
"""Checks for the logbook interior: trim, page count, fonts, and that NOTHING is printed within 0.25 in of any trim edge
(the tabs included: it renders every page and looks at the pixels). Usage: python3 check.py interior.pdf"""
import subprocess, sys, tempfile, glob
from pathlib import Path
from PIL import Image
pdf = sys.argv[1]
info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
pages = int([l for l in info.splitlines() if l.startswith("Pages:")][0].split()[1])
size = [l for l in info.splitlines() if l.startswith("Page size:")][0]
fonts = subprocess.run(["pdffonts", pdf], capture_output=True, text=True).stdout.splitlines()[2:]
names = sorted({l.split()[0].split("+")[-1] for l in fonts if l.strip()})
ok = True
def line(label, good, text):
    global ok
    ok &= good
    print(("PASS " if good else "FAIL ") + label + ": " + text)
line("trim", "432 x 648" in size, size.split(":", 1)[1].strip() + " (6 x 9 in)")
line("pages", 24 <= pages <= 828 and pages % 2 == 0, f"{pages} (KDP minimum 24, even)")
line("fonts embedded", all("Noto" in n for n in names), ", ".join(names))
DPI, EDGE = 60, 0.25
bad = []
with tempfile.TemporaryDirectory() as d:
    subprocess.run(["pdftoppm", "-r", str(DPI), "-png", pdf, d + "/p"], check=True)
    for f in sorted(glob.glob(d + "/p-*.png")):
        im = Image.open(f).convert("L"); w, h = im.size; m = round(EDGE * DPI)
        for box in ((0, 0, w, m), (0, h - m, w, h), (0, 0, m, h), (w - m, 0, w, h)):
            if im.crop(box).getextrema()[0] < 200:
                bad.append(Path(f).stem); break
line("nothing within 0.25 in of the trim edge", not bad, "all pages clear" if not bad else "ink in the edge zone on pages " + ", ".join(b.split("-")[-1] for b in bad[:12]))
sys.exit(0 if ok else 1)
