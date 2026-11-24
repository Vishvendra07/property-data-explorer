"""Query authored property records with DuckDB and explore them in a local report."""

import argparse
import json
from pathlib import Path

import duckdb

PROPERTIES = [
    (1, "Birch Court", "West", 255000, 3, 18, 44),
    (2, "River Gate", "Central", 338000, 2, 64, 42),
    (3, "Juniper Lane", "West", 217500, 2, 15, 23),
    (4, "Beacon House", "East", 369000, 4, 83, 52),
    (5, "Willow Place", "Central", 297500, 3, 40, 71),
    (6, "Stone Hill", "East", 182000, 2, 73, 76),
    (7, "North Terrace", "Central", 312000, 3, 43, 26),
    (8, "Hawthorn Row", "West", 289000, 4, 29, 68),
    (9, "Foundry Lofts", "East", 310000, 2, 86, 29),
    (10, "Elm Crossing", "Central", 228000, 2, 52, 56),
]
QUERY = """SELECT id, name, district, usd, beds, x, y FROM properties
    WHERE (?='' OR district=?) AND usd<=? AND beds>=? ORDER BY usd,id"""


def database():
    db = duckdb.connect()
    db.execute(
        "CREATE TABLE properties (id INTEGER, name VARCHAR, district VARCHAR, usd INTEGER, beds INTEGER, x INTEGER, y INTEGER)"
    )
    db.executemany("INSERT INTO properties VALUES (?,?,?,?,?,?,?)", PROPERTIES)
    return db


def query(db, district="", maximum=1_000_000, beds=0):
    if (
        district not in ("", "West", "Central", "East")
        or not 0 <= maximum <= 1_000_000
        or not 0 <= beds <= 8
    ):
        raise ValueError("Invalid district, budget, or bedroom count")
    args = [district, district, maximum, beds]
    cursor = db.execute(QUERY, args)
    keys = [column[0] for column in cursor.description]
    properties = [dict(zip(keys, row, strict=True)) for row in cursor.fetchall()]
    execution = db.execute("EXPLAIN " + QUERY, args).fetchone()[1]
    return {"records": properties, "explain": execution}


def render(records):
    data = json.dumps(records).replace("<", "\\u003c")
    return f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Property Data Explorer</title>
<style>body{{font:16px/1.4 system-ui;margin:0;background:#f8f8f3;color:#222b28}}header{{background:#151d24;color:white;padding:1.2rem 5vw;font-weight:700}}main{{max-width:1200px;margin:auto;padding:1.8rem 4vw}}h1{{font-size:clamp(2rem,4vw,3.4rem);margin:0}}form{{display:flex;flex-wrap:wrap;gap:1rem;margin:1.2rem 0}}label{{display:grid;gap:.3rem}}input,select,button{{font:inherit;color:inherit;padding:.4rem .6rem}}section{{display:grid;grid-template-columns:1fr 1fr;gap:1.2rem}}.map{{height:400px;position:relative;background:repeating-linear-gradient(0deg,transparent 0 52px,#d0dcd2 53px 54px),repeating-linear-gradient(90deg,#eaf1e7 0 60px,#cad9cc 61px 62px);border:1px solid #aebcb1;border-radius:10px}}.pin{{position:absolute;transform:translate(-50%,-50%);border-radius:50%;background:#215a45;color:white;border:1px solid #144a35;min-width:2.3rem}}button[aria-pressed=true]{{background:#9a431b;color:white}}table{{width:100%;border-collapse:collapse}}td,th{{padding:.4rem;text-align:left;border-bottom:1px solid #d3d8d1}}td button{{width:100%;text-align:left;border:0;background:transparent}}:focus-visible{{outline:3px solid #846d1d}}@media(max-width:750px){{section{{grid-template-columns:1fr}}.map{{height:270px}}}}</style>
<header>Property Data Explorer</header><main><h1>Explore the local market</h1><p>Fictional properties and schematic coordinates.</p><form id="filters" role="search">
<label>District<select name="district"><option value="">All districts</option><option>West</option><option>Central</option><option>East</option></select></label><label>Maximum price (USD)<input name="maximum" type="number" min="0" max="1000000" value="1000000"></label><label>Minimum bedrooms<input name="beds" type="number" min="0" max="8" value="0"></label><button>Apply filters</button></form>
<p id="count" role="status"></p><section><div id="map" class="map" aria-label="Schematic property map"></div>
<div><p id="selected" role="status">Select a property to see its details.</p><table><thead><tr><th scope="col">Property</th><th scope="col">District</th><th scope="col">Price</th></tr></thead><tbody id="rows"></tbody></table></div></section></main>
<script>const data={data};const form=document.querySelector('#filters');const params=new URLSearchParams(location.search);const money=new Intl.NumberFormat('en-US',{{style:'currency',currency:'USD',maximumFractionDigits:0}});
for(const input of form.elements){{if(input.name&&params.has(input.name))input.value=params.get(input.name);}}if(!form.checkValidity())form.reset();
function select(record){{document.querySelectorAll('[data-id]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.id)===record.id)));document.querySelector('#selected').textContent=`${{record.name}} · ${{record.beds}} bedrooms · ${{money.format(record.usd)}}`;}}
function render(){{const filters=new FormData(form);const list=data.filter(r=>(!filters.get('district')||r.district===filters.get('district'))&&r.usd<=Number(filters.get('maximum')||1000000)&&r.beds>=Number(filters.get('beds')||0)); const map=document.querySelector('#map'),rows=document.querySelector('#rows');map.replaceChildren();rows.replaceChildren();document.querySelector('#count').textContent=`${{list.length}} ${{list.length===1?'property':'properties'}}`;document.querySelector('#selected').textContent='Select a property to see its details.';
for(const record of list){{const pin=document.createElement('button');pin.type='button';pin.className='pin';pin.dataset.id=record.id;pin.setAttribute('aria-pressed','false');pin.setAttribute('aria-label',record.name+' on map');pin.style.left=record.x+'%';pin.style.top=record.y+'%';pin.textContent=record.id;pin.onclick=()=>select(record);map.append(pin);
const row=rows.insertRow();const button=document.createElement('button');button.type='button';button.dataset.id=record.id;button.setAttribute('aria-pressed','false');button.textContent=record.name;button.onclick=()=>select(record);row.insertCell().append(button);row.insertCell().textContent=record.district;row.insertCell().textContent=money.format(record.usd);}}}}
form.onsubmit=(event)=>{{event.preventDefault();try{{history.replaceState(null,'','?'+new URLSearchParams(new FormData(form)));}}catch{{}}render();}};render();</script></html>"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--district", default="")
    parser.add_argument("--maximum", type=int, default=1_000_000)
    parser.add_argument("--beds", type=int, default=0)
    parser.add_argument("--html", type=Path)
    args = parser.parse_args()
    with database() as db:
        result = query(db, args.district, args.maximum, args.beds)
        if args.html:
            args.html.write_text(render(query(db)["records"]), encoding="utf-8")
    print(json.dumps(result, indent=2))
