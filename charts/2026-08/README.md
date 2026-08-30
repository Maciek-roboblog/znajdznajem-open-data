# Wykresy — sierpień 2026 (CC BY 4.0, do przedruku)

Dane: `/api/v1/stats/barometr` (tydzień 24–30.08 vs 17–23.08) + `/api/v1/stats/report` (stan live 30.08.2026) + odczyt z 20.08 (barometr). Ceny ofertowe, nie transakcyjne; agregacja 10 portali po deduplikacji. Metodologia: https://znajdznajem.pl/metodologia

| Plik | Co pokazuje |
|---|---|
| `01-barometr-kawalerki-top6.png` | aktywne kawalerki + mediana + zmiana t/t, 6 największych miast akademickich |
| `02-barometr-pokoje-top6.png` | to samo dla pokoi |
| `03-kawalerki-20-08-vs-30-08.png` | podaż kawalerek 20.08 vs 30.08 (+10–15%) |
| `04-indeks-mediany-sierpien-2026.png` | mediany cen ofertowych, 10 rynków, m/m vs lipiec (+ marker czerwca) |
| `city/<miasto>.png` | karta miasta: kawalerki, pokoje, mediana wg liczby pokoi |
| `hero-barometr.png` | ilustracja (bez danych) do okładek / press kitu |

Reprodukcja: `uv run --no-project --with matplotlib --with pillow python render.py` (czyta `data-pack.json`; pierwsza sekcja skryptu opisuje, skąd biorą się pola).

Cytowanie: „Źródło: Znajdź Najem, Indeks Najmu — sierpień 2026, https://znajdznajem.pl/raporty”.
