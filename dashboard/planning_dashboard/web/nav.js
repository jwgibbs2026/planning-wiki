// Shared top nav bar for the static site (Toolkit Guide | Planning Wiki |
// Planning Map). On a static host there is no server to inject the bar, so this
// script adds it to every page. It no-ops if a bar is already present (e.g. when
// the page is served by the FastAPI app, which injects its own).
(function () {
  if (document.querySelector(".pmap-topbar")) return;

  var path = location.pathname.replace(/index\.html$/, "");
  var active = "guide";
  if (path.indexOf("/map") === 0) active = "map";
  else if (path.indexOf("/wiki") === 0) active = "wiki";

  var tabs = [
    { id: "guide", label: "Toolkit Guide", href: "/" },
    { id: "wiki", label: "Planning Wiki", href: "/wiki/" },
    { id: "map", label: "Planning Map", href: "/map/" },
  ];

  var bar = document.createElement("div");
  bar.className = "pmap-topbar";
  var links = tabs
    .map(function (t) {
      var cur = t.id === active ? ' aria-current="page"' : "";
      return '<a href="' + t.href + '" data-router-ignore' + cur + ">" + t.label + "</a>";
    })
    .join("");
  bar.innerHTML =
    '<span class="pmap-brand">Gloucestershire Planning</span>' +
    '<nav class="pmap-tabs">' + links + "</nav>";

  var style = document.createElement("style");
  style.textContent =
    ".pmap-topbar{position:sticky;top:0;z-index:10000;display:flex;align-items:center;" +
    "gap:1.25rem;padding:.5rem 1rem;background:#2d6a2d;color:#fff;" +
    'font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;' +
    "box-shadow:0 1px 4px rgba(0,0,0,.25)}" +
    ".pmap-brand{font-weight:700;letter-spacing:.01em}" +
    ".pmap-tabs{display:flex;gap:.25rem}" +
    ".pmap-tabs a{color:#fff;text-decoration:none;font-weight:600;padding:.3rem .8rem;" +
    "border-radius:6px;line-height:1}" +
    ".pmap-tabs a:hover{background:rgba(255,255,255,.15)}" +
    '.pmap-tabs a[aria-current="page"]{background:rgba(255,255,255,.25)}';

  document.head.appendChild(style);
  document.body.insertBefore(bar, document.body.firstChild);
})();
