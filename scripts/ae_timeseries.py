"""
A&E 4-hour performance in England: Type 1 vs Type 3 vs all types, monthly time series.

1. Download "Monthly A&E Time Series" (XLS) from
   https://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/
   and put it in data/ (that folder is git-ignored).
2. Run:
       python scripts/ae_timeseries.py data/Monthly-AE-Time-Series-<Month>-2026.xls
       python scripts/ae_timeseries.py data/<file>.xls --start 2015-01-01 -o figures/my_chart.png

The script finds the header row and the 4-hour percentage columns by name,
so it tolerates small layout changes between releases. It prints the
detected columns: check them before posting any number.
"""
import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# Colour-blind friendly palette (validated categorical slots)
COLORS = ["#2a78d6", "#eb6834", "#1baf7a"]
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"


def load(path: Path) -> tuple[pd.DataFrame, str]:
    """Return the data table and the name of its Period column."""
    sheets = pd.read_excel(path, sheet_name=None, header=None)
    for name, raw in sheets.items():
        for i in range(min(40, len(raw))):
            row = raw.iloc[i].astype(str).str.strip().str.lower()
            if (row == "period").any():
                df = raw.iloc[i + 1:].copy()
                df.columns = raw.iloc[i].astype(str).str.strip()
                print(f"Using sheet '{name}', header row {i}")
                period_col = [c for c in df.columns if c.lower() == "period"][0]
                df[period_col] = pd.to_datetime(df[period_col], errors="coerce")
                return df.dropna(subset=[period_col]), period_col
    sys.exit("Could not find a 'Period' header row - open the file and check the layout.")


def find(df: pd.DataFrame, *words: str) -> str | None:
    for c in df.columns:
        lc = c.lower()
        if all(w in lc for w in words):
            return c
    return None


def main(path: Path, start: str, out: Path) -> None:
    df, period_col = load(path)

    cols = {
        "Type 1 (major emergency depts)": find(df, "percentage", "4 hours", "type 1"),
        "Type 3 (UTCs / minor injury units)": find(df, "percentage", "4 hours", "type 3"),
        "All A&E types": find(df, "percentage", "4 hours", "all"),
    }
    print("Detected columns:", cols)
    cols = {k: v for k, v in cols.items() if v}
    if not cols:
        sys.exit("No 4-hour percentage columns found - print(df.columns) and edit find().")

    df = df[df[period_col] >= start].copy()
    for v in cols.values():
        s = pd.to_numeric(df[v], errors="coerce")
        df[v] = s * 100 if s.max() <= 1.5 else s  # proportions -> %

    fig, ax = plt.subplots(figsize=(10, 6.2), dpi=200)
    fig.patch.set_facecolor(SURF)
    ax.set_facecolor(SURF)
    last = df.iloc[-1]
    for (label, col), c in zip(cols.items(), COLORS):
        ax.plot(df[period_col], df[col], color=c, lw=2, label=label)
        ax.text(last[period_col], last[col], f"  {last[col]:.1f}%", color=INK, va="center", fontsize=10)

    ax.axhline(95, color=INK, ls=(0, (5, 4)), lw=1.4)
    ax.text(df[period_col].iloc[0], 96, "95% standard", color=INK, fontsize=10)
    ax.set_ylim(0, 102)
    ax.set_ylabel("Attendances completed within 4 hours (%)", color=INK2)
    ax.yaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=INK2, length=0)
    ax.legend(frameon=False, loc="lower left")

    fig.suptitle("A&E 4-hour performance in England, by department type", x=0.07, ha="left",
                 fontsize=15, fontweight="bold", color=INK)
    fig.text(0.07, 0.02, "Source: NHS England, Monthly A&E Time Series (accredited official statistics, "
             "Open Government Licence v3.0)", fontsize=8.5, color=INK2)
    fig.subplots_adjust(left=0.08, right=0.93, top=0.9, bottom=0.12)

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor=SURF)
    print(f"Saved {out}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("xls", type=Path, help="NHS England Monthly A&E Time Series file (.xls/.xlsx)")
    p.add_argument("--start", default="2019-04-01", help="first month to plot (YYYY-MM-DD)")
    p.add_argument("-o", "--out", type=Path, default=Path("figures/ae_4hour_timeseries.png"))
    a = p.parse_args()
    main(a.xls, a.start, a.out)
