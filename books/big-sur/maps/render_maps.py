#!/usr/bin/env python3
"""Render the Big Sur day maps from OpenStreetMap data (© OpenStreetMap contributors, ODbL).

Input: Overpass JSON (coastline + main roads) per map in maps/data/<day>.json.
Output: images/map-<day>.png, 4.75 in wide at 300 dpi (1425 px), drawn at 2x and downsampled.
Usage: python3 render_maps.py <books/big-sur>
"""
import json, math, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(sys.argv[1])
FONT = str(Path.home() / "Library/Fonts/NotoSans-Regular.ttf")
BOLD = str(Path.home() / "Library/Fonts/NotoSans-Bold.ttf")
LAND, SEA, ROAD, HWY1, INK, PIN = "#F4EFE1", "#BCD8E0", "#CFC6B2", "#C8553D", "#1E3A3A", "#123B3B"
OUT_W, SCALE = 1425, 2

MAPS = {
    "day1": dict(title="Day 1: Monterey", bbox=(36.545, -122.000, 36.630, -121.880), sea=(36.60, -121.995), sea2=[(36.627, -121.884)], legend="tl",
                 stops=[("Cannery Row", 36.6135, -121.8979), ("Monterey Bay Aquarium", 36.6181, -121.9016),
                        ("Old Fisherman's Grotto", 36.6044, -121.8929), ("17-Mile Drive: Lone Cypress", 36.5688, -121.9652)],
                 towns=[("MONTEREY", 36.596, -121.897), ("PACIFIC GROVE", 36.624, -121.928)]),
    "day2": dict(title="Day 2: Carmel and Point Lobos", bbox=(36.500, -121.965, 36.570, -121.895), sea=(36.53, -121.962), legend="tl",
                 stops=[("Carmel village", 36.5553, -121.9233), ("Storybook cottages, Torres St", 36.5562, -121.9191),
                        ("Carmel Beach", 36.5512, -121.9299), ("Point Lobos entrance", 36.5159, -121.9382)],
                 towns=[("CARMEL-BY-THE-SEA", 36.561, -121.912), ("CARMEL HIGHLANDS", 36.503, -121.925)]),
    "day3": dict(title="Day 3: Big Sur", bbox=(36.140, -121.990, 36.570, -121.640), sea=(36.30, -121.985), legend="tr",
                 stops=[("Bixby Creek Bridge", 36.3715, -121.9021), ("Pfeiffer Beach", 36.2394, -121.8180),
                        ("Nepenthe", 36.2218, -121.7597), ("McWay Falls", 36.1578, -121.6724)],
                 towns=[("CARMEL", 36.555, -121.905), ("BIG SUR", 36.270, -121.790)]),
}


def render(key, m):
    s, w, n, e = m["bbox"]
    k = math.cos(math.radians((s + n) / 2))
    W = OUT_W * SCALE
    H = round(W * (n - s) / ((e - w) * k))
    P = lambda lat, lon: ((lon - w) / (e - w) * W, (n - lat) / (n - s) * H)
    img = Image.new("RGB", (W, H), LAND)
    d = ImageDraw.Draw(img)
    data = json.loads((ROOT / "maps" / "data" / f"{key}.json").read_text())
    ways = [x for x in data["elements"] if x["type"] == "way" and "geometry" in x]
    for x in ways:
        if x["tags"].get("natural") == "coastline":
            d.line([P(p["lat"], p["lon"]) for p in x["geometry"]], fill=INK, width=3 * SCALE)
    for pt in [m["sea"]] + m.get("sea2", []):
        ImageDraw.floodfill(img, tuple(int(v) for v in P(*pt)), (0xBC, 0xD8, 0xE0), thresh=40)
    for x in ways:
        if x["tags"].get("natural") == "coastline":
            d.line([P(p["lat"], p["lon"]) for p in x["geometry"]], fill="#7FA9B5", width=2 * SCALE)
    for hw1 in (False, True):
        for x in ways:
            t = x["tags"]
            if "highway" not in t:
                continue
            is1 = t.get("ref", "").replace("SR ", "CA ") in ("CA 1",) or "CA 1" in t.get("ref", "")
            if is1 != hw1:
                continue
            width = (7 if is1 else {"motorway": 5, "trunk": 5, "primary": 4}.get(t["highway"], 3)) * SCALE
            d.line([P(p["lat"], p["lon"]) for p in x["geometry"]], fill=HWY1 if is1 else ROAD, width=width, joint="curve")
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
    # legend (stops + Highway 1 key) in the map's chosen corner; north arrow in the other top corner
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
    d.line((bx + pad, ky, bx + pad + 60 * SCALE, ky), fill=HWY1, width=7 * SCALE)
    d.text((bx + pad + 75 * SCALE, ky), "Highway 1", font=lf, fill=INK, anchor="lm")
    ax = W - 60 * SCALE if corner == "tl" else 60 * SCALE
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
