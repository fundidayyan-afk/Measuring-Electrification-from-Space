"""Download World Bank electricity access series for the four study countries.

Source: World Bank World Development Indicators API (no key needed).
Output: data/raw/worldbank_access.csv  (one row per country-year)

Run from the project folder:
    python src/download_worldbank.py
"""

from datetime import date

import pandas as pd
import requests

from config import DATA_RAW, ISO3, WB_INDICATORS, YEAR_END, YEAR_START

API = "https://api.worldbank.org/v2/country/{countries}/indicator/{indicator}"


def fetch_indicator(indicator: str) -> pd.DataFrame:
    """Return a long table (iso3, year, value) for one WDI indicator."""
    url = API.format(countries=";".join(ISO3), indicator=indicator)
    params = {
        "format": "json",
        "date": f"{YEAR_START}:{YEAR_END}",
        "per_page": 1000,
    }
    resp = requests.get(url, params=params, timeout=60)
    resp.raise_for_status()
    payload = resp.json()

    # The API returns [metadata, records]. If records is missing, the
    # indicator code or date range was rejected.
    if len(payload) < 2 or payload[1] is None:
        raise RuntimeError(f"No data returned for {indicator}: {payload[0]}")

    rows = [
        {
            "iso3": rec["countryiso3code"],
            "country": rec["country"]["value"],
            "year": int(rec["date"]),
            "value": rec["value"],
        }
        for rec in payload[1]
    ]
    return pd.DataFrame(rows)


def main() -> None:
    frames = []
    for code, short_name in WB_INDICATORS.items():
        df = fetch_indicator(code).rename(columns={"value": short_name})
        frames.append(df.set_index(["iso3", "country", "year"]))
        print(f"  pulled {code} ({short_name}): {df[short_name].notna().sum()} non-missing values")

    wide = pd.concat(frames, axis=1).reset_index().sort_values(["iso3", "year"])

    # Record when and what we downloaded, so the paper can cite it exactly.
    wide["source"] = "World Bank WDI API"
    wide["downloaded"] = date.today().isoformat()

    out = DATA_RAW / "worldbank_access.csv"
    wide.to_csv(out, index=False)

    last_year = wide.dropna(subset=["access_total"]).groupby("iso3")["year"].max()
    print(f"\nSaved {len(wide)} country-years to {out}")
    print("Latest year with a total-access value, by country:")
    print(last_year.to_string())


if __name__ == "__main__":
    main()
