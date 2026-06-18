// Shared top nav bar for the static site (Toolkit Guide | Planning Wiki |
// Planning Map). On a static host there is no server to inject the bar, so this
// script adds it to every page. It no-ops if a bar is already present.
//
// Brand: Gloucestershire Wildlife Trust — Neighbourhood Nature.
// Palette: Manilla base (#F7ECDF), Kelp (#058295), Fly Agaric (#E9511D).
// Type: Rubik (body) + Bitter (headings), loaded from Google Fonts.
(function () {
  if (document.querySelector(".pmap-topbar")) return;

  // Ensure the brand fonts are available on every page.
  if (!document.querySelector('link[data-pmap-fonts]')) {
    var pre1 = document.createElement("link");
    pre1.rel = "preconnect";
    pre1.href = "https://fonts.googleapis.com";
    var pre2 = document.createElement("link");
    pre2.rel = "preconnect";
    pre2.href = "https://fonts.gstatic.com";
    pre2.crossOrigin = "anonymous";
    var font = document.createElement("link");
    font.rel = "stylesheet";
    font.setAttribute("data-pmap-fonts", "");
    font.href =
      "https://fonts.googleapis.com/css2?family=Bitter:ital,wght@0,400;0,600;0,700;1,400&family=Rubik:ital,wght@0,400;0,500;0,700;1,400&display=swap";
    document.head.appendChild(pre1);
    document.head.appendChild(pre2);
    document.head.appendChild(font);
  }

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
    '<a class="pmap-logo" href="/" data-router-ignore aria-label="Gloucestershire Wildlife Trust — home">' +
    '<img src="/assets/gwt-logo.png" alt="Gloucestershire Wildlife Trust" />' +
    '<span class="pmap-sub">Neighbourhood<br/>Nature</span>' +
    "</a>" +
    '<nav class="pmap-tabs" aria-label="Sections">' + links + "</nav>";

  var style = document.createElement("style");
  style.textContent =
    ".pmap-topbar{position:sticky;top:0;z-index:10000;display:flex;align-items:center;" +
    "gap:1rem;padding:.45rem 1.1rem;background:#fffaf2;border-bottom:3px solid #058295;" +
    "font-family:'Rubik',system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;" +
    "box-shadow:0 1px 6px rgba(42,38,34,.10)}" +
    ".pmap-logo{display:flex;align-items:center;gap:.65rem;text-decoration:none}" +
    ".pmap-logo img{height:34px;width:auto;display:block}" +
    ".pmap-sub{font-size:.62rem;text-transform:uppercase;letter-spacing:.13em;font-weight:600;" +
    "color:#058295;line-height:1.15;border-left:2px solid #e3d6c3;padding-left:.65rem}" +
    ".pmap-tabs{display:flex;gap:.25rem;margin-left:auto;flex-wrap:wrap}" +
    ".pmap-tabs a{color:#058295;text-decoration:none;font-weight:500;font-size:.95rem;" +
    "padding:.35rem .85rem;border-radius:7px;line-height:1;transition:background .15s,color .15s}" +
    ".pmap-tabs a:hover{background:#F7ECDF}" +
    '.pmap-tabs a[aria-current="page"]{background:#058295;color:#fff}' +
    "@media (max-width:560px){.pmap-sub{display:none}.pmap-logo img{height:30px}" +
    ".pmap-tabs a{padding:.3rem .6rem;font-size:.85rem}}";

  document.head.appendChild(style);
  document.body.insertBefore(bar, document.body.firstChild);
})();
