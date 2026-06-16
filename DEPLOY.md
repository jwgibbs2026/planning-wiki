# Putting the site live on Netlify (free) — and editing it in your browser

The whole site — **Toolkit Guide, Planning Wiki, and Planning Map** — is now a
fully **static** site, so it hosts free on Netlify with no server and no
"sleeping". Every time you save a change on GitHub, Netlify rebuilds the site
automatically in a minute or two.

```
You edit a file on GitHub  ──▶  Netlify rebuilds  ──▶  live site updates
   (in the browser)               (automatic)        https://…netlify.app
```

You only need one free account: **Netlify** (it reads the code from your existing
GitHub repo). Everything is already prepared in this folder.

---

## One-time setup (≈5 minutes)

1. Go to <https://app.netlify.com> and **sign up with GitHub**.
2. Click **Add new site ▸ Import an existing project ▸ GitHub**.
3. Authorise Netlify and pick the **`planning-wiki`** repository.
4. Netlify reads the included `netlify.toml`, so the build command and publish
   folder are already filled in. Just click **Deploy**.
5. The first build takes ~3–5 minutes (it builds the wiki, then assembles the
   site). When it's done you get a live URL like
   `https://planning-wiki-xyz.netlify.app`. 🎉

You can rename the site (and the URL) under **Site configuration ▸ Site details**,
or attach your own domain later.

> No cold starts, no sleeping — Netlify serves the finished files instantly.

---

## Editing the live site from your browser

1. Go to your repo at **github.com/jwgibbs2026/planning-wiki**.
2. Open the file you want to change:
   - **Toolkit Guide** → `dashboard/planning_dashboard/web/guide.html`
   - **Wiki pages** → the markdown under `wiki-src/content/…`
3. Click the **pencil (✏️) icon**, make your change.
4. Scroll down, click **Commit changes**.
5. Netlify rebuilds automatically. Refresh the live site after a minute or two.

No software, no commands. (You can also edit on your PC and push, if you prefer.)

---

## Refreshing the map data

The map reads `dashboard/planning_dashboard/web/applications.geojson`, a snapshot
exported from your local database. To update it:

```powershell
cd "Planning toolkit wiki\dashboard"
.\.venv\Scripts\python.exe scripts\run_import.py        # fetch latest applications
$env:PYTHONPATH="."; .\.venv\Scripts\python.exe scripts\export_static.py   # rewrite the static files
```

Then commit the updated `applications.geojson` (and `authorities.json`) — Netlify
redeploys with the fresh data. The Guide and Wiki don't need this step.

---

## What's where

| Part of the site | Source | Lives at |
|------------------|--------|----------|
| Toolkit Guide    | `dashboard/planning_dashboard/web/guide.html` | `/` |
| Planning Wiki    | `wiki-src/content/…` (Quartz markdown)        | `/wiki/` |
| Planning Map     | `…/web/index.html`, `app.js`, `applications.geojson` | `/map/` |
| Shared nav bar   | `…/web/nav.js`                                | every page |
| Build recipe     | `netlify.toml` + `build-static.mjs`           | — |

### Test the build locally (optional)

```powershell
cd wiki-src; npm ci; npx quartz plugin install; npx quartz build; cd ..
node build-static.mjs
# then serve the ./dist folder with any static server and open it
```

---

## Alternative host (also free)

A server-based deploy for **Render** is also included (`Dockerfile`,
`render.yaml`) if you ever want the map to query a live database instead of a
static snapshot. Netlify (above) is simpler and faster for this site; you don't
need both.
