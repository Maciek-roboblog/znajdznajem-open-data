# znajdznajem-open-data

**Open data rental market snapshots for Poland.**  
Weekly aggregated from 10 major rental portals by [znajdznajem.pl](https://znajdznajem.pl). 21 cities.

Released under MIT license — free to cite, fork, embed, analyze.

## Content

- `reports/YYYY-MM/` — monthly market reports per city (markdown + full JSON snapshot: districts, rooms, sources, price distribution)
- `data/weekly/YYYY-WNN/` — weekly snapshots: `city-stats.csv`, `<city>.json` (one row per city), `raw/<city>.json` (full report payload)
- `data/latest/` — always-current snapshot (overwritten weekly)
- `methodology.md` — how the data is collected, what counts as an "active offer", refresh cadence
- `scripts/publish.py` — the publisher (stdlib Python, runs from cron on the znajdznajem server)

## For journalists / bloggers

- **Cite freely.** License is MIT.
- **Press contact**: see `PRESS.md`.
- **Charts**: raw data is in CSV/JSON — plug into your chart tool.
- **Monthly report headlines** live in `reports/YYYY-MM/<city>.md` under `## Headlines` section. Tweetable, quotable.

## For developers

```bash
# Get latest active-offer counts
curl https://raw.githubusercontent.com/Maciek-roboblog/znajdznajem-open-data/main/data/latest/city-stats.csv
curl https://raw.githubusercontent.com/Maciek-roboblog/znajdznajem-open-data/main/data/latest/krakow.json | jq
```

## For researchers

Time series of snapshots in `data/weekly/` — use for academic work, just cite source.

## Refresh cadence

Every Monday 06:00 Europe/Warsaw via cron (`scripts/publish.py`). Monthly reports are added on the first Monday after the app publishes the month's archive snapshot (1st of the following month) and are committed with that date.

Note: 2026-W17 is the only weekly snapshot before 2026-W35 — the pipeline was not automated until 2026-08-25. Monthly reports 2026-03…2026-07 were backfilled from the app's archive snapshots (`/api/v1/stats/report/archive`).
