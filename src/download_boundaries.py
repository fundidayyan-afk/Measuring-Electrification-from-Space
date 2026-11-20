"""Download DHS subnational boundaries for every survey in the study.

Source: DHS Spatial Data Repository (public; no data request needed).
The repository runs an ArcGIS geoprocessing service: we submit a job for a
survey, wait for it to finish, then ask the job where its zip file is.

Outputs:
    data/boundaries/<SurveyId>_<layer>.geojson   one file per boundary level
    data/boundaries/boundary_summary.csv          what each file contains

Run from the project folder:
    python src/download_boundaries.py
"""

import io
import time
import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd
import requests

from config import ROOT

SURVEYS = [
    "KE2014DHS", "KE2022DHS",
    "TZ2015DHS", "TZ2022DHS",
    "UG2016DHS", "UG2024MIS",
    "RW2015DHS", "RW2019DHS",
]

DHS_API = "https://api.dhsprogram.com/rest/dhs/surveys"
GP = ("https://gis.dhsprogram.com/arcgis/rest/services/Tools/"
      "DownloadSubnationalData/GPServer/downloadSubNationalBoundaries")

OUT = ROOT / "data" / "boundaries"
OUT.mkdir(parents=True, exist_ok=True)


def survey_numbers(ids: list[str]) -> dict[str, int]:
    """Map SurveyId (KE2014DHS) to the numeric SurveyNum the GIS service wants."""
    r = requests.get(DHS_API, params={"surveyIds": ",".join(ids), "f": "json"}, timeout=60)
    r.raise_for_status()
    return {s["SurveyId"]: int(s["SurveyNum"]) for s in r.json()["Data"]}


def run_job(survey_num: int, max_wait: int = 300) -> bytes:
    """Submit a boundary job, wait for it, and return the zip file's bytes."""
    r = requests.get(f"{GP}/submitJob",
                     params={"survey_ids": survey_num, "spatial_format": "shp", "f": "json"},
                     timeout=60)
    r.raise_for_status()
    job_id = r.json()["jobId"]

    waited = 0
    while True:
        status = requests.get(f"{GP}/jobs/{job_id}", params={"f": "json"}, timeout=60).json()
        state = status.get("jobStatus")
        if state == "esriJobSucceeded":
            break
        if state in ("esriJobFailed", "esriJobCancelled", "esriJobTimedOut") or waited > max_wait:
            raise RuntimeError(f"job {job_id} ended as {state}: {status.get('messages')}")
        time.sleep(5)
        waited += 5

    # The finished job lists its outputs; the zip is the one with a URL.
    for param in status.get("results", {}):
        res = requests.get(f"{GP}/jobs/{job_id}/results/{param}", params={"f": "json"}, timeout=60).json()
        value = res.get("value")
        url = value.get("url") if isinstance(value, dict) else value
        if isinstance(url, str) and url.endswith(".zip"):
            z = requests.get(url, timeout=300)
            z.raise_for_status()
            return z.content
    raise RuntimeError(f"job {job_id} finished but no zip was listed: {status}")


def save_layers(survey_id: str, zip_bytes: bytes) -> list[dict]:
    """Read every shapefile in the zip and save it as GeoJSON."""
    rows = []
    tmp = OUT / f"_tmp_{survey_id}"
    tmp.mkdir(exist_ok=True)
    zipfile.ZipFile(io.BytesIO(zip_bytes)).extractall(tmp)
    for shp in sorted(tmp.rglob("*.shp")):
        gdf = gpd.read_file(shp).to_crs(4326)
        gdf["geometry"] = gdf.geometry.make_valid()
        layer = shp.stem
        gdf.to_file(OUT / f"{survey_id}_{layer}.geojson", driver="GeoJSON")
        rows.append({
            "survey": survey_id,
            "layer": layer,
            "n_regions": len(gdf),
            "level_rank": ";".join(map(str, sorted(gdf["LEVELRNK"].unique()))) if "LEVELRNK" in gdf else "",
            "names": "; ".join(gdf.get("REGNAME", pd.Series(dtype=str)).astype(str).head(60)),
        })
    for f in sorted(tmp.rglob("*"), reverse=True):
        f.unlink() if f.is_file() else f.rmdir()
    tmp.rmdir()
    return rows


def main() -> None:
    nums = survey_numbers(SURVEYS)
    rows = []
    for s in SURVEYS:
        if s not in nums:
            print(f"{s}: not found in the DHS survey list")
            continue
        print(f"{s} (survey number {nums[s]}) ...", flush=True)
        try:
            new = save_layers(s, run_job(nums[s]))
            rows += new
            for r in new:
                print(f"  {r['layer']}: {r['n_regions']} regions")
        except Exception as e:  # keep going so one bad survey does not stop the rest
            print(f"  failed: {e}")
    summary = pd.DataFrame(rows)
    summary.to_csv(OUT / "boundary_summary.csv", index=False)
    print(summary[["survey", "layer", "n_regions", "level_rank"]].to_string(index=False) if len(summary) else "Nothing downloaded")


if __name__ == "__main__":
    main()
