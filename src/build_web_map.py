"""Interactive web map for GitHub Pages: where do nighttime lights miss?

Shows each country's most recent survey regions, colored by the gap between the
share of people in lit pixels (EOG mask) and the DHS share of households with
electricity. A second layer shows DHS access itself. Hovering shows the numbers,
including the random forest's out-of-sample prediction (country never seen).

Output: docs/index.html  (served by GitHub Pages from the docs/ folder)
"""

import json

import folium
import geopandas as gpd
import pandas as pd
from branca.element import Element

from config import DATA_PROCESSED, ROOT

LATEST = {"KE2022DHS": "sdr_subnational_boundaries", "TZ2022DHS": "sdr_subnational_boundaries2",
          "UG2024MIS": "sdr_subnational_boundaries", "RW2019DHS": "sdr_subnational_boundaries",
          "CD2023DHS": "sdr_subnational_boundaries"}
COUNTRY = {"KEN": "Kenya", "TZA": "Tanzania", "UGA": "Uganda", "RWA": "Rwanda", "COD": "DR Congo"}

# Diverging: blue = lights understate access, red = lights overstate, gray = close
GAP_BINS = [(-999, -20, "#1757ac", "Lights 20+ pts below survey"),
            (-20, -10, "#519ced", "10 to 20 below"),
            (-10, -3, "#b6d5f8", "3 to 10 below"),
            (-3, 3, "#efefef", "Within 3 points"),
            (3, 10, "#f8c4c4", "3 to 10 above"),
            (10, 20, "#ec4647", "10 to 20 above"),
            (20, 999, "#b0282a", "Lights 20+ pts above survey")]
ACCESS_BINS = [(0, 10, "#cce3fd"), (10, 25, "#9dc8f7"), (25, 40, "#6aabf1"),
               (40, 55, "#338ced"), (55, 70, "#2370cd"), (70, 85, "#1757ac"), (85, 101, "#0e3d7e")]


def color(v, bins):
    for lo, hi, c, *_ in bins:
        if lo <= v < hi:
            return c
    return "#cccccc"


def main():
    rs = pd.read_csv(DATA_PROCESSED / "region_survey.csv")
    ml = pd.read_csv(DATA_PROCESSED / "ml_predictions.csv")[["uid", "survey", "pred_random_forest"]]
    rs = rs.merge(ml, on=["uid", "survey"], how="left")
    rs = rs[rs.survey.isin(LATEST)]

    parts = []
    for survey, layer in LATEST.items():
        g = gpd.read_file(ROOT / "data" / "boundaries" / f"{survey}_{layer}.geojson").to_crs(4326)
        if survey.startswith("CD") or g["REG_ID"].isna().any():
            g["REG_ID"] = g["REG_ID"].astype(str)
        g["uid"] = survey + "|" + layer + "|" + g["REG_ID"].astype(str)
        parts.append(g[["uid", "geometry"]])
    shapes = gpd.GeoDataFrame(pd.concat(parts, ignore_index=True), crs=4326)
    shapes["geometry"] = shapes.geometry.simplify(0.01, preserve_topology=True)
    gdf = shapes.merge(rs, on="uid", how="inner")
    assert len(gdf) == len(rs), f"{len(rs) - len(gdf)} regions lost joining shapes"

    gdf["gap"] = (gdf["lit_pop_share_eog"] - gdf["dhs_access"]) * 100
    gdf["tip_region"] = gdf["REGNAME"] + ", " + gdf["iso3"].map(COUNTRY)
    gdf["tip_survey"] = gdf["SurveyType"] + " " + gdf["SurveyYearLabel"].astype(str)
    gdf["tip_dhs"] = gdf["dhs_access_pct"].map("{:.0f}%".format)
    gdf["tip_eog"] = (gdf["lit_pop_share_eog"] * 100).map("{:.0f}%".format)
    gdf["tip_thr"] = (gdf["lit_pop_share"] * 100).map("{:.0f}%".format)
    gdf["tip_gap"] = gdf["gap"].map("{:+.0f} points".format)
    gdf["tip_rf"] = (gdf["pred_random_forest"] * 100).map("{:.0f}%".format)
    gdf["c_gap"] = gdf["gap"].map(lambda v: color(v, GAP_BINS))
    gdf["c_access"] = gdf["dhs_access_pct"].map(lambda v: color(v, ACCESS_BINS))

    m = folium.Map(location=[-3, 28], zoom_start=5, tiles=None, control_scale=True)
    folium.TileLayer("OpenStreetMap", control=False).add_to(m)
    fields = ["tip_region", "tip_survey", "tip_dhs", "tip_eog", "tip_thr", "tip_gap", "tip_rf"]
    aliases = ["Region", "Survey", "Households with electricity (survey)", "People in lit pixels (EOG mask)",
               "People in lit pixels (our threshold)", "Lights minus survey",
               "Random forest prediction (country unseen)"]
    data = json.loads(gdf[fields + ["c_gap", "c_access", "geometry"]].to_json())

    for name, key, show in [("Where lights over- or understate access", "c_gap", True),
                            ("Households with electricity (DHS survey)", "c_access", False)]:
        folium.GeoJson(
            data, name=name, show=show, overlay=False,
            style_function=lambda f, key=key: {"fillColor": f["properties"][key], "color": "#ffffff",
                                               "weight": 1, "fillOpacity": 0.85},
            highlight_function=lambda f: {"weight": 2.5, "color": "#1f1f1f"},
            tooltip=folium.GeoJsonTooltip(fields=fields, aliases=aliases, sticky=True,
                                          style="font-family: system-ui, sans-serif; font-size: 12px;"),
        ).add_to(m)
    folium.LayerControl(collapsed=False, position="topright").add_to(m)
    b = gdf.total_bounds
    m.fit_bounds([[b[1], b[0]], [b[3], b[2]]], padding=(20, 20))

    gap_rows = "".join(f'<div class="row"><span class="sw" style="background:{c}"></span>{lbl}</div>'
                       for _, _, c, lbl in GAP_BINS)
    acc_rows = "".join(f'<div class="row"><span class="sw" style="background:{c}"></span>{lo}–{min(hi, 100)}%</div>'
                       for lo, hi, c in ACCESS_BINS)
    panel = f"""
<style>
  .panel {{position:absolute; z-index:1000; left:56px; top:12px; width:330px; background:#fff; padding:14px 16px;
           border-radius:8px; box-shadow:0 1px 6px rgba(0,0,0,.18); font-family:system-ui,sans-serif; color:#1f1f1f}}
  .panel h1 {{font-size:16px; margin:0 0 6px}} .panel p {{font-size:12.5px; line-height:1.45; margin:0 0 8px; color:#3d3d3d}}
  .panel .row {{font-size:12px; display:flex; align-items:center; gap:8px; margin:2px 0}}
  .panel .sw {{width:16px; height:12px; border-radius:2px; border:1px solid #d0d0d0; display:inline-block}}
  .panel .src {{font-size:11px; color:#6b6b6b; margin-top:8px}} .panel a {{color:#1b64be}}
  .panel h2 {{font-size:12px; margin:10px 0 4px; color:#3d3d3d}}
  @media (max-width:600px) {{.panel {{width:auto; right:12px; top:auto; bottom:12px; max-height:45vh; overflow:auto}}}}
</style>
<div class="panel">
  <h1>Measuring electrification from space</h1>
  <p>Do satellite images of light at night show who has electricity? Each region compares the share of people living
     under detectable light with the share of households that a national survey found have electricity.
     Hover over a region for the numbers.</p>
  <h2>Lights minus survey (default layer)</h2>{gap_rows}
  <h2>Survey access (second layer)</h2>{acc_rows}
  <p class="src">Most recent survey per country: Kenya 2022, Tanzania 2022, Uganda 2024-25 (MIS), Rwanda 2019-20,
     DR Congo 2023-24. Light: VIIRS annual composites (EOG). Population: WorldPop. Preliminary results.<br>
     Dayyan Lutshaka Fundi, Lake Forest College ·
     <a href="https://github.com/fundidayyan-afk/Measuring-Electrification-from-Space">code and data</a></p>
</div>"""
    m.get_root().header.add_child(Element('<meta name="viewport" content="width=device-width, initial-scale=1">'))
    m.get_root().html.add_child(Element(panel))
    m.get_root().title = "Measuring Electrification from Space"
    out = ROOT / "docs" / "index.html"
    m.save(str(out))
    print(f"Saved {out} ({out.stat().st_size / 1e6:.1f} MB), {len(gdf)} regions")


if __name__ == "__main__":
    main()
