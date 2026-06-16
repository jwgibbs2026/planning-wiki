"use strict";

const DOT_COLOR = "#1976d2";

const map = L.map("map").setView([51.83, -2.15], 10); // Gloucestershire
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

const clusterLayer = L.markerClusterGroup();
map.addLayer(clusterLayer);

// --- Designation overlay layers (togglable, lazy-loaded) --------------------
// Drop the .geojson files into planning_dashboard/web/layers/ (served at
// /map/static/layers/). Each layer is fetched the first time it is switched on,
// so large files don't slow the initial map load. Missing files are skipped.
const LAYERS_BASE = "layers/";
const OVERLAY_DEFS = [
  { file: "Ancient Woodlands.geojson", label: "Ancient Woodland", color: "#1b5e20", fill: 0.35 },
  { file: "GlosSac.geojson", label: "Special Areas of Conservation (SAC)", color: "#6a1b9a", fill: 0.30 },
  { file: "SSSI.geojson", label: "SSSIs", color: "#ef6c00", fill: 0.30 },
  { file: "LWS layer.geojson", label: "Local Wildlife Sites", color: "#00838f", fill: 0.30 },
  { file: "borders.geojson", label: "Council borders", color: "#000", fill: 0.0, weight: 4 },
];

// Property keys commonly holding a feature's name in UK designation datasets.
const NAME_KEYS = [
  "name", "NAME", "Name", "SITE_NAME", "SITENAME", "SNAME", "sname",
  "SSSI_NAME", "LWS_NAME", "WOODNAME", "NNR_NAME", "SAC_NAME", "DESCRIPT",
  "Site_Name", "site_name", "REFERENCE", "ref",
];
function featureName(props) {
  if (!props) return null;
  for (const k of NAME_KEYS) if (props[k]) return props[k];
  return null;
}

const overlayGroups = {}; // label -> { group, def, loaded }
const overlays = { "Planning applications": clusterLayer };
for (const def of OVERLAY_DEFS) {
  const group = L.layerGroup();
  overlayGroups[def.label] = { group, def, loaded: false };
  overlays[def.label] = group;
}

const layerControl = L.control.layers(null, overlays, { collapsed: false }).addTo(map);

async function loadOverlay(entry) {
  if (entry.loaded) return;
  entry.loaded = true; // guard against re-entry while fetching
  const { def, group } = entry;
  try {
    const resp = await fetch(LAYERS_BASE + encodeURIComponent(def.file));
    if (!resp.ok) throw new Error("HTTP " + resp.status);
    const gj = await resp.json();
    const style = {
      color: def.color,
      weight: def.weight ?? 1,
      fillColor: def.color,
      fillOpacity: def.fill ?? 0.3,
      dashArray: def.dashArray,
    };
    const gjLayer = L.geoJSON(gj, {
      style,
      pointToLayer: (f, latlng) =>
        L.circleMarker(latlng, { radius: 5, color: def.color, fillColor: def.color, fillOpacity: 0.6, weight: 1 }),
      onEachFeature: (f, lyr) => {
        const nm = featureName(f.properties);
        lyr.bindPopup(
          `<div class="popup"><strong>${esc(def.label)}</strong>${nm ? "<br>" + esc(nm) : ""}</div>`
        );
      },
    });
    group.addLayer(gjLayer);
  } catch (e) {
    entry.loaded = false; // allow a retry on next toggle
    console.warn(`Overlay "${def.label}" could not be loaded (${e.message}). ` +
      `Place "${def.file}" in planning_dashboard/web/layers/.`);
  }
}

map.on("overlayadd", (e) => {
  const entry = overlayGroups[e.name];
  if (entry) loadOverlay(entry);
});

// Expose for debugging/inspection in the browser console.
window._dash = { map, clusterLayer, layerControl, overlayGroups };

function esc(s) {
  return (s == null ? "" : String(s)).replace(/[&<>"]/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])
  );
}

function popupHtml(p) {
  const links = [];
  if (p.official_url)
    links.push(`<a href="${esc(p.official_url)}" target="_blank" rel="noopener">Official council page &rarr;</a>`);
  if (p.planit_url)
    links.push(`<a href="${esc(p.planit_url)}" target="_blank" rel="noopener">PlanIt</a>`);
  return `<div class="popup">
    <h3>${esc(p.ref || "Application")}</h3>
    <div class="meta">${esc(p.authority)}</div>
    <div class="meta">${esc(p.address || "")}</div>
    <div class="desc">${esc(p.description || "")}</div>
    <div class="meta">Status: ${esc(p.status || "?")}</div>
    <div class="meta">Received: ${esc(p.received_date || "?")}${
    p.decision_date ? " &middot; Decided: " + esc(p.decision_date) : ""
  }</div>
    <div style="margin-top:6px">${links.join(" &nbsp;|&nbsp; ")}</div>
  </div>`;
}

// All applications are loaded once from a static file, then filtered in the
// browser — so the map needs no running server and hosts anywhere static.
const DATA_URL = "applications.geojson";
let ALL_FEATURES = null;

async function ensureData() {
  if (ALL_FEATURES) return ALL_FEATURES;
  const resp = await fetch(DATA_URL);
  if (!resp.ok) throw new Error("HTTP " + resp.status);
  const data = await resp.json();
  ALL_FEATURES = data.features || [];
  // Populate the status dropdown from the full dataset, once.
  const statuses = new Set();
  for (const f of ALL_FEATURES) if (f.properties && f.properties.status) statuses.add(f.properties.status);
  populateStatusFilter(statuses);
  return ALL_FEATURES;
}

function withinDays(receivedDate, days) {
  if (!receivedDate) return false;
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - days);
  // received_date is an ISO 'YYYY-MM-DD' string; lexical compare is safe.
  return receivedDate >= cutoff.toISOString().slice(0, 10);
}

async function load() {
  const authority = document.getElementById("filter-authority").value;
  const status = document.getElementById("filter-status").value;
  const days = document.getElementById("filter-days").value;

  const countEl = document.getElementById("count");
  countEl.textContent = "Loading…";

  let features;
  try {
    features = await ensureData();
  } catch (e) {
    countEl.textContent = "Error loading applications: " + e.message;
    return;
  }

  if (authority) features = features.filter((f) => f.properties.authority === authority);
  if (status) features = features.filter((f) => f.properties.status === status);
  if (days) features = features.filter((f) => withinDays(f.properties.received_date, parseInt(days, 10)));

  clusterLayer.clearLayers();
  let plotted = 0;

  for (const f of features) {
    const p = f.properties;
    const geom = f.geometry;
    if (!geom) continue;

    // Plot every application as a dot (use the point, or a polygon's first vertex).
    let lat, lng;
    if (geom.type === "Point") {
      [lng, lat] = geom.coordinates;
    } else {
      const c = L.geoJSON(geom).getBounds().getCenter();
      lat = c.lat;
      lng = c.lng;
    }
    const marker = L.circleMarker([lat, lng], {
      radius: 6,
      color: "#fff",
      weight: 1,
      fillColor: DOT_COLOR,
      fillOpacity: 0.9,
    });
    marker.bindPopup(popupHtml(p));
    clusterLayer.addLayer(marker);
    plotted++;
  }

  countEl.textContent = `${plotted} application${plotted === 1 ? "" : "s"} shown`;
}

let statusFilterPopulated = false;
function populateStatusFilter(statuses) {
  if (statusFilterPopulated) return;
  const sel = document.getElementById("filter-status");
  [...statuses].sort().forEach((s) => {
    const opt = document.createElement("option");
    opt.value = s;
    opt.textContent = s;
    sel.appendChild(opt);
  });
  statusFilterPopulated = true;
}

async function loadAuthorities() {
  try {
    const resp = await fetch("authorities.json");
    const list = await resp.json();
    const sel = document.getElementById("filter-authority");
    list.forEach((a) => {
      const opt = document.createElement("option");
      opt.value = a.name;
      opt.textContent = a.name;
      sel.appendChild(opt);
    });
  } catch (e) {
    /* non-fatal */
  }
}

document.getElementById("apply").addEventListener("click", load);
loadAuthorities().then(load);
