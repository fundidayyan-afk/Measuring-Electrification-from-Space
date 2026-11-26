"""Model 3 (first pass): when a region's light rises, does its access rise too?

For every region observed in two survey waves:
    d_access_r = b * d_light_r + country_c + e_r
where d_ is the change between waves in percentage points. Differencing removes
everything fixed about a region (cities, mines, ports, terrain); country effects
absorb different time gaps and national trends. Inference: wild cluster
bootstrap with Webb weights, five country clusters (functions from Model 1).

Fixed boundaries: each region keeps its first-wave outline, and light is
measured inside that same outline in both years.
  * Kenya: 8 former provinces (counties need the 2014 microdata).
  * Tanzania: 30 regions; the 2022 Mbeya and Songwe estimates are combined,
    weighted by DHS household counts, to match the 2015 Mbeya.
  * Uganda: 15 sub-regions, 2016 DHS vs 2024-25 MIS.
  * Rwanda: 5 provinces. DR Congo: 26 provinces.

Survey standard errors are not yet available, so the model is unweighted.

Outputs:
    data/processed/long_differences.csv
    outputs/tables/model3_long_differences.md
"""

import re
import unicodedata

import numpy as np
import pandas as pd

from config import DATA_PROCESSED, DATA_RAW, OUT_TABLES, ROOT
from model1_national import cluster_se, ols, wild_cluster_p

PAIRS = [  # (first wave, second wave, first-wave boundary layer)
    ("KE2014DHS", "KE2022DHS", "sdr_subnational_boundaries"),
    ("TZ2015DHS", "TZ2022DHS", "sdr_subnational_boundaries2"),
    ("UG2016DHS", "UG2024MIS", "sdr_subnational_boundaries"),
    ("RW2015DHS", "RW2019DHS", "sdr_subnational_boundaries"),
    ("CD2013DHS", "CD2023DHS", "sdr_subnational_boundaries2"),
]
# boundary-file name -> DHS label, where they differ (after normalising)
ALIASES = {"central 1": "south buganda", "central 2": "north buganda", "bugishu": "bugisu/elgon",
           "mbeya (before 2016)": "mbeya", "mbeya (since 2016)": "mbeya", "bas-congo": "kongo central",
           "kigali city": "kigali", "equateur (>= 2015)": "equateur", "kasai-oriental (>= 2015)": "kasai-oriental", "haut-lomani": "haut-lomami", "lomani": "lomami", "tanganyka": "tanganyika"}
MEASURES = {"lit_pop_share_eog": "People in lit pixels (EOG mask)",
            "lit_pop_share": "People in lit pixels (our threshold)",
            "log_rad": "Log brightness"}
SPLIT_OLD_DRC = {"bandundu", "equateur", "orientale", "katanga", "kasai oriental", "kasai occident"}


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower().strip()
    s = re.sub(r"\s+", " ", s.lstrip(".").strip())
    return ALIASES.get(s, s)


def dhs_by_name(dhs, survey):
    """DHS regional values for one survey, keyed by normalised name (finest level wins)."""
    d = dhs[(dhs.SurveyId == survey) & (dhs.CharacteristicCategory == "Region")].copy()
    d["depth"] = d["CharacteristicLabel"].str.len() - d["CharacteristicLabel"].str.lstrip(".").str.len()
    d["key"] = d["CharacteristicLabel"].map(norm)
    if survey.startswith("CD"):
        d = d[~((d.depth == 0) & d.key.isin(SPLIT_OLD_DRC))]
    if survey == "TZ2022DHS":   # combine Mbeya (since 2016) and Songwe into the 2015 Mbeya
        m = d[d.key.isin(["mbeya", "songwe"]) & (d.depth > 0)]
        val = np.average(m["Value"], weights=m["DenominatorWeighted"])
        d = d[~d.key.isin(["mbeya", "songwe"])]
        d = pd.concat([d, pd.DataFrame([{"key": "mbeya", "Value": val, "depth": 2}])])
    d = d.sort_values("depth", ascending=False).drop_duplicates("key")
    return d.set_index("key")["Value"]


def build():
    light = pd.read_csv(ROOT / "data" / "light" / "light_measures.csv")
    dhs = pd.read_csv(DATA_RAW / "dhs_electricity_all.csv")
    rows = []
    for s1, s2, layer in PAIRS:
        y1 = int(dhs.loc[dhs.SurveyId == s1, "SurveyYearLabel"].astype(str).str[:4].iloc[0])
        y2 = int(dhs.loc[dhs.SurveyId == s2, "SurveyYearLabel"].astype(str).str[:4].iloc[0])
        lt = light[(light.survey == s1) & (light.layer == layer)].copy()
        lt["key"] = lt["REGNAME"].map(norm)
        v1, v2 = dhs_by_name(dhs, s1), dhs_by_name(dhs, s2)
        l1 = lt[lt.year == y1].set_index("key")
        l2 = lt[lt.year == y2].set_index("key")
        missing = [k for k in l1.index if k not in v1.index or k not in v2.index]
        if missing:
            raise RuntimeError(f"{s1}->{s2}: no DHS match for {missing}")
        for k in l1.index:
            r = {"iso3": l1.loc[k, "iso3"], "region": l1.loc[k, "REGNAME"], "wave1": s1, "wave2": s2,
                 "year1": y1, "year2": y2, "access1": v1[k], "access2": v2[k],
                 "d_access_pp": v2[k] - v1[k]}
            for m in MEASURES:
                scale = 1 if m == "log_rad" else 100
                r[f"{m}_1"], r[f"{m}_2"] = l1.loc[k, m], l2.loc[k, m]
                r[f"d_{m}"] = (l2.loc[k, m] - l1.loc[k, m]) * scale
            rows.append(r)
        print(f"{s1} -> {s2}: {len(l1)} regions, light years {y1} and {y2}")
    return pd.DataFrame(rows)


def main():
    ld = build()
    ld.to_csv(DATA_PROCESSED / "long_differences.csv", index=False)
    rng = np.random.default_rng(20261126)
    out = []
    for m, label in MEASURES.items():
        for fe in (True, False):
            y = ld["d_access_pp"].to_numpy()
            cols = [ld[f"d_{m}"].to_numpy()]
            cols += list(pd.get_dummies(ld["iso3"], dtype=float).to_numpy().T) if fe else [np.ones(len(ld))]
            X = np.column_stack(cols)
            g = ld["iso3"].astype("category").cat.codes.to_numpy()
            beta, resid = ols(y, X)
            p, _ = wild_cluster_p(y, X, g, rng)
            out.append({"Light measure": label, "Country effects": "yes" if fe else "no",
                        "Coefficient": beta[0], "Cluster s.e.": cluster_se(X, resid, g),
                        "Wild bootstrap p": p,
                        "Corr. of changes": np.corrcoef(ld[f"d_{m}"], y)[0, 1], "Regions": len(ld)})
    res = pd.DataFrame(out)
    by_c = ld.groupby("iso3").apply(lambda d: pd.Series({
        "Regions": len(d), "Mean change in access (pp)": d.d_access_pp.mean(),
        "Mean change in lit people, EOG (pp)": d.d_lit_pop_share_eog.mean(),
        "Corr. of changes": np.corrcoef(d.d_lit_pop_share_eog, d.d_access_pp)[0, 1] if len(d) > 2 else np.nan}),
        include_groups=False)
    text = ["# Model 3 (first pass): long differences", "",
            "Change in DHS household access between survey waves on change in light, same boundaries in both years.", "",
            res.to_markdown(index=False, floatfmt=".3f"), "",
            "Coefficient: percentage points of access per 1-point rise in the light share (per 1 log unit for brightness). "
            "Wild cluster bootstrap with Webb weights, 9,999 draws, 5 country clusters.", "",
            "## By country", "", by_c.to_markdown(floatfmt=".2f"), ""]
    (OUT_TABLES / "model3_long_differences.md").write_text("\n".join(text))
    print("\n".join(text))


if __name__ == "__main__":
    main()
