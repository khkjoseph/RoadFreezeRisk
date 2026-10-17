# Data handling

Competition datasets are NOT bundled here. Raw files belong under `data/raw/` and must never be committed to public GitHub without permission.

- rwis/ : road weather stations (pavement status and surface temperature)
- asos/ : synoptic observations
- aws/ : automatic/disaster-prevention weather observations
- roads/bridge_tunnel/ : start/end points and shape information
- roads/centerline/ : highway geospatial polylines
- terrain/elevation/ : terrain height / DEM
- hydro/rivers/ : river boundary geometries
- interim/ : normalized, per-source data
- processed/ : joined model tables
- external/ : only officially permitted external reference data

Keep `.shp` and accompanying `.shx`, `.dbf`, `.prj`, `.cpg` sidecars together. Note source, download date, license, coordinate reference system, and units.
