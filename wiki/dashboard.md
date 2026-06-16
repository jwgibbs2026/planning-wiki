---
tags: [tool, planning-applications, map, dashboard, gloucestershire]
type: concept
aliases: [Planning Application Map, Applications Dashboard, Planning Map]
---

# Planning Application Mapping Dashboard

A private, locally-run dashboard that answers the wiki's question *"What planning
applications are happening near me?"* (see [[Purpose]]). It collects recent
planning applications across all seven Gloucestershire authorities and plots each
one as a **dot** on an interactive map, with every dot linking back to the
**official council application page**.

It lives in the `dashboard/` folder of this vault and runs as a small local web
app — it is **not** published anywhere.

## What it does

- Pulls application metadata daily from the **PlanIt API** (`planit.org.uk`):
  reference, authority, address, description, dates, status, official URL, and
  point location.
- Stores them in a local database (SQLite) and shows them as dots on a
  [Leaflet](https://leafletjs.com/) map.
- Lets you filter by authority, application status, and recency.

## Authorities monitored

- [[Gloucester City Council]]
- [[Cheltenham Borough Council]]
- [[Gloucestershire County Council]]
- [[Tewkesbury Borough Council]]
- [[Forest of Dean District Council]]
- [[Stroud District Council]]
- [[Cotswold District Council]]

Each is a [[Local Planning Authority]] responsible for determining applications
in its area.

## How to run it

From the `dashboard/` folder (full instructions in its `README.md`):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts\init_db.py            # create DB + seed authorities
python scripts\run_import.py         # import applications from PlanIt
python -m uvicorn planning_dashboard.api:app
```

Then open <http://localhost:8000>.

## Scope and limitations

- Shows a **dot** at each application's location, linking to its official council
  page. Exact site boundaries (red-line plans) are deliberately **not** extracted.
- Stores **metadata and official links only** — planning drawings are never
  republished.
- Data freshness depends on PlanIt's own scraping of each council portal.

## Related

- [[Local Planning Authority]]
- [[Getting Involved in Planning]]
- [[Gloucestershire County Council]]
- [[Cotswolds National Landscape]]
- [[Purpose]]
