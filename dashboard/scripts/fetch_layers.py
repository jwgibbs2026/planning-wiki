"""Fetch Gloucestershire designation overlays from official open data.

Sources (all returned in WGS84 / EPSG:4326 via ArcGIS `outSR`):
  * Council borders + clip boundary — ONS Open Geography Portal, Local Authority
    Districts (May 2024), the six Gloucestershire districts.
  * Ancient Woodland, SAC, SSSI — Natural England Open Data (ArcGIS).

Every designation is **clipped to the Gloucestershire boundary** (union of the
six districts) with shapely, so anything outside the county is dropped and
straddling features are cut at the border. Output is written to
planning_dashboard/web/layers/.

Local Wildlife Sites are NOT open data (held by GWT / GCER), so `LWS layer.geojson`
is not fetched here — drop your own copy into the layers folder.

Run:  python dashboard/scripts/fetch_layers.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import requests
from shapely.geometry import mapping, shape
from shapely.ops import unary_union

# Drop slivers smaller than this (deg ~ a few m) and simplify to this tolerance.
SIMPLIFY_TOL = 0.00004  # ~4.5m at this latitude


def to_polygonal(geom):
    """Keep only polygonal parts of a (possibly mixed) clipped geometry."""
    if geom.is_empty:
        return None
    t = geom.geom_type
    if t in ("Polygon", "MultiPolygon"):
        polys = geom
    elif t == "GeometryCollection":
        parts = [g for g in geom.geoms if g.geom_type in ("Polygon", "MultiPolygon")]
        if not parts:
            return None
        polys = unary_union(parts)
    else:  # LineString/Point slivers from the intersection — discard
        return None
    polys = polys.simplify(SIMPLIFY_TOL, preserve_topology=True)
    return None if polys.is_empty else polys

OUT_DIR = Path(__file__).resolve().parent.parent / "planning_dashboard" / "web" / "layers"

ONS = "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services"
NE = "https://services.arcgis.com/JJzESW51TqeY9uat/arcgis/rest/services"

GLOS_DISTRICTS = ["Gloucester", "Cheltenham", "Tewkesbury", "Stroud", "Cotswold", "Forest of Dean"]

# Designation layers: (output filename, ArcGIS layer url)
DESIGNATIONS = [
    ("Ancient Woodlands.geojson", f"{NE}/Ancient_Woodland_England/FeatureServer/0"),
    ("GlosSac.geojson", f"{NE}/Special_Areas_of_Conservation_England/FeatureServer/0"),
    ("SSSI.geojson", f"{NE}/SSSI_England/FeatureServer/0"),
]

NAME_KEYS = [
    "NAME", "Name", "name", "SSSI_NAME", "SAC_NAME", "LWS_NAME", "WOODNAME",
    "NNR_NAME", "SITE_NAME", "DESCRIPT", "LAD24NM", "REFERENCE",
]

session = requests.Session()
session.headers.update({"User-Agent": "glos-planning-dashboard/0.1"})


def _name_of(props: dict) -> str | None:
    for k in NAME_KEYS:
        if props.get(k):
            return str(props[k])
    return None


def fetch_geojson(url: str, *, where: str = "1=1", bbox: str | None = None) -> list[dict]:
    """Page through an ArcGIS layer, returning GeoJSON features in WGS84."""
    features: list[dict] = []
    offset = 0
    page = 1000
    while True:
        params = {
            "where": where,
            "outFields": "*",
            "outSR": 4326,
            "f": "geojson",
            "resultOffset": offset,
            "resultRecordCount": page,
            "geometryPrecision": 6,
        }
        if bbox:
            params.update(
                geometry=bbox,
                geometryType="esriGeometryEnvelope",
                inSR=4326,
                spatialRel="esriSpatialRelIntersects",
            )
        r = session.get(url + "/query", params=params, timeout=120)
        r.raise_for_status()
        data = r.json()
        batch = data.get("features", [])
        features.extend(batch)
        if len(batch) < page and not data.get("exceededTransferLimit"):
            break
        if not batch:
            break
        offset += len(batch)
        time.sleep(0.3)
    return features


def write_fc(path: Path, features: list[dict]) -> None:
    path.write_text(
        json.dumps({"type": "FeatureCollection", "features": features}),
        encoding="utf-8",
    )


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Gloucestershire districts -> borders.geojson + clip boundary.
    names = ",".join(f"'{n}'" for n in GLOS_DISTRICTS)
    lad_url = f"{ONS}/Local_Authority_Districts_May_2024_Boundaries_UK_BGC/FeatureServer/0"
    print("Fetching Gloucestershire district boundaries (ONS)...")
    districts = fetch_geojson(lad_url, where=f"LAD24NM IN ({names})")
    if len(districts) != 6:
        print(f"  WARNING: expected 6 districts, got {len(districts)}")
    # Slim borders to just the name and write.
    border_feats = []
    geoms = []
    for f in districts:
        nm = _name_of(f.get("properties", {}))
        border_feats.append({"type": "Feature", "properties": {"name": nm}, "geometry": f["geometry"]})
        geoms.append(shape(f["geometry"]))
    write_fc(OUT_DIR / "borders.geojson", border_feats)
    print(f"  borders.geojson: {len(border_feats)} districts")

    boundary = unary_union(geoms).buffer(0)
    minx, miny, maxx, maxy = boundary.bounds
    bbox = f"{minx},{miny},{maxx},{maxy}"
    print(f"  county bbox: {bbox}")

    # 2. Designations: fetch within bbox, clip to the county boundary.
    for fname, url in DESIGNATIONS:
        print(f"Fetching {fname} ...")
        try:
            raw = fetch_geojson(url, bbox=bbox)
        except Exception as exc:  # noqa: BLE001
            print(f"  ERROR fetching {fname}: {exc}")
            continue
        out = []
        for f in raw:
            geom = f.get("geometry")
            if not geom:
                continue
            try:
                g = shape(geom).buffer(0)
            except Exception:
                continue
            if not g.intersects(boundary):
                continue
            clipped = to_polygonal(g.intersection(boundary))
            if clipped is None:
                continue
            out.append({
                "type": "Feature",
                "properties": {"name": _name_of(f.get("properties", {}))},
                "geometry": mapping(clipped),
            })
        write_fc(OUT_DIR / fname, out)
        size_kb = (OUT_DIR / fname).stat().st_size / 1024
        print(f"  {fname}: {len(out)} features clipped to Gloucestershire ({size_kb:.0f} kB)")

    print("Done. LWS layer.geojson must be supplied separately (not open data).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
