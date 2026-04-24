# Methodology

## Sources

ZnajdzNajem aggregates rental listings from 10 Polish real estate portals.
The exact list is in [src/constants/sources.js](https://github.com/Maciek-roboblog/znajdz/blob/main/app/frontend/src/constants/sources.js).

## What is an "active offer"

An offer counts as active if:
- discovered by one of our scrapers in the last 60 days
- not marked deactivated via HTTP 410/404 from source portal
- not flagged as duplicate by the image-hash dedup system

Full definition lives in `app/src/mieszkania/services/stats_definitions.py` and the public endpoint `/api/v1/stats/definitions`.

## Update cadence

- **Raw ingest**: continuous (scrapers run on rolling schedule)
- **Open-data snapshot**: weekly (Monday ~06:00 Europe/Warsaw)
- **Monthly report**: first snapshot of the month

## Deduplication

Offers appearing on multiple portals are deduplicated by:
- perceptual image hash (pHash distance ≤ 6)
- normalized address + price + area match
Counted once in `active_offers`.

## Caveats

- Supply-side data only: we don't track actual rent agreements signed.
- Sample skews toward portals that allow scraping (excludes private/closed listings).
- Price is asking price, not transaction price.
