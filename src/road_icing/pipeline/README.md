# Data ingestion pipeline — pending actual competition files

This directory is intentionally left without a guessed parser for the real data.

Codex should implement `prepare.py`, `spatial_join.py`, `temporal_align.py` after `inventory` identifies headers, units, periods, and spatial reference systems.

**Do not merge ASOS/AWS/RWIS naively on station_id**: IDs have source-specific namespaces and the station coordinates differ. Determine nearest/inverse-distance spatial interpolation in a projected CRS and time-align with data availability rules. Verify 10-minute cadence in the competition rules before aggregating source measurements.
