#!/usr/bin/env python3
"""Publish znajdznajem open data.

Weekly:  data/weekly/YYYY-WNN/ + data/latest/  (from live /stats/report + /stats/market/dynamics)
Monthly: reports/YYYY-MM/<city>.md + .json for every month the API has an archive
         snapshot for and this repo does not have yet (backfill + ongoing, one
         commit per month, dated 1st of the following month).

Usage: publish.py [--date YYYY-MM-DD] [--dry-run] [--api http://127.0.0.1:8001/api/v1]
       dry-run = write files, no git; --api = bypass the public rate limiter when run on the server
Stdlib only. Runs from cron on the znajdznajem server, see README.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

API = "https://znajdznajem.pl/api/v1"  # overridden by --api (cron uses the local uvicorn port)
SITE = "https://znajdznajem.pl"
PUBLIC_API = f"{SITE}/api/v1"  # for links inside published reports
REPO = Path(__file__).resolve().parents[1]
MONTHS_PL = [
    "", "styczeń", "luty", "marzec", "kwiecień", "maj", "czerwiec",
    "lipiec", "sierpień", "wrzesień", "październik", "listopad", "grudzień",
]
CSV_FIELDS = [
    "date", "city_slug", "city_name", "landing_url", "new_offers_url", "students_url", "rooms_url",
    "active_offers", "median_price", "avg_price_per_m2", "avg_price", "cheapest_district",
    "expensive_district", "top_source", "top_price_range", "new_offers_last_day", "new_offers_last_7d",
]


def get(path: str, **params):
    url = f"{API}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "znajdznajem-open-data/1.0"})
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None
            if exc.code != 429:
                raise
            wait = int(exc.headers.get("Retry-After") or 0) or 15 * (attempt + 1)
            print(f"  429 on {path}, sleeping {wait}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"gave up on {url} after repeated 429")


def fmt(n) -> str:
    return "—" if n in (None, "") else f"{int(n):,}".replace(",", " ")


def bucket(start) -> str:
    return "—" if start in (None, "") else f"{fmt(start)}-{fmt(int(start) + 499)} zł"


def top_bucket(dist: list[dict]) -> str:
    return bucket(max(dist, key=lambda r: r.get("count", 0)).get("price")) if dist else "—"


def cheapest_expensive(districts: list[dict]) -> tuple[str, str]:
    priced = [d for d in districts if d.get("avg_price")]
    if not priced:
        return "—", "—"
    return (min(priced, key=lambda d: d["avg_price"])["name"], max(priced, key=lambda d: d["avg_price"])["name"])


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data) -> None:
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def md_table(header: list[str], rows: list[list]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def prepend_changelog(entry: str) -> None:
    path = REPO / "CHANGELOG.md"
    head, sep, tail = path.read_text(encoding="utf-8").partition("\n---\n")
    write(path, f"{head}{sep}\n{entry.rstrip()}\n{tail}")


def git(*args: str, when: datetime | None = None) -> None:
    env = os.environ.copy()
    if when:
        stamp = when.strftime("%Y-%m-%dT%H:%M:%S+02:00")
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = stamp
    subprocess.run(["git", *args], cwd=REPO, env=env, check=True)


def commit(msg: str, when: datetime, dry_run: bool) -> None:
    if dry_run:
        print(f"[dry-run] would commit: {msg} @ {when:%Y-%m-%d}")
        return
    git("add", "-A")
    git("commit", "-q", "-m", msg, when=when)


# ---------------------------------------------------------------- weekly

def city_row(run_date: date, city: dict) -> tuple[dict | None, dict | None]:
    slug = city["slug"]
    report = get("/stats/report", city=slug)
    dynamics = get("/stats/market/dynamics", city=slug) or {}
    if not report:
        return None, None
    ov = report.get("overview") or {}
    daily = dynamics.get("daily_new_offers") or []
    cheap, expensive = cheapest_expensive(report.get("districts") or [])
    sources = report.get("sources") or []
    row = {
        "date": run_date.isoformat(),
        "city_slug": slug,
        "city_name": city["name"],
        "landing_url": f"{SITE}/{slug}",
        "new_offers_url": f"{SITE}/{slug}/nowe-oferty",
        "students_url": f"{SITE}/{slug}/dla-studentow",
        "rooms_url": f"{SITE}/{slug}/pokoje",
        "active_offers": int(ov.get("total_offers") or 0),
        "median_price": int(ov.get("median_price") or 0),
        "avg_price_per_m2": int(ov.get("avg_price_per_m2") or 0),
        "avg_price": int(ov.get("avg_price") or 0),
        "cheapest_district": cheap,
        "expensive_district": expensive,
        "top_source": str(sources[0].get("source")) if sources else "—",
        "top_price_range": top_bucket(report.get("price_distribution") or []),
        "new_offers_last_day": int(daily[-1].get("new_offers") or 0) if daily else 0,
        "new_offers_last_7d": sum(int(d.get("new_offers") or 0) for d in daily),
    }
    return row, {"report": report, "dynamics": dynamics}


def weekly(run_date: date, cities: list[dict], dry_run: bool) -> None:
    y, w, _ = run_date.isocalendar()
    week = f"{y}-W{w:02d}"
    dest = REPO / "data" / "weekly" / week
    latest = REPO / "data" / "latest"
    if dest.exists():
        print(f"weekly {week}: already published, skipping")
        return
    rows = []
    for city in cities:
        row, raw = city_row(run_date, city)
        if not row:
            print(f"  {city['slug']}: no report, skipped")
            continue
        rows.append(row)
        write_json(dest / f"{city['slug']}.json", row)
        write_json(dest / "raw" / f"{city['slug']}.json", raw)
    with (dest / "city-stats.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    shutil.rmtree(latest, ignore_errors=True)
    shutil.copytree(dest, latest)
    prepend_changelog(
        f"## {week} — {run_date.isoformat()}\n\nWeekly snapshot, {len(rows)} cities → `data/weekly/{week}/`\n\n"
        + "\n".join(f"- **{r['city_name']}**: {fmt(r['active_offers'])} aktywne · mediana {fmt(r['median_price'])} zł · {r['avg_price_per_m2']} zł/m²" for r in rows)
        + "\n"
    )
    commit(f"data: weekly snapshot {week} ({len(rows)} cities)", datetime.combine(run_date, datetime.min.time()).replace(hour=6), dry_run)
    print(f"weekly {week}: {len(rows)} cities")


# ---------------------------------------------------------------- monthly

def render_report(month: str, city: dict, r: dict) -> str:
    yr, mo = month.split("-")
    label = f"{MONTHS_PL[int(mo)]} {yr}"
    name, slug = city["name"], city["slug"]
    ov = r.get("overview") or {}
    districts = sorted([d for d in (r.get("districts") or []) if d.get("avg_price")], key=lambda d: d["avg_price"])
    cheap, expensive = cheapest_expensive(districts)
    sources = r.get("sources") or []
    rooms = r.get("by_rooms") or []
    top_src = sources[0]["source"] if sources else "—"
    parts = [
        f"# Rynek wynajmu: {name} — raport {label}",
        "",
        "> **Open data z 10 portali rental** · ZnajdzNajem · MIT license · wolno cytować",
        "",
        "## Headlines (tweetable)",
        "",
        f"- **{fmt(ov.get('total_offers'))}** aktywnych ofert wynajmu — {name}, {label}",
        f"- Mediana: **{fmt(ov.get('median_price'))} zł/mies.** · cena za m²: **{fmt(ov.get('avg_price_per_m2'))} zł**",
        f"- Najwięcej ofert w widełkach **{top_bucket(r.get('price_distribution') or [])}**",
        f"- Najtańsza dzielnica: **{cheap}** · najdroższa: **{expensive}**",
    ]
    parts += [f"- {i['text']}" for i in (r.get("insights") or []) if i.get("text")]
    parts += [
        "",
        "## Szczegółowe statystyki",
        "",
        md_table(["Wskaźnik", "Wartość"], [
            ["Aktywne oferty", fmt(ov.get("total_offers"))],
            ["Mediana ceny miesięcznej", f"{fmt(ov.get('median_price'))} zł"],
            ["Średnia cena miesięczna", f"{fmt(ov.get('avg_price'))} zł"],
            ["Średnia cena za m²", f"{fmt(ov.get('avg_price_per_m2'))} zł"],
            ["Średni metraż", f"{fmt(ov.get('avg_area'))} m²"],
            ["Najczęstsze widełki cenowe", top_bucket(r.get("price_distribution") or [])],
            ["Najtańsza dzielnica", cheap],
            ["Najdroższa dzielnica", expensive],
            ["Największe źródło ofert", top_src],
        ]),
    ]
    if rooms:
        parts += ["", "## Według liczby pokoi", "", md_table(
            ["Pokoje", "Oferty", "Mediana", "Średni metraż", "zł/m²"],
            [[x.get("rooms"), fmt(x.get("offer_count")), f"{fmt(x.get('median_price'))} zł", f"{fmt(x.get('avg_area'))} m²", fmt(x.get("price_per_m2"))] for x in rooms],
        )]
    if districts:
        parts += ["", "## Dzielnice (od najtańszej)", "", md_table(
            ["Dzielnica", "Oferty", "Średnia cena"],
            [[d["name"], fmt(d.get("offer_count")), f"{fmt(d['avg_price'])} zł"] for d in districts],
        )]
    if sources:
        parts += ["", "## Źródła ofert", "", md_table(
            ["Portal", "Oferty", "Udział"],
            [[s.get("source"), fmt(s.get("offer_count")), f"{s.get('pct', '—')}%"] for s in sources],
        )]
    parts += [
        "",
        "## Metodologia",
        "",
        "Miesięczny snapshot aktywnych ofert z 10 polskich portali ogłoszeniowych, po deduplikacji. "
        "Ceny to ceny ofertowe (asking), nie transakcyjne. Pełna definicja „aktywnej oferty”: "
        f"<{PUBLIC_API}/stats/definitions> · [methodology.md](../../methodology.md)",
        "",
        "## Dane źródłowe",
        "",
        f"- **JSON**: [`reports/{month}/{slug}.json`](./{slug}.json) — pełny snapshot (dzielnice, pokoje, źródła, rozkład cen)",
        f"- **Tygodniowe CSV**: [`data/weekly/`](../../data/weekly/)",
        f"- **Live dashboard**: {SITE}/{slug}/raport",
        f"- **Darmowy alert o nowych ofertach**: {SITE}/{slug}/nowe-oferty",
        "",
        "## Kontakt prasowy",
        "",
        "admin@znajdznajem.pl · [PRESS.md](../../PRESS.md)",
        "",
        "## Licencja",
        "",
        "MIT — wolno cytować, forkować, remixować. Preferowana atrybucja: "
        "ZnajdzNajem open data (<https://github.com/Maciek-roboblog/znajdznajem-open-data>)",
        "",
        "---",
        "",
        f"*Wygenerowano automatycznie ze snapshotu `/stats/report/archive?city={slug}&month={month}` przez `scripts/publish.py`.*",
        "",
    ]
    return "\n".join(parts)


def monthly(cities: list[dict], dry_run: bool) -> None:
    months = sorted((get("/stats/report/months", city="krakow") or {}).get("months") or [])
    for month in months:
        out = REPO / "reports" / month
        if out.exists():
            continue
        yr, mo = (int(x) for x in month.split("-"))
        done = []
        for city in cities:
            r = get("/stats/report/archive", city=city["slug"], month=month)
            if not r:
                continue
            write(out / f"{city['slug']}.md", render_report(month, city, r))
            write_json(out / f"{city['slug']}.json", r)
            done.append((city, r))
        if not done:
            continue
        label = f"{MONTHS_PL[mo]} {yr}"
        write(out / "README.md", "\n".join([
            f"# Rynek wynajmu w Polsce — raport {label}",
            "",
            "> **Open data z 10 portali rental** · ZnajdzNajem · MIT license · wolno cytować",
            "",
            f"## Miasta w tym raporcie ({len(done)})",
            "",
            md_table(["Miasto", "Aktywne oferty", "Mediana", "zł/m²"], [
                [f"[{c['name']}](./{c['slug']}.md)", fmt(r['overview'].get('total_offers')), f"{fmt(r['overview'].get('median_price'))} zł", fmt(r['overview'].get('avg_price_per_m2'))]
                for c, r in sorted(done, key=lambda cr: -(cr[1]['overview'].get('total_offers') or 0))
            ]),
            "",
            "## Kontakt prasowy",
            "",
            "admin@znajdznajem.pl · [PRESS.md](../../PRESS.md)",
            "",
            "## Licencja",
            "",
            "MIT — wolno cytować, forkować, remixować.",
            "",
        ]))
        # snapshot for month M is produced by the app on the 1st of M+1 → date the commit there
        published = (date(yr, mo, 1) + timedelta(days=32)).replace(day=1)
        prepend_changelog(f"## Raport {month} — {published.isoformat()}\n\nMiesięczne raporty dla {len(done)} miast → `reports/{month}/`\n")
        commit(f"reports: monthly report {month} ({len(done)} cities)", datetime.combine(published, datetime.min.time()).replace(hour=6), dry_run)
        print(f"monthly {month}: {len(done)} cities")


def main() -> int:
    global API
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="", help="run date YYYY-MM-DD (default today)")
    ap.add_argument("--dry-run", action="store_true", help="write files, skip git commit/push")
    ap.add_argument("--api", default=API, help=f"API base URL (default {API})")
    args = ap.parse_args()
    API = args.api.rstrip("/")
    run_date = date.fromisoformat(args.date) if args.date else date.today()
    cities = (get("/stats/cities/summary") or {}).get("cities") or []
    if not args.dry_run:
        git("pull", "-q", "--rebase")
    monthly(cities, args.dry_run)
    weekly(run_date, cities, args.dry_run)
    if not args.dry_run:
        git("push", "-q")
    return 0


if __name__ == "__main__":
    sys.exit(main())
