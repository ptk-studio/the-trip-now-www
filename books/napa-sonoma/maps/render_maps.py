#!/usr/bin/env python3
"""Render the Napa & Sonoma day maps from OpenStreetMap data (© OpenStreetMap contributors, ODbL).

Inland variant of books/big-sur/maps/render_maps.py: no coastline or sea fill; rivers in blue; the
day's main highway highlighted. Input: maps/data/roads.json (Overpass, 2026-11-17: motorway, trunk,
primary and secondary roads, the Napa River and Sonoma Creek, plus the named minor roads to the Day 3 stops). Stop positions from OSM (same date); Jack London SHP is pinned at its entrance, the west end of London Ranch Road.
Output: images/map-<day>.png, 4.75 in wide at 300 dpi (1425 px), drawn at 2x and downsampled.
Usage: python3 render_maps.py <books/napa-sonoma>
"""
import json, math, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(sys.argv[1])
FONT = str(Path.home() / "Library/Fonts/NotoSans-Regular.ttf")
BOLD = str(Path.home() / "Library/Fonts/NotoSans-Bold.ttf")
LAND, ROAD, MAIN, WATER, INK, PIN = "#F4EFE1", "#CFC6B2", "#7B2D4B", "#8FB8C8", "#1E3A3A", "#3B1F2B"
OUT_W, SCALE = 1425, 2

MAPS = {
    "day1": dict(title="Day 1: Napa and Carneros", bbox=(38.235, -122.385, 38.325, -122.255), main=("CA 29", "CA 121"), main_label="Highways 29 and 121",
                 legend="tr", stops=[("Oxbow Public Market", 38.3017, -122.2817), ("Domaine Carneros", 38.2555, -122.3514)],
                 towns=[("NAPA", 38.293, -122.290), ("CARNEROS", 38.248, -122.325)]),
    "day2": dict(title="Day 2: Up the valley", bbox=(38.380, -122.625, 38.605, -122.355), main=("CA 29",), main_label="Highway 29",
                 legend="bl", stops=[("Robert Mondavi Winery", 38.4415, -122.4094), ("St. Helena, Main Street", 38.5052, -122.4703),
                                     ("Castello di Amorosa", 38.5584, -122.5426), ("Calistoga spas", 38.5788, -122.5797)],
                 towns=[("YOUNTVILLE", 38.404, -122.408), ("ST. HELENA", 38.512, -122.452), ("CALISTOGA", 38.596, -122.548)]),
    "day3": dict(title="Day 3: Sonoma and Glen Ellen", bbox=(38.275, -122.585, 38.370, -122.435), main=("CA 12",), main_label="Highway 12",
                 legend="tr", stops=[("Sonoma Plaza and the Mission", 38.2930, -122.4570), ("Jack London State Historic Park", 38.35709, -122.54388)],
                 towns=[("SONOMA", 38.287, -122.468), ("GLEN ELLEN", 38.366, -122.522)]),
}

DATA = json.loads((ROOT / "maps" / "data" / "roads.json").read_text())["elements"]


def render(key, m):
    s, w, n, e = m["bbox"]
    k = math.cos(math.radians((s + n) / 2))
    W = OUT_W * SCALE
    H = round(W * (n - s) / ((e - w) * k))
    P = lambda lat, lon: ((lon - w) / (e - w) * W, (n - lat) / (n - s) * H)
    img = Image.new("RGB", (W, H), LAND)
    d = ImageDraw.Draw(img)
    for x in DATA:
        if x["tags"].get("waterway"):
            d.line([P(p["lat"], p["lon"]) for p in x["geometry"]], fill=WATER, width=5 * SCALE, joint="curve")
    for main in (False, True):
        for x in DATA:
            t = x["tags"]
            if "highway" not in t:
                continue
            is_main = any(r in t.get("ref", "").split(";") for r in m["main"])
            if is_main != main:
                continue
            width = (8 if is_main else {"motorway": 5, "trunk": 5, "primary": 4, "tertiary": 2, "unclassified": 2}.get(t["highway"], 3)) * SCALE
            d.line([P(p["lat"], p["lon"]) for p in x["geometry"]], fill=MAIN if is_main else ROAD, width=width, joint="curve")
    tf = ImageFont.truetype(FONT, 26 * SCALE)
    for name, lat, lon in m["towns"]:
        x, y = P(lat, lon)
        d.text((x, y), name, font=tf, fill="#6B6252", anchor="mm")
    nf = ImageFont.truetype(BOLD, 30 * SCALE)
    r = 26 * SCALE
    for i, (name, lat, lon) in enumerate(m["stops"], 1):
        x, y = P(lat, lon)
        d.ellipse((x - r, y - r, x + r, y + r), fill=PIN, outline="white", width=4 * SCALE)
        d.text((x, y), str(i), font=nf, fill="white", anchor="mm")
    lf, hf = ImageFont.truetype(FONT, 28 * SCALE), ImageFont.truetype(BOLD, 32 * SCALE)
    lines = [f"{i}  {nm}" for i, (nm, _, _) in enumerate(m["stops"], 1)]
    pad, lh, m0 = 24 * SCALE, 42 * SCALE, 30 * SCALE
    bw = max([d.textlength(l, font=lf) for l in lines] + [d.textlength(m["title"], font=hf)]) + 2 * pad
    bh = pad * 2 + lh * (len(lines) + 2) + 12 * SCALE
    corner = m.get("legend", "tr")
    bx = W - bw - m0 if corner[1] == "r" else m0
    by = m0 if corner[0] == "t" else H - bh - 70 * SCALE
    d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=12 * SCALE, fill="white", outline=INK, width=2 * SCALE)
    d.text((bx + pad, by + pad), m["title"], font=hf, fill=INK)
    for j, l in enumerate(lines):
        d.text((bx + pad, by + pad + lh * (j + 1) + 12 * SCALE), l, font=lf, fill=INK)
    ky = by + pad + lh * (len(lines) + 1) + 12 * SCALE + lh / 2
    d.line((bx + pad, ky, bx + pad + 60 * SCALE, ky), fill=MAIN, width=8 * SCALE)
    d.text((bx + pad + 75 * SCALE, ky), m["main_label"], font=lf, fill=INK, anchor="lm")
    ax = 60 * SCALE if corner[1] == "r" else W - 60 * SCALE
    ay = 60 * SCALE
    d.polygon([(ax, ay - 30 * SCALE), (ax - 16 * SCALE, ay + 16 * SCALE), (ax + 16 * SCALE, ay + 16 * SCALE)], fill=INK)
    d.text((ax, ay + 40 * SCALE), "N", font=nf, fill=INK, anchor="mm")
    cf = ImageFont.truetype(FONT, 20 * SCALE)
    credit = "Map data © OpenStreetMap contributors (ODbL)"
    cw = d.textlength(credit, font=cf)
    d.rectangle((W - cw - 36 * SCALE, H - 48 * SCALE, W, H), fill="white")
    d.text((W - 18 * SCALE, H - 14 * SCALE), credit, font=cf, fill="#444", anchor="rd")
    out = img.resize((OUT_W, round(H / SCALE)), Image.LANCZOS)
    path = ROOT / "images" / f"map-{key}.png"
    out.save(path, dpi=(300, 300))
    print(path.name, out.size, f"{out.size[1] / 300:.2f} in tall")


for key, m in MAPS.items():
    render(key, m)
