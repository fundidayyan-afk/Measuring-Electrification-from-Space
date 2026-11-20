"""Download DHS household electricity estimates (national, urban/rural, regional).

Source: The DHS Program API (same numbers as STATcompiler, no key needed for
light use). Indicator HC_ELEC_H_ELC = % of households with electricity.

Outputs:
    data/raw/dhs_electricity_all.csv   every row the API returns (untouched)
    data/raw/dhs_surveys.csv           one row per survey, with the level of
                                       geography and whether CIs exist

Run from the project folder:
    python src/download_dhs.py

Why keep the untouched file: DHS reports some surveys at more than one
geographic level (for example Kenya by former province and by county). We
keep everything here and choose the reporting level in the cleaning step, so
that choice is visible in the code rather than hidden in the download.
"""

from datetime import date

import pandas as pd
import requests

from config import DATA_RAW, DHS_CODES, DHS_INDICATOR, DHS_SURVEY_YEAR_START, DHS_TO_ISO3

API = "https://api.dhsprogram.com/rest/dhs/data"

FIELDS = [
    "CountryName", "DHS_CountryCode", "SurveyId", "SurveyYear", "SurveyYearLabel",
    "SurveyType", "IndicatorId", "Indicator", "CharacteristicCategory",
    "CharacteristicLabel", "ByVariableLabel", "RegionId", "IsPreferred",
    "Value", "CILow", "CIHigh", "DenominatorUnweighted", "DenominatorWeighted",
    "Precision",
]


def fetch_all() -> pd.DataFrame:
    """Page through the API and return every record as one table."""
    params = {
        "countryIds": ",".join(DHS_CODES),
        "indicatorIds": DHS_INDICATOR,
        "surveyYearStart": DHS_SURVEY_YEAR_START,
        "breakdown": "all",          # national + residence + subnational
        "returnFields": ",".join(FIELDS),
        "perpage": 1000,
        "f": "json",
    }
    records, page, total_pages = [], 1, 1
    while page <= total_pages:
        resp = requests.get(API, params={**params, "page": page}, timeout=60)
        resp.raise_for_status()
        payload = resp.json()
        records.extend(payload.get("Data", []))
        total_pages = payload.get("TotalPages", 1)
        page += 1
    return pd.DataFrame.from_records(records)


def summarise_surveys(df: pd.DataFrame) -> pd.DataFrame:
    """One row per survey and geography level, so we can see what we have."""
    sub = df[~df["CharacteristicCategory"].isin(["Total", "Residence"])]
    ci_present = sub["CILow"].notna() & (sub["CILow"].astype(str).str.strip() != "")
    sub = sub.assign(has_ci=ci_present)
    return (
        sub.groupby(["iso3", "SurveyId", "SurveyType", "SurveyYearLabel", "CharacteristicCategory"])
        .agg(n_units=("CharacteristicLabel", "nunique"),
             share_with_ci=("has_ci", "mean"),
             min_value=("Value", "min"),
             max_value=("Value", "max"))
        .reset_index()
        .sort_values(["iso3", "SurveyYearLabel", "n_units"])
    )


def main() -> None:
    df = fetch_all()
    if df.empty:
        raise RuntimeError("The DHS API returned no rows. Check the indicator ID and country codes.")

    df["iso3"] = df["DHS_CountryCode"].map(DHS_TO_ISO3)
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    df["downloaded"] = date.today().isoformat()

    out_all = DATA_RAW / "dhs_electricity_all.csv"
    df.to_csv(out_all, index=False)

    surveys = summarise_surveys(df)
    out_sum = DATA_RAW / "dhs_surveys.csv"
    surveys.to_csv(out_sum, index=False)

    print(f"Saved {len(df)} rows to {out_all}")
    print(f"Saved survey summary to {out_sum}\n")
    with pd.option_context("display.width", 140, "display.max_rows", 100):
        print(surveys.to_string(index=False))

    if surveys["share_with_ci"].max() == 0:
        print(
            "\nNOTE: no confidence intervals came back for this indicator. "
            "We will need to compute standard errors another way "
            "(see docs/analysis_plan.md, 'Survey uncertainty')."
        )


if __name__ == "__main__":
    main()
