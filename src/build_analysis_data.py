"""Join light measures to DHS regional access and World Bank national access.

Inputs:
    data/light/light_measures.csv        from notebooks/01_light_measures.ipynb
    data/raw/dhs_electricity_all.csv     from src/download_dhs.py
    data/raw/worldbank_access.csv        from src/download_worldbank.py

Outputs:
    data/processed/region_survey.csv     one row per DHS region and survey (analysis sample)
    data/processed/national_panel.csv    one row per country and year

Matching rules:
  * Each DHS regional estimate is matched to the region outline with the same
    DHS region ID. The DR Congo 2013-14 province file has no IDs, so those 26
    provinces are matched by name.
  * The light year is the first calendar year of survey fieldwork
    (a survey labelled 2015-16 uses 2015 light).
  * Analysis sample: the finest geography DHS publishes for each survey, so
    each place appears once per survey.

Run from the project folder:
    python src/build_analysis_data.py
"""

import re
import unicodedata

import pandas as pd

from config import DATA_PROCESSED, DATA_RAW, ROOT

LIGHT = ROOT / "data" / "light" / "light_measures.csv"

# Survey -> boundary layer used in the analysis (finest level DHS publishes)
ANALYSIS_LAYERS = {
    "KE2014DHS": "sdr_subnational_boundaries",    # 8 former provinces (counties need microdata)
    "KE2022DHS": "sdr_subnational_boundaries",    # 47 counties
    "TZ2015DHS": "sdr_subnational_boundaries2",   # 30 regions
    "TZ2022DHS": "sdr_subnational_boundaries2",   # 31 regions
    "UG2016DHS": "sdr_subnational_boundaries",    # 15 sub-regions
    "UG2024MIS": "sdr_subnational_boundaries",    # 15 sub-regions
    "RW2015DHS": "sdr_subnational_boundaries",    # 5 provinces
    "RW2019DHS": "sdr_subnational_boundaries",    # 5 provinces
    "CD2013DHS": "sdr_subnational_boundaries2",   # 26 provinces (post-2015 borders)
    "CD2023DHS": "sdr_subnational_boundaries",    # 26 provinces
}

LIGHT_COLS = ["mean_rad", "log_rad", "lit_land_share", "lit_pop_share",
              "lit_land_share_eog", "lit_pop_share_eog", "pop_per_pixel",
              "cf_cvg_mean", "low_cvg_share"]

# DHS spellings that differ from the boundary file (after normalising)
SPLIT_OLD_PROVINCES = {"Bandundu", "Equateur", "Orientale", "Katanga", "Kasai Oriental", "Kasai Occident"}

NAME_FIXES = {"bas-congo": "kongo central", "haut-lomani": "haut-lomami", "lomani": "lomami", "tanganyka": "tanganyika",
              "equateur (>= 2015)": "equateur", "kasai-oriental (>= 2015)": "kasai-oriental"}


def norm(name: str) -> str:
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    s = s.lower().strip().lstrip(".").strip()
    s = re.sub(r"\s+", " ", s)
    return NAME_FIXES.get(s, s)


def regional() -> pd.DataFrame:
    light = pd.read_csv(LIGHT)
    dhs = pd.read_csv(DATA_RAW / "dhs_electricity_all.csv")
    dhs = dhs[(dhs["CharacteristicCategory"] == "Region") & dhs["SurveyId"].isin(ANALYSIS_LAYERS)].copy()
    dhs["light_year"] = dhs["SurveyYearLabel"].astype(str).str[:4].astype(int)

    frames = []
    for survey, layer in ANALYSIS_LAYERS.items():
        lt = light[(light["survey"] == survey) & (light["layer"] == layer)].copy()
        dh = dhs[dhs["SurveyId"] == survey]
        year = int(dh["light_year"].iloc[0])
        lt = lt[lt["year"] == year]

        if survey == "CD2013DHS":
            # DHS lists the six pre-2015 provinces that were split alongside their
            # successors; keep only the 26 current provinces.
            dh = dh[~dh["CharacteristicLabel"].isin(SPLIT_OLD_PROVINCES)]
            lt["key"] = lt["REGNAME"].map(norm)
            dh = dh.assign(key=dh["CharacteristicLabel"].map(norm))
        else:
            lt["key"] = lt["REG_ID"].astype(str)
            dh = dh.assign(key=dh["RegionId"].astype(str))

        # Nairobi is listed twice (as province and county) with identical values
        dh = dh.drop_duplicates(subset=["key", "Value"])
        assert dh["key"].is_unique, f"{survey}: conflicting duplicate DHS rows"
        m = lt.merge(
            dh[["key", "SurveyYearLabel", "SurveyType", "CharacteristicLabel", "Value",
                "DenominatorUnweighted", "DenominatorWeighted"]],
            on="key", how="inner")
        if len(m) != len(lt):
            missing = sorted(set(lt["REGNAME"]) - set(m["REGNAME"]))
            raise RuntimeError(f"{survey}: {len(lt) - len(m)} regions did not match DHS: {missing}")
        frames.append(m)
        print(f"{survey}: {len(m)} regions matched (light year {year})")

    out = pd.concat(frames, ignore_index=True).rename(columns={
        "Value": "dhs_access_pct", "DenominatorUnweighted": "dhs_n_households",
        "DenominatorWeighted": "dhs_n_households_weighted", "year": "light_year",
        "CharacteristicLabel": "dhs_region_label"})
    out["dhs_access"] = out["dhs_access_pct"] / 100
    keep = ["iso3", "survey", "SurveyType", "SurveyYearLabel", "light_year", "uid", "REG_ID",
            "REGNAME", "dhs_region_label", "dhs_access_pct", "dhs_access", "dhs_n_households",
            "dhs_n_households_weighted"] + LIGHT_COLS
    return out[keep].sort_values(["iso3", "survey", "REGNAME"])


def national() -> pd.DataFrame:
    light = pd.read_csv(LIGHT)
    nat = light[light["layer"] == "national"][["iso3", "year"] + LIGHT_COLS]
    wb = pd.read_csv(DATA_RAW / "worldbank_access.csv")[["iso3", "year", "access_total", "access_urban", "access_rural"]]
    out = nat.merge(wb, on=["iso3", "year"], how="left")
    for c in ["access_total", "access_urban", "access_rural"]:
        out[c.replace("access", "wb_access")] = out.pop(c) / 100
    return out.sort_values(["iso3", "year"])


def main() -> None:
    reg = regional()
    reg.to_csv(DATA_PROCESSED / "region_survey.csv", index=False)
    print(f"\nregion_survey.csv: {len(reg)} region-survey rows, "
          f"{reg['uid'].nunique()} region outlines, {reg['iso3'].nunique()} countries")

    nat = national()
    nat.to_csv(DATA_PROCESSED / "national_panel.csv", index=False)
    print(f"national_panel.csv: {len(nat)} country-years "
          f"({nat['wb_access_total'].notna().sum()} with World Bank access)")


if __name__ == "__main__":
    main()
