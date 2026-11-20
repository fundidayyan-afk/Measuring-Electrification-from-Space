# Data inventory

Fill in one row each time a dataset is downloaded. The paper's data section cites these exact versions.

| Dataset | Version / ID | Years | Downloaded | Script | Notes |
|---|---|---|---|---|---|
| World Bank access to electricity | EG.ELC.ACCS.ZS, .UR.ZS, .RU.ZS | 2013 onward | | `src/download_worldbank.py` | Partly modeled between surveys |
| DHS household electricity | HC_ELEC_H_ELC | surveys 2014 onward | | `src/download_dhs.py` | Check which geographic level each survey reports |
| DHS region boundaries | Spatial Data Repository | per survey | | manual (spatialdata.dhsprogram.com) | One shapefile per survey |
| VIIRS annual nighttime lights | NOAA/VIIRS/DNB/ANNUAL_V22 | 2013 onward | | `gee/` | Earth Engine catalog listed through 2023 when checked Nov 2026; 2024 may need EOG direct download |
| WorldPop population | WorldPop/GP/100m/R2025A/v1/pop | 2015 onward | | `gee/` | Constrained; 2013-2014 need the older unconstrained series or 2015 as a stand-in |
| Falchetta et al. (2019) | gridded electrification | 2014-2019 | | manual | Comparison only |
