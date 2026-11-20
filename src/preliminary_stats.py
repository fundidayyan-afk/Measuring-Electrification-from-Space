"""Preliminary numbers for the proposal's 'Preliminary data work' paragraph.

Needs the two raw files from download_worldbank.py and download_dhs.py.
Prints, and saves to outputs/tables/preliminary_stats.md:
  1. Country-years with World Bank access data
  2. DHS surveys and number of regions at each geographic level
  3. Correlation between DHS national access and World Bank access in
     survey years (the proposal promises this number)

Run from the project folder:
    python src/preliminary_stats.py
"""

import pandas as pd

from config import DATA_RAW, OUT_TABLES


def main() -> None:
    wb = pd.read_csv(DATA_RAW / "worldbank_access.csv")
    dhs = pd.read_csv(DATA_RAW / "dhs_electricity_all.csv")
    surveys = pd.read_csv(DATA_RAW / "dhs_surveys.csv")

    lines = ["# Preliminary data summary", ""]

    # 1. World Bank coverage
    wb_ok = wb.dropna(subset=["access_total"])
    lines += [
        "## World Bank national series",
        f"- Country-years with total access: {len(wb_ok)}",
        f"- Years covered: {wb_ok['year'].min()} to {wb_ok['year'].max()}",
        "",
    ]

    # 2. DHS coverage
    lines += ["## DHS surveys and regional units", "",
              surveys.to_markdown(index=False), ""]

    # 3. DHS national vs World Bank in matching years.
    # A DHS survey labelled '2015-16' is matched to its first year; we will
    # revisit this choice (fieldwork months) in the cleaning step.
    # Standard DHS surveys only; Malaria Indicator Surveys (MIS) and others are
    # listed in the survey table above but kept out of this comparison.
    nat = dhs[(dhs["CharacteristicCategory"] == "Total") & (dhs["SurveyType"] == "DHS")].copy()
    nat["year"] = nat["SurveyYearLabel"].astype(str).str[:4].astype(int)
    nat = nat[["iso3", "SurveyYearLabel", "year", "Value"]].rename(columns={"Value": "dhs_access"})
    merged = nat.merge(wb[["iso3", "year", "access_total"]], on=["iso3", "year"], how="left")
    merged["gap_pp"] = merged["dhs_access"] - merged["access_total"]

    corr = merged[["dhs_access", "access_total"]].corr().iloc[0, 1]
    lines += [
        "## DHS national vs World Bank, survey years",
        "",
        merged.to_markdown(index=False, floatfmt=".1f"),
        "",
        f"- Correlation: {corr:.3f} (n = {merged['access_total'].notna().sum()})",
        f"- Mean gap (DHS minus World Bank): {merged['gap_pp'].mean():.1f} percentage points",
        "",
        "Note: DHS measures households and the World Bank measures population, "
        "so a small gap is expected even when both are correct.",
    ]

    text = "\n".join(lines)
    out = OUT_TABLES / "preliminary_stats.md"
    out.write_text(text)
    print(text)
    print(f"\nSaved to {out}")


if __name__ == "__main__":
    main()
