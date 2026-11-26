"""Shared settings for the project: countries, years, and file paths.

Every script imports from here, so if we change the study window or add a
country, we only change it in one place.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_INTERIM = ROOT / "data" / "interim"
DATA_PROCESSED = ROOT / "data" / "processed"
OUT_TABLES = ROOT / "outputs" / "tables"
OUT_FIGURES = ROOT / "outputs" / "figures"

for _p in (DATA_RAW, DATA_INTERIM, DATA_PROCESSED, OUT_TABLES, OUT_FIGURES):
    _p.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Study countries
# ---------------------------------------------------------------------------
# Each country needs three codes: ISO3 (World Bank), DHS two-letter code,
# and a readable name.
COUNTRIES = {
    "KEN": {"dhs": "KE", "name": "Kenya"},
    "TZA": {"dhs": "TZ", "name": "Tanzania"},
    "UGA": {"dhs": "UG", "name": "Uganda"},
    "RWA": {"dhs": "RW", "name": "Rwanda"},
    "COD": {"dhs": "CD", "name": "DR Congo"},
}
ISO3 = list(COUNTRIES)
DHS_CODES = [c["dhs"] for c in COUNTRIES.values()]
DHS_TO_ISO3 = {c["dhs"]: iso for iso, c in COUNTRIES.items()}

# ---------------------------------------------------------------------------
# Study window
# ---------------------------------------------------------------------------
# VIIRS annual V2.2 starts with a partial 2012 composite, which we exclude.
YEAR_START = 2013
YEAR_END = 2024  # confirm the last year actually available in each source

# Earliest DHS survey year we want (Kenya 2014 is the first planned survey)
DHS_SURVEY_YEAR_START = 2014

# ---------------------------------------------------------------------------
# Indicators
# ---------------------------------------------------------------------------
WB_INDICATORS = {
    "EG.ELC.ACCS.ZS": "access_total",
    "EG.ELC.ACCS.UR.ZS": "access_urban",
    "EG.ELC.ACCS.RU.ZS": "access_rural",
}
DHS_INDICATOR = "HC_ELEC_H_ELC"  # % of households with electricity
