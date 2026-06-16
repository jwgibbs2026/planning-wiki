# Putting the site live (and editing it in your browser)

This publishes the **whole site** — Toolkit Guide, Planning Wiki, and Planning
Map — to a live URL, and lets you edit the content from your web browser. Every
time you save a change on GitHub, the live site rebuilds itself in 1–2 minutes.

```
You edit a file on GitHub  ──▶  Render rebuilds  ──▶  live site updates
   (in the browser)               (automatic)         https://…onrender.com
```

You only need two free accounts: **GitHub** (holds the files) and **Render**
(runs the site). Everything is already prepared in this folder.

---

## One-time setup

### 1. Put the project on GitHub
1. Create a free account at <https://github.com> if you don't have one.
2. Install **GitHub Desktop** (<https://desktop.github.com>) — the easy,
   no-command-line way.
3. Open GitHub Desktop → **File ▸ Add local repository** → choose
   `C:\Users\jwgib\Documents\Planning toolkit wiki`.
   (The repository has already been initialised and committed for you.)
4. Click **Publish repository**. Untick "Keep this code private" only if you're
   happy for it to be public; either works with Render. Click **Publish**.

### 2. Deploy on Render
1. Create a free account at <https://render.com> and choose **"Sign in with
   GitHub"** so Render can see your repository.
2. In the Render dashboard click **New ▸ Blueprint**.
3. Pick the repository you just published. Render finds the included
   `render.yaml` and shows a service called **gloucestershire-planning**.
4. Click **Apply**. The first build takes ~5–10 minutes (it installs the wiki
   builder and builds everything once).
5. When it finishes, Render gives you a URL like
   `https://gloucestershire-planning.onrender.com`. That's your live site. 🎉

> **Free-tier note:** the site "sleeps" after ~15 minutes of no visitors, so the
> first visit after a quiet spell takes ~30 seconds to wake up. Upgrading the
> Render service to the paid Starter plan removes this.

---

## Editing the live site from your browser

1. Go to your repository on GitHub.com.
2. Open the file you want to change:
   - **Toolkit Guide** → `dashboard/planning_dashboard/web/guide.html`
   - **Wiki pages** → the markdown files under `wiki-src/content/…`
3. Click the **pencil (✏️) icon** to edit, make your change.
4. Scroll down, click **Commit changes**.
5. Render notices the change and redeploys automatically. Refresh the live site
   after a minute or two.

That's it — no software, no commands. You can also edit on your PC with GitHub
Desktop if you prefer, then click **Push**.

---

## Keeping the map data fresh

The map shows the planning applications stored in
`dashboard/data/planning.sqlite`, which ships with the site. On the free tier it
doesn't refresh by itself. To update it:

1. On your PC, in the `dashboard` folder, run the importer:
   ```powershell
   .\.venv\Scripts\python.exe scripts\run_import.py
   ```
2. Commit the updated `dashboard/data/planning.sqlite` (GitHub Desktop ▸ Push).
   Render redeploys with the fresh data.

For **automatic daily refresh**, upgrade the Render service to a paid instance
and uncomment the disk + cron block in `render.yaml` (instructions are in that
file).

---

## What's where (for reference)

| Part of the site | Lives in | Served at |
|------------------|----------|-----------|
| Toolkit Guide    | `dashboard/planning_dashboard/web/guide.html` | `/` |
| Planning Wiki    | `wiki-src/content/…` (Quartz markdown)        | `/wiki` |
| Planning Map     | `dashboard/` app + `data/planning.sqlite`     | `/map` |
| Build recipe     | `Dockerfile`                                  | — |
| Deploy settings  | `render.yaml`                                 | — |

To run the whole thing locally with Docker (optional, for testing):

```powershell
docker build -t glos-planning .
docker run -p 8000:8000 glos-planning
# then open http://localhost:8000
```
