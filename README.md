# znajdznajem-open-data

**Open data rental market snapshots for Poland.**  
Weekly aggregated from 10 major rental portals by [znajdznajem.pl](https://znajdznajem.pl).

Released under MIT license — free to cite, fork, embed, analyze.

## Content

- `reports/YYYY-MM/` — monthly market reports per city (article-style markdown with charts data, OG-ready headlines, press quotes)
- `data/weekly/YYYY-WNN/` — raw weekly snapshots (JSON + CSV)
- `data/latest/` — always-current snapshot (overwritten weekly)
- `methodology.md` — how the data is collected, what counts as an "active offer", refresh cadence

## For journalists / bloggers

- **Cite freely.** License is MIT.
- **Press contact**: see `PRESS.md`.
- **Charts**: raw data is in CSV/JSON — plug into your chart tool.
- **Monthly report headlines** live in `reports/YYYY-MM/<city>.md` under `## Headlines` section. Tweetable, quotable.

## For developers

```bash
# Get latest active-offer counts
curl https://raw.githubusercontent.com/Maciek-roboblog/znajdznajem-open-data/main/data/latest/city-stats.json | jq
```

## For researchers

Time series of snapshots in `data/weekly/` — use for academic work, just cite source.

## Refresh cadence

Every Monday ~06:00 Europe/Warsaw. Automated by Jenkins job `znajdznajem/marketing-weekly`.
