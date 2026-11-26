"""Figures for the first-pass models.

outputs/figures/national_trends.png   World Bank access vs. share of people in lit pixels
outputs/figures/loco_bias.png         Leave-one-country-out prediction bias
"""

import matplotlib.pyplot as plt
import pandas as pd

from config import DATA_PROCESSED, OUT_FIGURES, OUT_TABLES

NAMES = {"COD": "DR Congo", "KEN": "Kenya", "RWA": "Rwanda", "TZA": "Tanzania", "UGA": "Uganda"}
SERIES = [("wb_access_total", "World Bank: population with access", "#257de0", "-"),
          ("lit_pop_share_eog", "Lights: people in lit pixels (EOG mask)", "#f47230", "--"),
          ("lit_pop_share", "Lights: people in lit pixels (our threshold)", "#00b894", ":")]
INK, INK2, GRID = "#1f1f1f", "#6b6b6b", "#ececec"


def style(ax):
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_color("#c8c8c8")
    ax.tick_params(colors=INK2, labelsize=8.5)
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)


def national():
    n = pd.read_csv(DATA_PROCESSED / "national_panel.csv")
    fig, axes = plt.subplots(1, 5, figsize=(13, 3.6), sharey=True)
    for ax, iso in zip(axes, ["KEN", "TZA", "RWA", "UGA", "COD"]):
        g = n[n.iso3 == iso]
        for col, label, color, ls in SERIES:
            ax.plot(g.year, g[col], color=color, lw=2, ls=ls, label=label)
        ax.set_title(NAMES[iso], loc="left", fontsize=10.5, color=INK)
        ax.set_ylim(0, 0.85)
        ax.set_xticks([2013, 2019, 2025])
        ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
        style(ax)
    fig.suptitle("Lights rise with access in four countries but barely move in DR Congo; the level depends on how 'lit' is defined",
                 x=0.01, ha="left", fontsize=12, color=INK, y=1.04)
    axes[0].legend(frameon=False, fontsize=8.5, loc="upper left", bbox_to_anchor=(0, -0.13), ncol=3)
    fig.savefig(OUT_FIGURES / "national_trends.png", dpi=170, bbox_inches="tight")


def loco():
    b = pd.read_csv(OUT_TABLES / "model2_loco.csv")
    keep = {"People in lit pixels (EOG mask)": ("#f47230", "o"), "People in lit pixels (our threshold)": ("#00b894", "s")}
    order = ["KEN", "TZA", "RWA", "UGA", "COD"]
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    ax.axvline(0, color="#9c9c9c", lw=1)
    for i, (measure, (color, marker)) in enumerate(keep.items()):
        g = b[b["Light measure"] == measure].set_index("Held-out country").loc[order]
        y = [k + (i - 0.5) * 0.22 for k in range(len(order))]
        ax.scatter(g["Mean bias (pp)"], y, s=70, c=color, marker=marker, edgecolors="white", lw=1.2,
                   label=measure, zorder=3)
        for yy, v in zip(y, g["Mean bias (pp)"]):
            ax.annotate(f"{v:+.0f}", (v, yy), xytext=(8 if v >= 0 else -8, -3), textcoords="offset points",
                        ha="left" if v >= 0 else "right", fontsize=8, color=INK2)
    ax.set_yticks(range(len(order)), [NAMES[c] for c in order], color=INK)
    ax.invert_yaxis()
    ax.set_xlim(-25, 25)
    ax.set_xlabel("Average error when the country is left out (prediction minus survey, percentage points)",
                  color=INK2, fontsize=9)
    ax.set_title("Predicting a country with no survey: lights overstate DR Congo and understate Kenya,\n"
                 "Rwanda and Uganda", loc="left", fontsize=11.5, color=INK)
    style(ax)
    ax.grid(axis="y", visible=False)
    ax.legend(frameon=False, fontsize=8.5, loc="lower left", bbox_to_anchor=(0, -0.3), ncol=2)
    fig.savefig(OUT_FIGURES / "loco_bias.png", dpi=170, bbox_inches="tight")


if __name__ == "__main__":
    national()
    loco()
    print("saved")
