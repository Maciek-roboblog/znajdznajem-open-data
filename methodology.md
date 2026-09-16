# Methodology

## Sources

ZnajdzNajem aggregates rental listings from 10 monitored Polish sources and channels, including real estate portals and Facebook channels.
The exact list is in [src/constants/sources.js](https://github.com/Maciek-roboblog/znajdznajem/blob/main/app/frontend/src/constants/sources.js).

## What is an "active offer"

Live report counts use the app's public active-offer filter: active rental listings that have not been deactivated and pass its visibility and data-quality checks, including duplicate exclusions. There is no general "discovered in the last 60 days" rule. Reports also apply the analysis price range described by `price_sample` in the JSON payload when present.

The current definition lives in `app/src/mieszkania/services/stats_definitions.py` and the public endpoint `/api/v1/stats/definitions`. Older archived snapshots reflect the rules used when they were generated; they are not recalculated by this publisher.

## Update cadence

- **Raw ingest**: continuous (scrapers run on rolling schedule)
- **Open-data snapshot**: weekly (Monday ~06:00 Europe/Warsaw)
- **Monthly report**: copies each available `/stats/report/archive?city=…&month=YYYY-MM` snapshot; it does not select the first weekly file of the month

## Dates and periods

- `data/weekly/YYYY-WNN/` and the CSV `date` identify the publisher run. The `report` object is the live active-offer snapshot fetched at that run, not a count restricted to offers discovered that week. `data/latest/` is the most recently published weekly copy.
- `reports/YYYY-MM/` uses the archive's `generated_month`. The app captures the market state for that archive label; this is not a monthly average or a complete inventory of every listing seen during the month.
- `generated_at` records report generation. `data_as_of`, when present, is the underlying source-data timestamp; it does not certify that every offer was refreshed at that time. These timestamps can differ from the directory label and Git commit date.
- The publisher dates monthly commits to the first day of the following month, including backfills. Use the JSON timestamps for the snapshot's timing, not Git history alone.
- Flow measures such as `new_offers_last_7d` use their own stated observation window and must not be interpreted as the active-offer count's window.

## Deduplication

Offers appearing on multiple portals are deduplicated by:
- perceptual image hash (pHash distance ≤ 6)
- normalized address + price + area match
Counted once in `active_offers`.

## Caveats

- Supply-side data only: we don't track actual rent agreements signed.
- Sample skews toward portals that allow scraping (excludes private/closed listings).
- Price is asking price, not transaction price.
