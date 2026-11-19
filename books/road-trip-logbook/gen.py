#!/usr/bin/env python3
"""Glovebox Road Trip Logbook, interior (ttn#39 Gate A/B). Drawn by code: HTML pages -> weasyprint -> PDF; $0.

6 x 9 in trim, black and white, undated, 120 pages: front matter, 25 trips x 4 pages (plan, route log, costs, memories),
US checklists, tickets and receipts, notes, the feedback page. Grey example hints are dense in the first trips and sparser
later (R100). Page-edge trip numbers stand in for dividers (kept 0.25 in inside the trim edge, so no bleed is needed).
Usage: python3 gen.py <out dir>      writes interior.html and interior.pdf
"""
import html, subprocess, sys
from pathlib import Path

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
TRIPS = 25
BOX = "☐"

CSS = """
@page { size: 6in 9in; margin: 0.62in 0.55in 0.7in 0.75in; }
@page :right { margin-left: 0.75in; margin-right: 0.55in; @top-right { content: string(tab); font: 700 11pt 'Noto Sans'; color: #fff; background: #222; padding: 3pt 9pt 3pt 12pt; margin-right: -0.3in; margin-top: 0.3in; margin-bottom: 0.08in; }
               @bottom-right { content: counter(page); font: 8.5pt 'Noto Sans'; color: #555; } }
@page :left  { margin-left: 0.55in; margin-right: 0.75in; @top-left { content: string(tab); font: 700 11pt 'Noto Sans'; color: #fff; background: #222; padding: 3pt 12pt 3pt 9pt; margin-left: -0.3in; margin-top: 0.3in; margin-bottom: 0.08in; }
               @bottom-left { content: counter(page); font: 8.5pt 'Noto Sans'; color: #555; } }
@page plain:right { @top-right { content: none; background: none; } }
@page plain:left { @top-left { content: none; background: none; } }
@page cover { @top-right { content: none; background: none; } @bottom-right { content: none; } @top-left { content: none; background: none; } @bottom-left { content: none; } }
html { font-family: 'Noto Sans', sans-serif; font-size: 8.6pt; line-height: 1.3; color: #1a1a1a; }
.page { break-after: page; }
.trip-page { string-set: tab attr(data-tab); }
.plain { page: plain; } .cover { page: cover; }
h1 { font-size: 21pt; margin: 0 0 8pt; } h2 { font-size: 13pt; margin: 0 0 7pt; } h3 { font-size: 9.5pt; margin: 9pt 0 3pt; }
p { margin: 0 0 6pt; } ul { margin: 0 0 6pt; padding-left: 13pt; } li { margin-bottom: 2pt; }
.sub { color: #555; font-size: 8pt; margin: -3pt 0 8pt; }
.field { display: flex; align-items: flex-end; margin-bottom: 6pt; }
.field label { font-weight: 700; font-size: 8pt; white-space: nowrap; margin-right: 5pt; }
.field .fill { flex: 1; border-bottom: 0.6pt solid #888; height: 13pt; line-height: 13pt; overflow: hidden; white-space: nowrap; }
.hint { color: #9a9a9a; font-style: italic; font-size: 7.6pt; }
.row2 { display: flex; gap: 10pt; } .row2 .field { flex: 1; }
table { width: 100%; border-collapse: collapse; table-layout: fixed; margin-bottom: 6pt; }
th { font-size: 7.4pt; text-align: left; border-bottom: 1pt solid #333; padding: 2pt 3pt; }
td { border-bottom: 0.5pt solid #999; height: 0.36in; padding: 0 3pt; vertical-align: bottom; font-size: 8pt; overflow: hidden; white-space: nowrap; }
td.box:after { content: ""; display: inline-block; width: 8.5pt; height: 8.5pt; border: 0.8pt solid #444; vertical-align: bottom; }
td.box, th.box { text-align: center; }
.tall td { height: 0.44in; }
.lines { margin-bottom: 6pt; } .lines .l { border-bottom: 0.5pt solid #999; height: 0.3in; line-height: 0.3in; }
.tape { border: 0.8pt dashed #777; color: #999; font-size: 7.6pt; display: flex; align-items: center; justify-content: center; }
.tape.photo { height: 2.1in; } .tape.ticket { height: 1.15in; flex: 1; }
.stars { font-size: 15pt; letter-spacing: 4pt; color: #444; }
.cover-page { text-align: center; padding-top: 2.3in; } .cover-page .t { font-size: 27pt; font-weight: 700; } .cover-page .s { font-size: 11pt; color: #444; margin-top: 8pt; }
.big-fill { border-bottom: 0.6pt solid #888; height: 16pt; margin: 14pt 0 3pt; }
.small { font-size: 7.6pt; color: #555; }
.cols { columns: 2; column-gap: 14pt; } .cols h3, .cols li { break-inside: avoid; }
.chk { padding-left: 0; } .chk li { list-style: none; } .chk li:before { content: ""; display: inline-block; width: 7pt; height: 7pt; border: 0.8pt solid #444; margin-right: 5pt; }
.num { font-weight: 700; }
"""

def esc(s): return html.escape(s)

def field(label, hint=None):
    return f'<div class="field"><label>{esc(label)}</label><div class="fill{" hint" if hint else ""}">{esc(hint or "")}</div></div>'

def table(cols, widths, n, hints=None, cls=""):
    colgroup = "".join(f'<col style="width:{w}">' for w in widths)
    th = "".join(f'<th class="{"box" if c.startswith(BOX) else ""}">{esc(c.replace(BOX, "").strip())}</th>' for c in cols)
    body = []
    for i in range(n):
        h = (hints or {}).get(i)
        cells = []
        for j, c in enumerate(cols):
            if c.startswith(BOX):
                cells.append('<td class="box"></td>')
            elif h and j < len(h) and h[j]:
                cells.append(f'<td class="hint">{esc(h[j])}</td>')
            else:
                cells.append("<td></td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f'<table class="{cls}"><colgroup>{colgroup}</colgroup><thead><tr>{th}</tr></thead>' + "".join(body) + "</table>"

def lines(n, hint=None):
    return '<div class="lines">' + "".join(f'<div class="l hint">{esc(hint) if (hint and i == 0) else ""}</div>' for i in range(n)) + "</div>"

def trip(n):
    tab = f"TRIP {n:02d}"
    dense, some = n <= 2, 3 <= n <= 5   # R100: full hints on trips 1-2, a first-row hint on 3-5, none after
    H = (lambda s: s) if dense else (lambda s: None)
    a = f'''<section class="page trip-page" data-tab="{tab}"><h2>Plan</h2>
{field("Trip name", H("Spring weekend: Napa and back"))}
<div class="row2">{field("Dates", H("Apr 12 to Apr 14"))}{field("Who's coming", H("Sam, Jo, the dog"))}</div>
<div class="row2">{field("From", H("Home"))}{field("To", H("Napa Valley, CA"))}</div>
<div class="row2">{field("Miles", H("about 220"))}{field("Drive time", H("4 hrs each way"))}{field("Budget", H("$600"))}</div>
<h3>Stops and bookings</h3>
{table(["Stop", BOX + " Booked", BOX + " Paid", BOX + " Dep.", "Conf. no."], ["2.0in", "0.55in", "0.5in", "0.5in", "1.15in"], 8,
  {0: ["Hotel, 2 nights", "", "", "", "A-4471"], 1: ["Winery tasting, 11 am"]} if dense else ({0: ["Hotel"]} if some else None))}
<h3>Before we go</h3>
<ul class="chk cols"><li>Car check (page near the back)</li><li>Fuel up</li><li>Charge phones and the car charger</li><li>Download maps for the area</li><li>Packing list (back)</li><li>Tickets and reservations ready</li></ul>
</section>'''
    b = f'''<section class="page trip-page" data-tab="{tab}"><h2>Route log</h2><p class="sub">One line a stop, with room to write what to remember and what to skip next time.</p>
{table(["#", "Place", "Arrived", "Miles", "Notes"], ["0.25in", "1.15in", "0.55in", "0.5in", "2.25in"], 14,
  {0: ["1", "Home to Vacaville", "9:10", "62", "Coffee stop; the line was long, go earlier."], 1: ["2", "Napa, Oxbow Market", "11:20", "41", "Parking is free"]} if dense else ({0: ["1", "First stop"]} if some else None), "tall")}
</section>'''
    c = f'''<section class="page trip-page" data-tab="{tab}"><h2>Costs</h2>
<h3>Fuel</h3>
{table(["Date", "Odometer", "Gallons", "Total $", "Where"], ["0.65in", "0.85in", "0.7in", "0.7in", "1.8in"], 6,
  {0: ["Apr 12", "48,210", "11.4", "42.90", "Vacaville"]} if dense else ({0: ["Apr 12"]} if some else None))}
<h3>Everything else</h3>
<table><colgroup><col style="width:1.7in"><col style="width:1in"><col style="width:2in"></colgroup><thead><tr><th>Item</th><th>Amount $</th><th>Note</th></tr></thead>
{''.join(f"<tr><td><b>{x}</b></td><td></td><td></td></tr>" for x in ["Lodging", "Food and drink", "Tolls and parking", "Tickets and tours", "Souvenirs", "Other"])}</table>
<div class="row2">{field("Total spent")}{field("Miles driven")}{field("MPG")}</div>
</section>'''
    d = f'''<section class="page trip-page" data-tab="{tab}"><h2>Memories</h2>
{field("Best moment", H("Sunset at the vineyard"))}
{field("Best meal", H("The tacos in Napa"))}
<div class="row2">{field("Weather", H("Sunny, 68"))}{field("Would we go again?", H("Yes, in winter"))}</div>
<p><b>Rating</b> <svg width="110" height="18" viewBox="0 0 110 18">''' + ''.join(f'<polygon points="9,1 11.4,6.6 17.5,7 12.8,10.9 14.3,17 9,13.7 3.7,17 5.2,10.9 0.5,7 6.6,6.6" transform="translate({i*22},0)" fill="none" stroke="#444" stroke-width="1"/>' for i in range(5)) + f'''</svg></p>
<div class="tape photo">Tape a photo or a postcard here</div>
<h3>Tickets and receipts</h3>
<div class="row2"><div class="tape ticket">Tape here</div><div class="tape ticket">Tape here</div></div>
<h3>Next time</h3>
{lines(3, H("Book the 11 am tasting a week ahead."))}
</section>'''
    return a + b + c + d

def front():
    p = ['<section class="page cover cover-page"><div class="t">Road Trip Logbook</div><div class="s">25 trips: plan it, log it, remember it</div><div style="margin-top:2.6in;letter-spacing:.08em;font-size:9pt">THETRIPNOW</div></section>',
         '<section class="page plain" style="padding-top:4.2in;font-size:8pt;color:#444"><p>&copy; 2026 TheTripNow. All rights reserved.</p><p>Prices, opening hours and road rules change. Check before you go.</p><p class="big-fill">This logbook belongs to</p><div class="big-fill"></div><p class="small">If found, please call:</p><div class="big-fill"></div></section>',
         '''<section class="page plain"><h2>How to use this logbook</h2>
<p>Each trip gets four pages, always in the same order, and its number sits on the page edge so you can flip straight to it.</p>
<ul><li><b>Plan:</b> where, when, with whom, and what is booked, paid and confirmed.</li><li><b>Route log:</b> one line a stop, with a wide notes column.</li><li><b>Costs:</b> fuel with the odometer, and everything else, so you know your miles per gallon and your real budget.</li><li><b>Memories:</b> the best moment, a photo, the tickets, and what to do next time.</li></ul>
<p>Pages are undated: start any day of the year. Grey italic lines on the first trips are examples; write over them or ignore them.</p>
<p>At the back: US road checklists (including winter), a packing list, a car check, tickets and receipts, and notes.</p>
<p class="small">Tip: keep a pen in the glovebox, fill the Plan page before you leave and the Memories page the same night.</p></section>''']
    for part in (0, 1):
        r = "".join(f'<tr><td class="num">{i:02d}</td><td></td><td></td><td></td></tr>' for i in range(1 + part * 13, 14 + part * 13) if i <= TRIPS)
        p.append(f'<section class="page plain"><h2>Trips {1+part*13} to {min(13+part*13, TRIPS)}</h2><table><colgroup><col style="width:0.4in"><col style="width:2.4in"><col style="width:1.3in"><col style="width:0.8in"></colgroup><thead><tr><th>#</th><th>Where</th><th>When</th><th>Miles</th></tr></thead>{r}</table></section>')
    return "".join(p)

def back():
    p = ['''<section class="page plain"><h2>Road trip checklist (US)</h2><div class="cols"><h3>Car</h3><ul class="chk"><li>Registration and insurance card</li><li>Spare tire, jack, lug wrench</li><li>Jumper cables or a jump starter</li><li>Flashlight and spare batteries</li><li>First-aid kit</li><li>Water and snacks</li><li>Phone charger and mount</li><li>Windshield washer fluid</li></ul>
<h3>Money and rules</h3><ul class="chk"><li>Cash for tolls and parking</li><li>Toll pass or toll-by-plate plan</li><li>Park pass or reservation</li><li>Fuel stops on remote stretches</li><li>Rest stops every two hours</li></ul>
<h3>Winter and mountains</h3><ul class="chk"><li>Tire chains that fit, tried once at home</li><li>Check road and chain controls before you go</li><li>Ice scraper, gloves, blanket</li><li>Full tank before a pass</li><li>Plan to arrive before dark</li></ul>
<h3>People</h3><ul class="chk"><li>Who drives which leg</li><li>Medicines</li><li>ID for everyone</li></ul><h3>Kids</h3><ul class="chk"><li>Car seats and boosters fitted</li><li>Snacks, water, games</li><li>Spare clothes and wipes</li></ul><h3>Pets</h3><ul class="chk"><li>Leash, bowl, water, bags</li><li>Vaccination papers</li><li>Never leave a pet in a parked car</li></ul></div></section>''',
         '<section class="page plain"><h2>Packing list</h2><div class="cols"><h3>Clothes</h3>' + lines(6) + '<h3>Toiletries</h3>' + lines(4) + '<h3>Gear</h3>' + lines(6) + '<h3>Food and drink</h3>' + lines(4) + '</div></section>',
         '<section class="page plain"><h2>Car check</h2><p class="sub">Before every long trip.</p>' + table(["Check", BOX, "Note"], ["2.5in", "0.5in", "1.7in"], 10, {i: [x] for i, x in enumerate(["Tire pressure, spare included", "Tire tread", "Oil level", "Coolant", "Washer fluid", "Lights and signals", "Wipers", "Brakes feel normal", "Battery terminals clean", "Warning lights off"])}) + '<div class="row2">' + field("Date") + field("Odometer") + '</div></section>']
    for k in range(2):
        p.append(f'<section class="page plain"><h2>Tickets and receipts {k+1}</h2><p class="sub">Tape them in and note the trip number.</p><div class="row2" style="margin-bottom:10pt"><div class="tape ticket" style="height:1.9in">Trip ___</div><div class="tape ticket" style="height:1.9in">Trip ___</div></div><div class="row2"><div class="tape ticket" style="height:1.9in">Trip ___</div><div class="tape ticket" style="height:1.9in">Trip ___</div></div></section>')
    p.append('<section class="page plain"><h2>Emergency and useful numbers</h2>' + table(["Who", "Number", "Note"], ["1.8in", "1.5in", "1.5in"], 8, {0: ["Roadside assistance"], 1: ["Insurance claims"]}) + '<p class="small">Highway conditions: dial 511 in most states. Emergencies: 911.</p></section>')
    for k in range(8):
        p.append(f'<section class="page plain"><h2>Notes {k+1}</h2>{lines(21)}</section>')
    p.append('<section class="plain" style="text-align:center;padding-top:2.2in"><h2>Tell us what you think</h2><p>Enjoyed it? A short review on Amazon helps other travelers find it.<br>Something we should change? Tell us at<br><b style="font-size:15pt">thetripnow.com</b></p></section>')
    return "".join(p)

body = front() + "".join(trip(n) for n in range(1, TRIPS + 1)) + back()
(OUT / "interior.html").write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><title>Road Trip Logbook</title><style>{CSS}</style><body>{body}</body></html>')
subprocess.run(["weasyprint", str(OUT / "interior.html"), str(OUT / "interior.pdf")], check=True, capture_output=True)
