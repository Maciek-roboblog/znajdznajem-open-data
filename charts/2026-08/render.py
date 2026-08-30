import json
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image


ROOT = Path(__file__).parent
OUT = ROOT / "out"
CITY_OUT = OUT / "city"
OUT.mkdir(exist_ok=True)
CITY_OUT.mkdir(exist_ok=True)

with (ROOT / "data-pack.json").open(encoding="utf-8") as f:
    DATA = json.load(f)

FONT_FILE = ROOT / "fonts" / "Onest-Variable.ttf"
if FONT_FILE.exists():
    for weight in (400, 500, 650, 700, 750):
        static_file = FONT_FILE.with_name(f"Onest-{weight}.ttf")
        if not static_file.exists():
            font = instantiateVariableFont(TTFont(FONT_FILE), {"wght": weight})
            font["OS/2"].usWeightClass = weight
            font.save(static_file)
        fm.fontManager.addfont(static_file)
    FONT = "Onest"
else:
    FONT = "Noto Sans"

BG = "#f8f9ff"
SURFACE = "#fcfdff"
BORDER = "#dce6f4"
TEXT = "#0d1c2e"
SECONDARY = "#3f4c61"
MUTED = "#66758d"
BLUE = "#2563EB"
NAVY = "#003594"
AMBER = "#F59E0B"
GREEN = "#059669"
RED = "#dc2626"
PREVIOUS = "#c2cfe4"
FOOTER = "Źródło: Znajdź Najem — agregacja 10 portali po deduplikacji · stan 30.08.2026 · CC BY 4.0 · znajdznajem.pl/raporty"

plt.rcParams.update({
    "font.family": FONT,
    "text.color": TEXT,
    "axes.labelcolor": SECONDARY,
    "xtick.color": MUTED,
    "ytick.color": TEXT,
    "axes.edgecolor": BORDER,
})


def pl_int(value):
    return f"{int(value):,}".replace(",", "\u202f")


def pl_money(value):
    return f"{pl_int(value)} zł"


def pl_pct(value, signed=True):
    sign = "+" if signed and value > 0 else "−" if value < 0 else ""
    return f"{sign}{abs(value):.1f}%".replace(".", ",")


def base_figure(size, title, subtitle, title_size=21):
    fig = plt.figure(figsize=size, dpi=200, facecolor=BG)
    card = FancyBboxPatch(
        (0.025, 0.035), 0.95, 0.93,
        boxstyle="round,pad=0.006,rounding_size=0.018",
        transform=fig.transFigure, facecolor=SURFACE,
        edgecolor=BORDER, linewidth=0.8, zorder=-10,
    )
    fig.add_artist(card)
    fig.text(0.065, 0.93, "Znajdź Najem", color=NAVY, fontsize=13, fontweight=750, va="center")
    fig.text(0.210, 0.932, "•", color=AMBER, fontsize=18, fontweight="bold", va="center")
    fig.text(0.065, 0.855, title, color=NAVY, fontsize=title_size, fontweight=750, va="center")
    fig.text(0.065, 0.805, subtitle, color=SECONDARY, fontsize=10.5, va="center")
    fig.text(0.065, 0.064, FOOTER, color=MUTED, fontsize=6.7, va="center")
    return fig


def rounded_barh(ax, y, width, color, height=0.34, x0=0, zorder=2):
    ax.plot([x0, x0 + width], [y, y], color=color, linewidth=height * 45,
            solid_capstyle="round", zorder=zorder)


def clean_axis(ax, xlim, yticks, labels):
    ax.set_xlim(*xlim)
    ax.set_ylim(-0.65, len(labels) - 0.35)
    ax.set_yticks(yticks, labels, fontsize=10.5, fontweight=650)
    ax.invert_yaxis()
    ax.grid(axis="x", color=BORDER, linewidth=0.7, alpha=0.65)
    ax.tick_params(axis="x", labelbottom=False, length=0)
    ax.tick_params(axis="y", length=0, pad=12)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_facecolor(SURFACE)


def render_barometer(kind, filename, title, color):
    rows = sorted(DATA["barometr_top6"], key=lambda r: r[f"{kind}_active"], reverse=True)
    max_value = max(r[f"{kind}_active"] for r in rows)
    fig = base_figure(
        (8, 6), title,
        "Aktywne oferty w 6 największych miastach akademickich · mediana ceny · zmiana tydzień do tygodnia",
    )
    ax = fig.add_axes([0.16, 0.20, 0.77, 0.54])
    clean_axis(ax, (0, max_value * 1.73), range(len(rows)), [r["name"] for r in rows])
    for y, row in enumerate(rows):
        active = row[f"{kind}_active"]
        median = row[f"{kind}_median"]
        rounded_barh(ax, y, active, color)
        ax.text(active + max_value * 0.035, y,
                f"{pl_int(active)} ofert · mediana {pl_money(median)}",
                fontsize=8.2, color=TEXT, va="center")
        ax.text(max_value * 1.62, y, f"{pl_pct(row[f'{kind}_wow_pct'])} t/t",
                fontsize=8.0, color=TEXT, ha="center", va="center", fontweight=700,
                bbox=dict(boxstyle="round,pad=0.34,rounding_size=0.7", fc=AMBER, ec="none"))
    fig.text(0.065, 0.128, "t/t = tydzień 24–30.08 vs 17–23.08 (snapshoty tygodniowe)",
             fontsize=7.8, color=MUTED)
    fig.savefig(OUT / filename, dpi=200, facecolor=BG)
    plt.close(fig)


def render_supply_comparison():
    rows = DATA["barometr_top6"]
    max_value = max(r["kaw_active"] for r in rows)
    fig = base_figure(
        (8, 6), "Podaż kawalerek w sierpniu rosła, nie topniała",
        "Aktywne kawalerki 20.08 vs 30.08.2026 · 6 największych miast",
    )
    legend = [
        Line2D([0], [0], color=PREVIOUS, lw=7, solid_capstyle="round", label="20.08"),
        Line2D([0], [0], color=BLUE, lw=7, solid_capstyle="round", label="30.08"),
    ]
    fig.legend(handles=legend, loc="upper left", bbox_to_anchor=(0.065, 0.772),
               ncol=2, frameon=False, fontsize=8.2, handlelength=1.4)
    ax = fig.add_axes([0.16, 0.16, 0.77, 0.54])
    clean_axis(ax, (0, max_value * 1.52), range(len(rows)), [r["name"] for r in rows])
    for y, row in enumerate(rows):
        old, new = row["kaw_2008"], row["kaw_active"]
        rounded_barh(ax, y - 0.16, old, PREVIOUS, height=0.22, zorder=2)
        rounded_barh(ax, y + 0.16, new, BLUE, height=0.22, zorder=3)
        ax.text(old + max_value * 0.025, y - 0.16, pl_int(old), fontsize=7.4, color=TEXT, va="center")
        ax.text(new + max_value * 0.025, y + 0.16, pl_int(new), fontsize=7.4, color=TEXT, va="center")
        delta = (new / old - 1) * 100
        ax.text(max_value * 1.43, y, pl_pct(delta), fontsize=8.1, color=TEXT,
                ha="center", va="center", fontweight=700,
                bbox=dict(boxstyle="round,pad=0.34,rounding_size=0.7", fc=AMBER, ec="none"))
    fig.savefig(OUT / "03-kawalerki-20-08-vs-30-08.png", dpi=200, facecolor=BG)
    plt.close(fig)


def render_monthly_index():
    rows = DATA["monthly_top10"]
    fig = base_figure(
        (8, 6), "Indeks Najmu — sierpień 2026: mediany cen ofertowych",
        "10 największych rynków · mediana miesięcznego czynszu · zmiana m/m vs lipiec",
        title_size=14.5,
    )
    marker = Line2D([0], [0], marker="o", markerfacecolor=SURFACE,
                    markeredgecolor=NAVY, markeredgewidth=1.4, linestyle="none",
                    markersize=6, label="czerwiec 2026")
    fig.legend(handles=[marker], loc="upper left", bbox_to_anchor=(0.065, 0.772),
               frameon=False, fontsize=8.2)
    ax = fig.add_axes([0.16, 0.17, 0.77, 0.53])
    clean_axis(ax, (0, 4250), range(len(rows)), [r["name"] for r in rows])
    for y, row in enumerate(rows):
        rounded_barh(ax, y, row["median_aug"], BLUE, height=0.22)
        ax.text(max(row["median_aug"], row["median_jun"]) + 60, y, pl_money(row["median_aug"]),
                fontsize=7.7, color=TEXT, va="center")
        ax.scatter(row["median_jun"], y, s=30, facecolor=SURFACE,
                   edgecolor=NAVY, linewidth=1.3, zorder=5)
        mm = row["mm_pct"]
        label = "bez zmian" if mm == 0 else pl_pct(mm)
        delta_color = MUTED if mm == 0 else GREEN if mm > 0 else RED
        ax.text(4150, y, label, fontsize=8.0, color=delta_color,
                ha="right", va="center", fontweight=700 if mm else 500)
    fig.text(0.065, 0.118,
             f"Ceny ofertowe (nie transakcyjne). Mediana ogólnopolska ważona liczbą ofert: {pl_money(DATA['weighted_median_pl_aug'])}",
             fontsize=7.7, color=MUTED)
    fig.savefig(OUT / "04-indeks-mediany-sierpien-2026.png", dpi=200, facecolor=BG)
    plt.close(fig)


def stat_tile(fig, x, title, active, median, wow, color):
    tile = FancyBboxPatch((x, 0.31), 0.18, 0.35,
                          boxstyle="round,pad=0.012,rounding_size=0.018",
                          transform=fig.transFigure, facecolor=BG,
                          edgecolor=BORDER, linewidth=0.8)
    fig.add_artist(tile)
    fig.text(x + 0.018, 0.615, title, color=color, fontsize=10, fontweight=750)
    fig.text(x + 0.018, 0.505, pl_int(active), color=TEXT, fontsize=24, fontweight=750)
    fig.text(x + 0.018, 0.458, "aktywnych ofert", color=MUTED, fontsize=8.2)
    fig.text(x + 0.018, 0.36, f"mediana {pl_money(median)} · {pl_pct(wow)} t/t",
             color=SECONDARY, fontsize=6.9)


def render_city_cards():
    monthly = {r["slug"]: r for r in DATA["monthly_top10"]}
    for city in DATA["barometr_top6"]:
        fig = base_figure(
            (8, 4.5), f"{city['name']}: rynek najmu na start roku akademickiego",
            "Aktywne oferty na koniec sierpnia 2026",
            title_size=14.5,
        )
        stat_tile(fig, 0.065, "Kawalerki", city["kaw_active"], city["kaw_median"], city["kaw_wow_pct"], BLUE)
        stat_tile(fig, 0.265, "Pokoje", city["pok_active"], city["pok_median"], city["pok_wow_pct"], NAVY)

        ax = fig.add_axes([0.54, 0.32, 0.38, 0.35])
        room_rows = [r for r in DATA["city_detail"][city["slug"]]["by_rooms"] if r["rooms"] <= 3]
        values = [r["median_price"] for r in room_rows]
        max_value = max(values)
        clean_axis(ax, (0, max_value * 1.35), range(3), ["", "", ""])
        ax.set_title("Mediana wg liczby pokoi (sierpień)", loc="left", color=NAVY,
                     fontsize=10, fontweight=750, pad=14)
        for y, (room, value) in enumerate(zip(room_rows, values)):
            room_label = f"{room['rooms']} pokój" if room["rooms"] == 1 else f"{room['rooms']} pokoje"
            ax.text(-0.02, y, room_label, transform=ax.get_yaxis_transform(),
                    ha="right", va="center", fontsize=9.2, color=TEXT,
                    fontweight=650, clip_on=False)
            rounded_barh(ax, y, value, BLUE, height=0.25)
            ax.text(value + max_value * 0.045, y, pl_money(value), fontsize=7.8,
                    color=TEXT, va="center")

        row = monthly.get(city["slug"])
        if row:
            strip = FancyBboxPatch((0.065, 0.205), 0.855, 0.065,
                                   boxstyle="round,pad=0.006,rounding_size=0.012",
                                   transform=fig.transFigure, facecolor="#edf3ff",
                                   edgecolor="none")
            fig.add_artist(strip)
            fig.text(0.085, 0.237,
                     f"Mediana wszystkich ofert: {pl_money(row['median_aug'])} (lipiec: {pl_money(row['median_jul'])})",
                     fontsize=8.4, color=SECONDARY, va="center", fontweight=650)
        fig.savefig(CITY_OUT / f"{city['slug']}.png", dpi=200, facecolor=BG)
        plt.close(fig)


def render_hero():
    source = ROOT / "hero-source.png"
    if not source.exists():
        raise FileNotFoundError("Brak hero-source.png z generatora ilustracji")
    with Image.open(source) as im:
        im = im.convert("RGB")
        target_ratio = 16 / 9
        ratio = im.width / im.height
        if ratio > target_ratio:
            width = round(im.height * target_ratio)
            left = (im.width - width) // 2
            im = im.crop((left, 0, left + width, im.height))
        elif ratio < target_ratio:
            height = round(im.width / target_ratio)
            top = (im.height - height) // 2
            im = im.crop((0, top, im.width, top + height))
        im.resize((1600, 900), Image.Resampling.LANCZOS).save(OUT / "hero-barometr.png")


def main():
    assert len(DATA["barometr_top6"]) == 6
    assert len(DATA["monthly_top10"]) == 10
    render_barometer("kaw", "01-barometr-kawalerki-top6.png", "Kawalerki na wynajem: koniec sierpnia 2026", BLUE)
    render_barometer("pok", "02-barometr-pokoje-top6.png", "Pokoje na wynajem: koniec sierpnia 2026", NAVY)
    render_supply_comparison()
    render_monthly_index()
    render_city_cards()
    render_hero()


if __name__ == "__main__":
    main()
