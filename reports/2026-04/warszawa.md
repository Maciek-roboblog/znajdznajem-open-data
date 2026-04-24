# Rynek wynajmu w Warszawie — raport kwiecień 2026

<!--
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "name": "Rynek wynajmu w Warszawie — raport kwiecień 2026",
  "description": "Miesięczny agregat aktywnych ofert wynajmu w Warszawie (kwiecień 2026). 9 780 aktywnych ofert · mediana 2 950 zł miesięcznie. Źródło: agregat z 10 polskich portali ogłoszeniowych (OLX, Otodom, Gratka, Morizon i 6 innych). Aktualizacja: tygodniowa. License: MIT.",
  "url": "https://github.com/Maciek-roboblog/znajdznajem-open-data/blob/main/reports/2026-04/warszawa.md",
  "sameAs": "https://znajdznajem.pl/warszawa/raport",
  "temporalCoverage": "2026-04",
  "spatialCoverage": {
    "@type": "Place",
    "name": "Warszawa",
    "containedInPlace": {
      "@type": "Country",
      "name": "Poland"
    }
  },
  "creator": {
    "@type": "Organization",
    "name": "ZnajdzNajem",
    "url": "https://znajdznajem.pl",
    "contactPoint": {
      "@type": "ContactPoint",
      "email": "admin@znajdznajem.pl",
      "contactType": "Press"
    }
  },
  "license": "https://opensource.org/licenses/MIT",
  "isAccessibleForFree": true,
  "keywords": [
    "rynek najmu",
    "wynajem mieszkań",
    "ceny najmu Warszawa",
    "open data",
    "Polska",
    "Warszawa"
  ],
  "variableMeasured": [
    {
      "@type": "PropertyValue",
      "name": "active_offers",
      "description": "Liczba aktywnych ofert (60-day window)"
    },
    {
      "@type": "PropertyValue",
      "name": "median_price",
      "description": "Mediana ceny miesięcznej (zł)"
    },
    {
      "@type": "PropertyValue",
      "name": "avg_price_per_m2",
      "description": "Średnia cena za metr kwadratowy (zł)"
    },
    {
      "@type": "PropertyValue",
      "name": "top_price_range",
      "description": "Najczęstsze widełki cenowe"
    },
    {
      "@type": "PropertyValue",
      "name": "cheapest_district",
      "description": "Dzielnica z najniższą medianą"
    },
    {
      "@type": "PropertyValue",
      "name": "most_expensive_district",
      "description": "Dzielnica z najwyższą medianą"
    }
  ],
  "distribution": [
    {
      "@type": "DataDownload",
      "encodingFormat": "text/csv",
      "contentUrl": "https://raw.githubusercontent.com/Maciek-roboblog/znajdznajem-open-data/main/data/latest/city-stats.csv"
    },
    {
      "@type": "DataDownload",
      "encodingFormat": "application/json",
      "contentUrl": "https://raw.githubusercontent.com/Maciek-roboblog/znajdznajem-open-data/main/data/latest/warszawa.json"
    }
  ]
}
</script>
-->

> **Open data z 10 portali rental** · ZnajdzNajem · MIT license · wolno cytować

## Headlines (tweetable)

- **9 780** aktywnych ofert wynajmu w Warszawie w kwietniu 2026
- Mediana: **2 950 zł/mies.** · cena za m²: **84 zł**
- Najwięcej ofert w widełkach **1 000-1 499 zł**
- Najtańsza dzielnica: **Rembertów** · najdroższa: **Wilanów**

## Streszczenie

W kwietniu 2026 na rynku wynajmu w Warszawie odnotowaliśmy 9 780 aktywnych ofert wśród 10 tysięcy ogłoszeń z 10 największych portali. Mediana ceny to 2 950 zł miesięcznie.

Dane są agregatem publicznych ogłoszeń z OLX, Otodom, Gratka, Morizon i 6 innych portali. Wszystkie liczby są dostępne jako open data w repozytorium GitHub (patrz sekcja [Dane źródłowe](#dane-źródłowe)).

## Szczegółowe statystyki

| Wskaźnik | Wartość |
|---|---|
| Aktywne oferty | 9 780 |
| Mediana ceny miesięcznej | 2 950 zł |
| Średnia cena za m² | 84 zł |
| Najczęstsze widełki cenowe | 1 000-1 499 zł |
| Najtańsza dzielnica | Rembertów |
| Najdroższa dzielnica | Wilanów |
| Nowych ofert wczoraj | 12 |

## Co to znaczy dla najemców

Przy medianie 2 950 zł miesięcznie w Warszawie, najemca z budżetem 1 000-1 499 zł ma dziś do dyspozycji największą pulę ofert. Jeśli Twój budżet jest powyżej mediany, liczba dostępnych mieszkań maleje, ale konkurencja o nie również jest niższa. Warto śledzić alerty — dobre oferty w górnej połowie rozkładu znikają w ciągu 24-72h od publikacji.

Pełną mapę cen z per-dzielnicowym rozbiciem można obejrzeć tutaj:  
→ https://znajdznajem.pl/warszawa/mapa-cen

## Co to znaczy dla wynajmujących

Jeśli wynajmujesz mieszkanie w Warszawie, porównaj swoją cenę z medianą (2 950 zł) oraz z medianą per m² (84 zł). Ogłoszenia wycenione o >15% powyżej mediany wymagają średnio 3-4x dłuższego czasu na znalezienie najemcy (na podstawie danych o czasie życia ogłoszeń).

## Metodologia

- **Źródła danych**: 10 publicznych portali ogłoszeniowych (patrz [sources.js](https://github.com/Maciek-roboblog/znajdznajem-open-data/blob/main/methodology.md))
- **Aktywna oferta**: widoczna przez scraper w ostatnich 60 dniach, nie oznaczona jako usunięta, nie zduplikowana (pHash + adres+cena+metraż)
- **Cadence**: snapshot tygodniowy (poniedziałek 06:00 Europe/Warsaw)
- **Dedup**: perceptual image hash ≤6 + normalized adres

Pełna metodologia: <https://github.com/Maciek-roboblog/znajdznajem-open-data/blob/main/methodology.md>

## Dane źródłowe

- **CSV**: `data/weekly/2026-W04/warszawa.csv` w repo
- **JSON**: `data/weekly/2026-W04/warszawa.json`
- **Live dashboard**: https://znajdznajem.pl/warszawa/raport
- **Darmowy alert o nowych ofertach**: https://znajdznajem.pl/warszawa/nowe-oferty

## Kontakt prasowy

- **Email**: admin@znajdznajem.pl
- **Custom data cuts**: dostępne dla dziennikarzy i badaczy (patrz [PRESS.md](https://github.com/Maciek-roboblog/znajdznajem-open-data/blob/main/PRESS.md))

## Licencja

MIT — wolno cytować, forkować, remixować. Preferowana atrybucja: 
> ZnajdzNajem open data (<https://github.com/Maciek-roboblog/znajdznajem-open-data>)

---

*Raport wygenerowany automatycznie 2026-04-24T04:19:27 przez pipeline Jenkins `znajdznajem/marketing-weekly`.*
