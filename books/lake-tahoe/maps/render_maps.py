#!/usr/bin/env python3
"""Render the Lake Tahoe in 3 Days day maps from OpenStreetMap data (© OpenStreetMap contributors, ODbL).
Adapted from books/napa-sonoma/maps/render_maps.py (lakes instead of rivers). Inputs, all from OSM on 2026-11-18:
  maps/data/roads.json  Overpass (overpass.private.coffee): motorway, trunk and primary roads in 38.84,-120.32,39.40,-119.88;
  maps/data/lakes.json  Nominatim polygons of Lake Tahoe (relation 1823287) and Donner Lake (6659033);
  maps/data/stops.json  Nominatim positions of the stops (osm id and name recorded per stop).
Output: images/map-<day>.png, 4.75 in wide at 300 dpi (1425 px), drawn at 2x and downsampled.
Usage: python3 render_maps.py <books/lake-tahoe>
"""
import json, math, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(sys.argv[1])
FONT = str(Path.home() / "Library/Fonts/NotoSans-Regular.ttf")
BOLD = str(Path.home() / "Library/Fonts/NotoSans-Bold.ttf")
LAND, ROAD, MAIN, WATER, INK, PIN = "#F4EFE1", "#CFC6B2", "#7B2D4B", "#8FB8C8", "#1E3A3A", "#3B1F2B"
OUT_W, SCALE = 1425, 2
S = json.loads((ROOT / "maps/data/stops.json").read_text())
pos = lambda k: (S[k]["lat"], S[k]["lon"])
MAPS = {
    "day1": dict(title="Day 1: South Lake Tahoe and Emerald Bay", bbox=(38.915, -120.17, 39.015, -119.90), main=("US 50", "CA 89"),
                 main_label="US-50 and Highway 89", legend="tr",
                 stops=[("Heavenly Village", *pos("heavenly")), ("Emerald Bay and Vikingsholm", *pos("vikingsholm")), ("D.L. Bliss State Park", *pos("dlbliss"))],
                 towns=[("SOUTH LAKE TAHOE", 38.9330, -119.9890), ("LAKE TAHOE", 38.9850, -120.0000)]),
    "day2": dict(title="Day 2: The West Shore to Tahoe City", bbox=(39.025, -120.40, 39.225, -120.06), main=("CA 89",),
                 main_label="Highway 89", legend="bl",
                 stops=[("Sugar Pine Point (Ehrman Mansion)", *pos("sugarpine")), ("Tahoe City", *pos("tahoecity")), ("Palisades Tahoe", *pos("olympicvalley"))],
                 towns=[("LAKE TAHOE", 39.1000, -120.0900)]),
    "day3": dict(title="Day 3: Truckee and the North Shore", bbox=(39.17, -120.33, 39.36, -119.90), main=("I 80",),
                 main_label="Interstate 80", legend="tr",
                 stops=[("Truckee", *pos("truckee")), ("Donner Memorial State Park (museum)", *pos("donner")), ("Sand Harbor (option)", *pos("sandharbor"))],
                 towns=[("DONNER LAKE", 39.3070, -120.2640), ("LAKE TAHOE", 39.1900, -120.0300)]),
}
ROADS = json.loads((ROOT / "maps/data/roads.json").read_text())["elements"]
LAKES = json.loads((ROOT / "maps/data/lakes.json").read_text())


def rings(gj):
    if gj["type"] == "Polygon":
        return [gj["coordinates"]]
    return gj["coordinates"]


def render(key, m):
    s, w, n, e = m["bbox"]
    k = math.cos(math.radians((s + n) / 2))
    W = OUT_W * SCALE
    H = round(W * (n - s) / ((e - w) * k))
    P = lambda lat, lon: ((lon - w) / (e - w) * W, (n - lat) / (n - s) * H)
    img = Image.new("RGB", (W, H), LAND)
    d = ImageDraw.Draw(img)
    for lake in LAKES.values():
        for poly in rings(lake["geojson"]):
            d.polygon([P(lat, lon) for lon, lat in poly[0]], fill=WATER)
            for hole in poly[1:]:
                d.polygon([P(lat, lon) for lon, lat in hole], fill=LAND)
    for main in (False, True):
        for x in ROADS:
            t = x["tags"]
            is_main = any(r in t.get("ref", "").split(";") for r in m["main"])
            if is_main != main:
                continue
            width = (8 if is_main else {"motorway": 5, "trunk": 5, "primary": 4}.get(t["highway"], 3)) * SCALE
            d.line([P(p["lat"], p["lon"]) for p in x["geometry"]], fill=MAIN if is_main else ROAD, width=width, joint="curve")
    tf = ImageFont.truetype(FONT, 26 * SCALE)
    for name, lat, lon in m["towns"]:
        x, y = P(lat, lon)
        d.text((x, y), name, font=tf, fill="#4F7384" if name == "LAKE TAHOE" or "LAKE" in name else "#6B6252", anchor="mm")
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
    (ROOT / "images").mkdir(exist_ok=True)
    path = ROOT / "images" / f"map-{key}.png"
    out.save(path, dpi=(300, 300))
    print(path.name, out.size, f"{out.size[1] / 300:.2f} in tall")


for key, m in MAPS.items():
    render(key, m)
