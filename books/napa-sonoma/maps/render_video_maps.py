#!/usr/bin/env python3
"""The six map cards for the Napa video (ptk-studio#224, scenes 2, 5, 10, 11, 13, 20), 1920x1080.

Map data: OpenStreetMap (c) OpenStreetMap contributors, ODbL; credited on every card and in the description.
Same style as the guide maps (render_maps.py). Inputs: maps/data/roads.json (valley roads, 2026-11-17) and
maps/data/video/*.json (SF-Napa roads, Napa River streets, the Napa/Sonoma county line, the two bays; Overpass and
Nominatim, 2026-11-18). No AI image; every label is our own overlay.
Usage: python3 render_video_maps.py <books/napa-sonoma> <out dir>
"""
import json, math, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
FONT = str(Path.home() / "Library/Fonts/NotoSans-Regular.ttf")
BOLD = str(Path.home() / "Library/Fonts/NotoSans-Bold.ttf")
LAND, ROAD, MAIN, ALT, WATER, INK, PIN = "#F4EFE1", "#CFC6B2", "#7B2D4B", "#1F6F78", "#8FB8C8", "#1E3A3A", "#3B1F2B"
W, H, S = 1920, 1080, 2

VALLEY = json.loads((ROOT / "maps/data/roads.json").read_text())["elements"]
V = ROOT / "maps/data/video"
SF = json.loads((V / "sf.json").read_text())["elements"]
OXBOW = json.loads((V / "oxbow.json").read_text())["elements"]
COUNTY = json.loads((V / "county.json").read_text())["elements"]
BAYS = json.loads((V / "bays.json").read_text())


def frame(center_lat, center_lon, height_deg):
    """A 16:9 window centred on a point, `height_deg` of latitude tall."""
    k = math.cos(math.radians(center_lat))
    wd = height_deg * (W / H) / k
    return (center_lat - height_deg / 2, center_lon - wd / 2, center_lat + height_deg / 2, center_lon + wd / 2)


class Card:
    def __init__(self, bbox):
        self.s, self.w, self.n, self.e = bbox
        self.img = Image.new("RGB", (W * S, H * S), LAND)
        self.d = ImageDraw.Draw(self.img)

    def P(self, lat, lon):
        return ((lon - self.w) / (self.e - self.w) * W * S, (self.n - lat) / (self.n - self.s) * H * S)

    def line(self, geom, fill, width, dash=None):
        pts = [self.P(p["lat"], p["lon"]) for p in geom]
        if dash is None:
            self.d.line(pts, fill=fill, width=width * S, joint="curve")
            return
        on, left = True, dash[0] * S
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            seg = math.hypot(x1 - x0, y1 - y0)
            pos = 0.0
            while pos < seg:
                step = min(left, seg - pos)
                if on:
                    a, b = pos / seg, (pos + step) / seg
                    self.d.line([(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a), (x0 + (x1 - x0) * b, y0 + (y1 - y0) * b)], fill=fill, width=width * S)
                pos += step
                left -= step
                if left <= 0:
                    on = not on
                    left = (dash[0] if on else dash[1]) * S

    def bays(self):
        for bay in BAYS["bays"]:
            for ring in bay["rings"]:
                self.d.polygon([self.P(y, x) for x, y in ring], fill=WATER)

    def roads(self, els, main_refs=(), main_names=(), alt_refs=(), base_width=None, skip_minor=False, minor_w=None):
        order = []
        for x in els:
            t = x["tags"]
            if t.get("waterway"):
                self.line(x["geometry"], WATER, (minor_w or 5))
                continue
            if "highway" not in t:
                continue
            refs = t.get("ref", "").split(";")
            kind = "main" if (any(r in main_refs for r in refs) or t.get("name") in main_names) else "alt" if any(r in alt_refs for r in refs) else "road"
            order.append((kind, x))
        for want in ("road", "alt", "main"):
            for kind, x in order:
                if kind != want:
                    continue
                t = x["tags"]
                if kind == "road" and skip_minor and t["highway"] not in ("motorway", "trunk", "primary"):
                    continue
                w = {"main": 9, "alt": 9}.get(kind) or (base_width or {"motorway": 5, "trunk": 5, "primary": 4, "secondary": 2, "tertiary": 2}.get(t["highway"], 2))
                self.line(x["geometry"], MAIN if kind == "main" else ALT if kind == "alt" else ROAD, w)

    def label(self, text, lat, lon, size=34, color="#6B6252", bold=False):
        x, y = self.P(lat, lon)
        self.d.text((x, y), text, font=ImageFont.truetype(BOLD if bold else FONT, size * S), fill=color, anchor="mm", stroke_width=6 * S, stroke_fill=LAND)

    def pin(self, n, lat, lon, caption=None, side="r"):
        x, y = self.P(lat, lon)
        r = 30 * S
        self.d.ellipse((x - r, y - r, x + r, y + r), fill=PIN, outline="white", width=5 * S)
        self.d.text((x, y), str(n), font=ImageFont.truetype(BOLD, 36 * S), fill="white", anchor="mm")
        if caption:
            f = ImageFont.truetype(BOLD, 34 * S)
            tw = self.d.textlength(caption, font=f)
            bx = x + r + 14 * S if side == "r" else x - r - 14 * S - tw - 24 * S
            self.d.rounded_rectangle((bx, y - 28 * S, bx + tw + 24 * S, y + 28 * S), radius=10 * S, fill="white", outline=INK, width=2 * S)
            self.d.text((bx + 12 * S, y), caption, font=f, fill=INK, anchor="lm")

    def banner(self, text, sub=None):
        f, g = ImageFont.truetype(BOLD, 44 * S), ImageFont.truetype(FONT, 30 * S)
        tw = max(self.d.textlength(text, font=f), self.d.textlength(sub or "", font=g)) + 56 * S
        h = (96 if sub else 72) * S
        self.d.rounded_rectangle((40 * S, 40 * S, 40 * S + tw, 40 * S + h), radius=14 * S, fill="white", outline=INK, width=2 * S)
        self.d.text((68 * S, 40 * S + 38 * S if sub else 40 * S + 36 * S), text, font=f, fill=INK, anchor="lm")
        if sub:
            self.d.text((68 * S, 40 * S + 78 * S), sub, font=g, fill="#4A5A50", anchor="lm")

    def legend(self, rows):
        f = ImageFont.truetype(FONT, 30 * S)
        tw = max(self.d.textlength(t, font=f) for _, t, _ in rows) + 120 * S
        h = (len(rows) * 46 + 28) * S
        x0, y0 = 40 * S, (H - 40) * S - h - 38 * S
        self.d.rounded_rectangle((x0, y0, x0 + tw, y0 + h), radius=12 * S, fill="white", outline=INK, width=2 * S)
        for i, (color, text, dashed) in enumerate(rows):
            y = y0 + (14 + 23 + 46 * i) * S
            if dashed:
                self.d.line((x0 + 22 * S, y, x0 + 44 * S, y), fill=color, width=9 * S)
                self.d.line((x0 + 56 * S, y, x0 + 78 * S, y), fill=color, width=9 * S)
            else:
                self.d.line((x0 + 22 * S, y, x0 + 78 * S, y), fill=color, width=9 * S)
            self.d.text((x0 + 98 * S, y), text, font=f, fill=INK, anchor="lm")

    def save(self, name):
        f = ImageFont.truetype(FONT, 24 * S)
        t = "Map data © OpenStreetMap contributors (ODbL)"
        tw = self.d.textlength(t, font=f)
        self.d.rectangle(((W - 40) * S - tw - 20 * S, (H - 40) * S - 36 * S, (W - 40) * S + 12 * S, (H - 40) * S + 12 * S), fill="white")
        self.d.text(((W - 40) * S, (H - 40) * S), t, font=f, fill=INK, anchor="rs")
        self.img.resize((W, H), Image.LANCZOS).save(OUT / name)
        print(name)


def refs_between(els, refs, lat_min, lat_max):
    return [x for x in els if "highway" in x["tags"] and any(r in refs for r in x["tags"].get("ref", "").split(";"))
            and lat_min <= sum(p["lat"] for p in x["geometry"]) / len(x["geometry"]) <= lat_max]


# Scene 2: the whole valley, Napa to Calistoga.
c = Card(frame(38.44, -122.43, 0.42))
c.roads(VALLEY, main_refs=("CA 29",), main_names=("Silverado Trail", "Silverado Trail North"))  # drawn again on top (cheap)
for n, la, lo in (("NAPA", 38.299, -122.286), ("YOUNTVILLE", 38.402, -122.362), ("ST. HELENA", 38.505, -122.470), ("CALISTOGA", 38.579, -122.580)):
    c.label(n, la, lo, 34, bold=True)
c.banner("The Napa Valley", "about 35 miles, Napa to Calistoga")
c.legend([(MAIN, "Highway 29 and the Silverado Trail", False)])
c.save("napa-map-02-valley.png")

# Scene 5: San Francisco to Napa, both routes.
c = Card(frame(37.99, -122.33, 0.82))
c.bays()
A = refs_between(SF, ("US 101", "US 101;CA 1"), 37.80, 38.13) + refs_between(SF, ("CA 37",), 38.0, 38.3) + refs_between(SF, ("CA 29", "CA 12;CA 29"), 38.12, 38.34)
B = refs_between(SF, ("I 80",), 37.79, 38.14)
base = [x for x in SF if "highway" in x["tags"]]
for x in base:
    c.line(x["geometry"], ROAD, 3)
for x in B:
    c.line(x["geometry"], ALT, 9)
for x in A:
    c.line(x["geometry"], MAIN, 9)
for n, la, lo in (("SAN FRANCISCO", 37.745, -122.545), ("OAKLAND", 37.80, -122.17), ("VALLEJO", 38.145, -122.18), ("NAPA", 38.335, -122.30)):
    c.label(n, la, lo, 32, bold=True)
c.label("SAN FRANCISCO BAY", 37.64, -122.27, 26, "#4C7686")
c.label("SAN PABLO BAY", 38.04, -122.36, 26, "#4C7686")
c.banner("San Francisco to Napa", "about 50 miles")
c.legend([(MAIN, "Golden Gate Bridge, Highways 101, 37 and 29", False), (ALT, "Bay Bridge and Interstate 80", False)])
c.save("napa-map-05-routes.png")

# Scene 10: the oxbow bend of the Napa River at the market.
OX = (38.3017, -122.2817)
c = Card(frame(OX[0] + 0.0004, OX[1], 0.0235))
for x in OXBOW:
    t = x["tags"]
    if t.get("waterway"):
        c.line(x["geometry"], WATER, 22 if t["waterway"] == "river" else 8)
for x in OXBOW:
    t = x["tags"]
    if "highway" in t:
        c.line(x["geometry"], "#BDB29A" if t["highway"] in ("primary", "secondary") else ROAD, 7 if t["highway"] in ("primary", "secondary") else 4)
c.label("NAPA RIVER", 38.3040, -122.2760, 30, "#4C7686", True)
c.pin(1, OX[0], OX[1], "Oxbow Public Market", side="l")
c.banner("The river's bend", "downtown Napa")
c.save("napa-map-10-oxbow.png")

# Scene 11: Carneros straddles the Napa/Sonoma county line.
c = Card(frame(38.268, -122.335, 0.20))
c.bays()
c.roads(VALLEY, main_refs=("CA 121", "CA 12;CA 121"), alt_refs=("CA 29",), skip_minor=True)
for x in COUNTY:
    c.line(x["geometry"], INK, 5, dash=(26, 18))
c.label("NAPA COUNTY", 38.25, -122.262, 30, "#4A5A50", True)
c.label("SONOMA COUNTY", 38.21, -122.40, 30, "#4A5A50", True)
c.label("CARNEROS", 38.238, -122.325, 38, MAIN, True)
c.pin(1, 38.2972, -122.2860, "Downtown Napa", side="r")
c.pin(2, 38.2555, -122.3514, "Domaine Carneros", side="l")
c.banner("Carneros", "one wine region, two counties")
c.legend([(INK, "The Napa and Sonoma county line", True)])
c.save("napa-map-11-carneros.png")

# Scene 13: Highway 29 and the Silverado Trail side by side.
c = Card(frame(38.44, -122.43, 0.42))
c.roads(VALLEY, main_refs=("CA 29",), alt_refs=(), skip_minor=False)
for x in VALLEY:
    if x["tags"].get("name") in ("Silverado Trail", "Silverado Trail North"):
        c.line(x["geometry"], ALT, 9)
for n, la, lo in (("NAPA", 38.299, -122.286), ("YOUNTVILLE", 38.402, -122.362), ("ST. HELENA", 38.505, -122.470), ("CALISTOGA", 38.579, -122.580)):
    c.label(n, la, lo, 32, bold=True)
c.banner("Two roads up the valley")
c.legend([(MAIN, "Highway 29 (busier)", False), (ALT, "The Silverado Trail (quieter)", False)])
c.save("napa-map-13-two-roads.png")

# Scene 20: Calistoga, with Chateau Montelena marked (our overlay: the year only).
M = BAYS["montelena"]
c = Card(frame(M["lat"] - 0.004, M["lon"] + 0.012, 0.075))
c.roads(VALLEY, main_refs=("CA 29", "CA 128", "CA 29;CA 128"), skip_minor=False, base_width=3)
c.label("CALISTOGA", 38.5788, -122.5797, 34, bold=True)
c.pin(1, M["lat"], M["lon"], "Chateau Montelena", side="r")
c.label("1976", M["lat"] - 0.020, M["lon"] - 0.030, 80, MAIN, True)
c.banner("Calistoga")
c.save("napa-map-20-calistoga.png")
