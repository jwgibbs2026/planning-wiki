# Gloucestershire Planning Application Mapping Dashboard

A private, local dashboard that collects recent planning applications for the
seven Gloucestershire local authorities and shows each as a **dot** on a web map,
every dot linking back to the **official council** application page.

- **Working:** PlanIt importer → SQLite → FastAPI → Leaflet map (points only).
- **Scaffolded, optional:** per-council document scrapers (`scrapers/`) and a
  title/VLM document classifier (`classify/`) — interfaces and tables exist but
  are not wired up. Red-line boundary extraction is **out of scope** by design.

Authorities monitored: Gloucester City, Cheltenham, Gloucestershire County,
Tewkesbury, Forest of Dean, Stroud, Cotswold.

## Setup (Windows / PowerShell)

```powershell
cd "Planning toolkit wiki\dashboard"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # optional; defaults are fine
```

## Initialise the database

```powershell
python scripts\init_db.py
```

Creates `data\planning.sqlite` with the schema and the seven seeded authorities,
and checks the seeded PlanIt names against the live PlanIt areas list.

> SpatiaLite is loaded automatically **if available**; otherwise geometry is
> stored as GeoJSON text and the app works exactly the same. PostGIS/PostGIS is
> the documented eventual target but is not required for the prototype.

## Import applications

```powershell
# One authority, last 30 days (quick test)
python scripts\run_import.py --authority Cotswold --days 30

# All seven authorities (first run backfills 90 days, then incremental)
python scripts\run_import.py
```

The importer is **incremental**: the first run per authority backfills
`PLANNING_BACKFILL_DAYS` (default 90); later runs fetch only records changed
since the last run (via PlanIt `changed_start`). Each authority is isolated, so
one failing council does not abort the others.

### Daily automation (Windows Task Scheduler)

Create a Basic Task → Daily → *Start a program*:

- Program: `…\dashboard\.venv\Scripts\python.exe`
- Arguments: `…\dashboard\scripts\run_import.py`
- Start in: `…\dashboard`

## Run the merged site (wiki + map)

The FastAPI server is the single front door for the whole site:

- `/` — the **Planning Wiki** (the built Quartz site)
- `/map` — the **Planning Map**
- `/api/*` — the data API

A green nav bar with **Planning Wiki | Planning Map** tabs sits on top of every
page, so it's one site. The wiki itself is never modified — the nav bar is
injected as each page is served, so it survives Quartz rebuilds.

```powershell
# 1. Build the wiki (in the Quartz folder) so /public is up to date
cd C:\Users\jwgib\Documents\quartz-5
npx quartz build

# 2. Run the site (back in the dashboard folder)
cd "C:\Users\jwgib\Documents\Planning toolkit wiki\dashboard"
.\.venv\Scripts\Activate.ps1
python -m uvicorn planning_dashboard.api:app
```

Open <http://localhost:8000>. The map shows clustered application dots
(filterable by authority, status, and recency); each popup links to the official
council page and to PlanIt.

- The wiki is served from `PLANNING_WIKI_PUBLIC_DIR` (default
  `C:\Users\jwgib\Documents\quartz-5\public`). If that folder is missing, `/`
  returns a 503 with a hint and the map still works at `/map`.
- **Editing the wiki:** keep using Quartz's live dev server
  (`npx quartz build --serve --port 3000`) while writing content; rebuild
  (`npx quartz build`) to update what the merged site on :8000 serves.
- To change the nav bar, edit the single `nav_bar()` function in
  `planning_dashboard/api.py`.

API: `GET /api/applications?authority=&status=&days=&bbox=` returns GeoJSON;
`GET /api/authorities` lists the authorities.

## Map overlay layers (designations)

The map has a layer control (top-right) with togglable overlays for Ancient
Woodland, SACs, SSSIs, Local Wildlife Sites and council borders. Generate the
open-data ones (clipped to Gloucestershire, in WGS84) with:

```powershell
python scripts\fetch_layers.py
```

This writes GeoJSON into `planning_dashboard/web/layers/`. **Local Wildlife
Sites** is not open data (held by GWT/GCER) — drop your own `LWS layer.geojson`
into that folder. See `planning_dashboard/web/layers/README.txt`. Layers are
lazy-loaded on first toggle; edit `OVERLAY_DEFS` in `web/app.js` to add/restyle.

## Tests

```powershell
python -m pytest tests
```

## Constraints / etiquette

- Stores **metadata and official links only** — planning drawings/images are
  never republished, and site boundaries are not extracted.
- Polite by default: User-Agent set, request delay, exponential backoff on HTTP
  429/5xx, and robots.txt checking in the (optional) scrapers.
