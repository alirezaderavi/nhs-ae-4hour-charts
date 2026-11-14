"""
A&E 4-hour performance in England, July 2025 vs July 2026, by department type.

Figures are typed in from NHS England's "A&E Attendances and Emergency
Admissions - Statistical commentary, July 2026". Check them against the
published commentary before reusing.

Usage:
    python scripts/ae_bar_july2026.py            # writes figures/ae_4hour_july2026.png
    python scripts/ae_bar_july2026.py -o out.png
"""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# --- Data (percent of attendances completed within 4 hours) -----------------
CATS = ["All A&E types", "Type 1\n(major emergency depts)", "Type 3\n(UTCs / minor injury units)"]
JUL25 = [76.4, 63.1, 97.3]
JUL26 = [75.4, 61.7, 96.8]

# --- Style ------------------------------------------------------------------
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
C25, C26 = "#eb6834", "#2a78d6"


def main(out: Path) -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
    fig, ax = plt.subplots(figsize=(10, 6.2), dpi=200)
    fig.patch.set_facecolor(SURF)
    ax.set_facecolor(SURF)

    x = np.arange(len(CATS))
    w = 0.36
    b1 = ax.bar(x - w / 2 - 0.01, JUL25, w, color=C25, label="July 2025", zorder=3)
    b2 = ax.bar(x + w / 2 + 0.01, JUL26, w, color=C26, label="July 2026", zorder=3)
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.2, f"{b.get_height():.1f}%",
                    ha="center", va="bottom", fontsize=10.5, color=INK)

    ax.axhline(95, color=INK, ls=(0, (5, 4)), lw=1.4, zorder=4)
    ax.text(-0.45, 96.5, "95% standard (NHS Constitution)", ha="left", va="bottom", fontsize=10, color=INK)

    ax.set_xticks(x, CATS, color=INK)
    ax.set_ylim(0, 108)
    ax.set_yticks(range(0, 101, 20))
    ax.set_ylabel("Attendances completed within 4 hours (%)", color=INK2)
    ax.yaxis.grid(True, color=GRID, lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(INK2)
    ax.tick_params(colors=INK2, length=0)
    ax.legend(frameon=False, loc="lower right", ncol=2, bbox_to_anchor=(1, 1.0))

    fig.suptitle("Major A&Es in England are furthest from the 4-hour standard", x=0.07, ha="left",
                 fontsize=15, fontweight="bold", color=INK, y=0.97)
    ax.set_title("Share of A&E attendances admitted, transferred or discharged within 4 hours, by department type",
                 loc="left", fontsize=10.5, color=INK2, pad=24)
    fig.text(0.07, 0.02,
             "Source: NHS England, A&E Attendances and Emergency Admissions - Statistical commentary, July 2026\n"
             "(accredited official statistics, Open Government Licence v3.0). Chart: Alireza",
             fontsize=8.5, color=INK2, ha="left")
    fig.subplots_adjust(left=0.07, right=0.98, top=0.82, bottom=0.19)

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor=SURF)
    print(f"Saved {out}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-o", "--out", type=Path, default=Path("figures/ae_4hour_july2026.png"))
    main(p.parse_args().out)
