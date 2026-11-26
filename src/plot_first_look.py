"""First look: DHS household access vs. share of people in lit pixels, by region.

Output: outputs/figures/first_look_access_vs_light.png
"""

import matplotlib.pyplot as plt
import pandas as pd

from config import DATA_PROCESSED, OUT_FIGURES

COUNTRIES = [  # fixed order: color and marker follow the country, never its rank
    ("KEN", "Kenya", "#257de0", "o"),
    ("TZA", "Tanzania", "#f47230", "s"),
    ("UGA", "Uganda", "#00b894", "^"),
    ("RWA", "Rwanda", "#f2a600", "D"),
    ("COD", "DR Congo", "#ee7fac", "v"),
]
LABEL = {("CD2023DHS", "Kongo Central"), ("KE2022DHS", "Mandera"), ("TZ2022DHS", "Kaskazini Unguja"),
         ("UG2024MIS", "Kigezi"), ("UG2016DHS", "Bunyoro"), ("CD2023DHS", "Kinshasa"), ("KE2022DHS", "Nairobi")}

r = pd.read_csv(DATA_PROCESSED / "region_survey.csv")
fig, ax = plt.subplots(figsize=(7.5, 7))
ax.plot([0, 1], [0, 1], color="#9c9c9c", lw=1, ls=(0, (4, 3)), zorder=1, label="Lights equal survey")
for iso, name, color, marker in COUNTRIES:
    g = r[r.iso3 == iso]
    ax.scatter(g.dhs_access, g.lit_pop_share_eog, s=46, c=color, marker=marker, edgecolors="white",
               linewidths=1.2, label=f"{name} ({len(g)})", zorder=3)
for _, row in r.iterrows():
    if (row.survey, row.REGNAME) in LABEL:
        ax.annotate(f"{row.REGNAME} {row.SurveyYearLabel}", (row.dhs_access, row.lit_pop_share_eog),
                    xytext=(6, -3), textcoords="offset points", fontsize=8, color="#3d3d3d")
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
for s in ["left", "bottom"]:
    ax.spines[s].set_color("#c8c8c8")
ax.tick_params(colors="#6b6b6b", labelsize=9)
ax.grid(color="#ececec", lw=0.8)
ax.set_axisbelow(True)
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
ax.set_xlabel("Households with electricity (DHS survey)", color="#3d3d3d")
ax.set_ylabel("People living in lit pixels (VIIRS, EOG mask)", color="#3d3d3d")
ax.set_title("Nighttime lights track survey access, but miss in both directions\n208 region-surveys, 2013–2024",
             loc="left", fontsize=12, color="#1f1f1f")
ax.legend(frameon=False, loc="upper left", fontsize=9, title="Country (region-surveys)", title_fontsize=9)
fig.savefig(OUT_FIGURES / "first_look_access_vs_light.png", dpi=170, bbox_inches="tight")
print("saved")
