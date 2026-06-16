Designation overlay layers for the planning map
================================================

These GeoJSON files appear as togglable overlays in the layer control
(top-right of the map). Each is served at /map/static/layers/<file> and is
loaded the first time you switch it on.

Four of them are generated automatically by:

    python dashboard/scripts/fetch_layers.py

which pulls from official open data, reprojects to WGS84, and CLIPS everything
to the Gloucestershire boundary (so nothing outside the county is shown):

  Ancient Woodlands.geojson   "Ancient Woodland"   (Natural England)
  GlosSac.geojson             "Special Areas of Conservation (SAC)" (Natural England)
  SSSI.geojson                "SSSIs"              (Natural England)
  borders.geojson             "Council borders"    (ONS, the 6 Glos districts)

Supply this one yourself (it is NOT open data — held by GWT / GCER):

  LWS layer.geojson           "Local Wildlife Sites"

The map works without it; the Local Wildlife Sites toggle simply shows nothing
until the file is present.

Notes
-----
* GeoJSON must be in WGS84 / EPSG:4326 (lon,lat). The fetch script already does
  this; if you drop in your own LWS file and it appears off the map, it is
  probably British National Grid (EPSG:27700) and needs reprojecting first:
      ogr2ogr -t_srs EPSG:4326 "LWS layer.geojson" your_source.geojson
* To add / rename / restyle a layer, edit OVERLAY_DEFS in ../app.js.
