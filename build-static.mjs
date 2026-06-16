// Assemble the fully static site into ./dist for static hosting (Netlify,
// Cloudflare Pages, GitHub Pages, ...).
//
// Run AFTER the Quartz wiki has been built (see netlify.toml):
//   dist/                     ← publish this
//     index.html              ← Toolkit Guide (site root / opening tab)
//     nav.js                  ← shared top nav bar
//     map/                    ← Planning Map (Leaflet + static data)
//       index.html app.js style.css authorities.json applications.geojson
//       layers/*.geojson
//     wiki/                   ← built Quartz site, nav.js injected into each page
import { promises as fs } from "node:fs";
import path from "node:path";

const ROOT = path.resolve(".");
const WEB = path.join(ROOT, "dashboard", "planning_dashboard", "web");
const WIKI_PUBLIC = path.join(ROOT, "wiki-src", "public");
const DIST = path.join(ROOT, "dist");

const NAV_TAG = '<script src="/nav.js" defer></script>';

async function copy(src, dest) {
  await fs.cp(src, dest, { recursive: true });
}

async function injectNav(dir) {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  for (const e of entries) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) {
      await injectNav(full);
    } else if (e.name.endsWith(".html")) {
      let html = await fs.readFile(full, "utf8");
      if (html.includes("/nav.js")) continue;
      if (html.includes("</body>")) html = html.replace("</body>", NAV_TAG + "\n</body>");
      else html += NAV_TAG;
      await fs.writeFile(full, html);
    }
  }
}

async function main() {
  await fs.rm(DIST, { recursive: true, force: true });
  await fs.mkdir(path.join(DIST, "map", "layers"), { recursive: true });

  // 1. Toolkit Guide at the site root.
  await fs.copyFile(path.join(WEB, "guide.html"), path.join(DIST, "index.html"));

  // 2. Shared nav bar at the root.
  await fs.copyFile(path.join(WEB, "nav.js"), path.join(DIST, "nav.js"));

  // 3. Planning Map assets + static data.
  for (const f of ["index.html", "app.js", "style.css", "authorities.json", "applications.geojson"]) {
    await fs.copyFile(path.join(WEB, f), path.join(DIST, "map", f));
  }
  // Designation overlay layers (whatever is present).
  const layersSrc = path.join(WEB, "layers");
  try {
    for (const f of await fs.readdir(layersSrc)) {
      if (f.endsWith(".geojson")) await fs.copyFile(path.join(layersSrc, f), path.join(DIST, "map", "layers", f));
    }
  } catch { /* no layers dir — fine */ }

  // 4. Built Quartz wiki under /wiki, with the nav injected into every page.
  if (!(await fs.stat(WIKI_PUBLIC).catch(() => null))) {
    throw new Error(`Wiki build missing at ${WIKI_PUBLIC}. Run the Quartz build first.`);
  }
  await copy(WIKI_PUBLIC, path.join(DIST, "wiki"));
  await injectNav(path.join(DIST, "wiki"));

  console.log("Static site assembled in ./dist");
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
