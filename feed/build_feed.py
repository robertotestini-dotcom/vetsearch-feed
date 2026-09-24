"""Build two small HTTPS feeds from the latest Overture Places release.

Run with `pip install -r feed/requirements.txt` then `python feed/build_feed.py`.
Requires network access to the Overture STAC, S3 and the public ISTAT-derived
province boundaries. Fails without replacing an existing published feed.
"""
import datetime as dt
import json
import os
from pathlib import Path
from urllib.request import urlopen

import duckdb
from shapely.geometry import Point, shape


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "public"
STAC = "https://stac.overturemaps.org/catalog.json"
BOUNDARIES = "https://raw.githubusercontent.com/guglielmo/geojson-italy/main/geojson/limits_IT_provinces.geojson"
PROVINCES = {15: ("Milano", "milano"), 108: ("Monza", "monza")}


def download_json(url):
    with urlopen(url, timeout=60) as response:
        return json.load(response)


def build():
    latest = download_json(STAC)["latest"]
    if not isinstance(latest, str) or not latest.startswith("20") or "/" in latest:
        raise ValueError("Release Overture non valida")
    boundaries = download_json(BOUNDARIES)
    polygons = {}
    for feature in boundaries["features"]:
        code = feature["properties"].get("prov_istat_code")
        if code is not None and int(code) in PROVINCES:
            polygons[int(code)] = shape(feature["geometry"])
    if set(polygons) != set(PROVINCES):
        raise ValueError("Confini provinciali incompleti")

    con = duckdb.connect()
    con.execute("SET s3_region='us-west-2'")
    path = f"s3://overturemaps-us-west-2/release/{latest}/theme=places/type=place/*"
    # The bounding box is deliberately wider than both provinces; the actual
    # selection is performed by the polygon.contains/touches checks below.
    query = """SELECT id, names.primary, addresses[1].locality,
       addresses[1].freeform, phones[1], bbox.xmin, bbox.ymin,
       confidence, operating_status
       FROM read_parquet(?)
       WHERE bbox.xmin BETWEEN 8.3 AND 10.0
         AND bbox.ymin BETWEEN 44.9 AND 46.0
         AND taxonomy.primary = 'veterinarian'
         AND confidence >= 0.5
         AND (operating_status IS NULL OR operating_status != 'permanently_closed')
    """
    rows = con.execute(query, [path])
    groups = {code: [] for code in PROVINCES}
    while batch := rows.fetchmany(500):
        for uid, name, city, address, phone, lon, lat, confidence, status in batch:
            if not uid or not name or lon is None or lat is None:
                continue
            point = Point(float(lon), float(lat))
            for code, polygon in polygons.items():
                if polygon.covers(point):
                    groups[code].append({"id": str(uid), "name": name,
                        "city": city or "", "address": address or "",
                        "phone": phone or "", "province": PROVINCES[code][0],
                        "lat": float(lat), "lon": float(lon),
                        "confidence": float(confidence), "operating_status": status})
                    break
    OUT.mkdir(parents=True, exist_ok=True)
    generated = dt.datetime.now(dt.timezone.utc).isoformat()
    for code, (province, filename) in PROVINCES.items():
        items = groups[code]
        if not items:
            raise ValueError(f"Nessuna struttura per {province}; non pubblicare")
        payload = {"schema": 1, "province": province, "release": latest,
                   "generated_at": generated, "source": "Overture Maps Places",
                   "items": items}
        data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        if len(data.encode("utf-8")) > 7_000_000:
            raise ValueError(f"Feed {province} troppo grande")
        (OUT / (filename + ".json.tmp")).write_text(data, encoding="utf-8")
    for _, filename in PROVINCES.values():
        os.replace(OUT / (filename + ".json.tmp"), OUT / (filename + ".json"))
    (OUT / "index.html").write_text("<p>VetSearch · Overture Places</p>", encoding="utf-8")
    print("Release", latest, "counts", {PROVINCES[k][0]: len(v) for k, v in groups.items()})


if __name__ == "__main__":
    build()
