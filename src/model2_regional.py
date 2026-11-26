"""Model 2 (first pass): how well do light measures explain regional access?

Data: data/processed/region_survey.csv (208 region-surveys, 5 countries)

Part A, explanation. Fractional logit (Papke & Wooldridge, 1996) of the DHS
share of households with electricity on one light measure, with and without
country effects. We report the average marginal effect (AME): how many
percentage points of access go with a 10-point rise in the light share (or a
0.1 rise in log brightness). Standard errors are clustered by survey
(10 clusters); with so few clusters they are indicative only.

Part B, prediction. Leave one country out: fit on four countries, predict the
fifth, and report the mean absolute error and mean bias in percentage points.
This answers the applied question, "If a country had no survey, how far off
would a light-based estimate be?" Country effects cannot be used here,
because the held-out country has none.

Survey standard errors are not yet available (they need the DHS microdata),
so this version is unweighted. A robustness run weights by the DHS sample size.

Outputs:
    outputs/tables/model2_regional.md
    outputs/tables/model2_loco.csv
"""

import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

from config import DATA_PROCESSED, OUT_TABLES

# statsmodels: clustered errors are approximate with weights; we only use the weighted
# run to check that point estimates are stable, and say so in the table note.
warnings.filterwarnings("ignore", message="cov_type not fully supported with var_weights")

MEASURES = {
    "lit_pop_share_eog": ("People in lit pixels (EOG mask)", 0.10, "+10 pp"),
    "lit_pop_share": ("People in lit pixels (our threshold)", 0.10, "+10 pp"),
    "log_rad": ("Log brightness", 0.10, "+0.1 log units"),
    "lit_land_share": ("Land area lit (our threshold)", 0.10, "+10 pp"),
}


def frac_logit(df, x, fe, weights=None):
    rhs = f"{x} + C(iso3)" if fe else x
    model = smf.glm(f"dhs_access ~ {rhs}", data=df, family=sm.families.Binomial(),
                    var_weights=weights)   # precision weights: larger samples count more
    return model.fit(cov_type="cluster", cov_kwds={"groups": df["survey"].astype("category").cat.codes})


def ame(res, df, x, step):
    """Average change in predicted access (pp) when x rises by `step`."""
    hi = df.copy()
    hi[x] = hi[x] + step
    return float((res.predict(hi) - res.predict(df)).mean() * 100)


def ame_se(res, df, x, step, draws=2000, seed=1):
    """Simulation (Krinsky-Robb) standard error for the AME."""
    rng = np.random.default_rng(seed)
    b = rng.multivariate_normal(res.params.to_numpy(), res.cov_params().to_numpy(), size=draws)
    X0 = res.model.exog
    hi = df.copy(); hi[x] = hi[x] + step
    X1 = np.asarray(smf.glm(res.model.formula, data=hi, family=sm.families.Binomial()).exog)
    inv = lambda z: 1 / (1 + np.exp(-z))
    vals = (inv(X1 @ b.T) - inv(X0 @ b.T)).mean(axis=0) * 100
    return float(vals.std())


def fit_stats(res, df):
    pred = res.predict(df)
    err = (pred - df["dhs_access"]) * 100
    return float(np.sqrt((err ** 2).mean())), float(np.corrcoef(pred, df["dhs_access"])[0, 1] ** 2)


def part_a(df):
    rows = []
    for x, (label, step, step_lbl) in MEASURES.items():
        for fe in (False, True):
            for w in (None, "n"):
                weights = df["dhs_n_households"] / df["dhs_n_households"].mean() if w else None
                res = frac_logit(df, x, fe, weights)
                rmse, r2 = fit_stats(res, df)
                rows.append({
                    "Light measure": label, "Country effects": "yes" if fe else "no",
                    "Weights": "sample size" if w else "none",
                    f"AME (pp)": ame(res, df, x, step), "AME s.e.": ame_se(res, df, x, step),
                    "Change in light": step_lbl, "R² (pred. vs actual)": r2, "RMSE (pp)": rmse,
                })
    return pd.DataFrame(rows)


def part_b(df):
    rows = []
    for x, (label, *_rest) in MEASURES.items():
        for held in sorted(df["iso3"].unique()):
            train, test = df[df.iso3 != held], df[df.iso3 == held]
            res = smf.glm(f"dhs_access ~ {x}", data=train, family=sm.families.Binomial()).fit()
            err = (res.predict(test) - test["dhs_access"]) * 100
            rows.append({"Light measure": label, "Held-out country": held, "Regions": len(test),
                         "MAE (pp)": float(err.abs().mean()), "Mean bias (pp)": float(err.mean())})
    return pd.DataFrame(rows)


def main():
    df = pd.read_csv(DATA_PROCESSED / "region_survey.csv")
    a = part_a(df)
    b = part_b(df)
    b.to_csv(OUT_TABLES / "model2_loco.csv", index=False)

    main_spec = a[(a.Weights == "none")]
    loco_sum = (b.groupby("Light measure")
                 .apply(lambda g: pd.Series({"MAE, all held-out regions (pp)": np.average(g["MAE (pp)"], weights=g["Regions"]),
                                             "Worst country MAE (pp)": g["MAE (pp)"].max()}), include_groups=False)
                 .reset_index())
    loco_wide = b.pivot(index="Light measure", columns="Held-out country", values="Mean bias (pp)")

    text = ["# Model 2 (first pass): regional access and light", "",
            f"{len(df)} region-surveys, {df.iso3.nunique()} countries, {df.survey.nunique()} surveys.", "",
            "## A. Fractional logit, unweighted", "",
            main_spec.drop(columns="Weights").to_markdown(index=False, floatfmt=".3f"), "",
            "AME: average change in predicted household access (percentage points) for the stated change in light. "
            "Standard errors clustered by survey (10 clusters) and simulated for the AME; treat as indicative.", "",
            "## A2. Same, weighted by DHS sample size (robustness)", "",
            a[a.Weights == "sample size"].drop(columns="Weights").to_markdown(index=False, floatfmt=".3f"), "",
            "Standard errors in this weighted table are approximate (statsmodels does not fully support clustered "
            "errors with weights); use it to check that the point estimates are stable.", "",
            "## B. Leave one country out: predicting a country with no survey", "",
            loco_sum.to_markdown(index=False, floatfmt=".1f"), "",
            "Mean bias by held-out country (prediction minus DHS, percentage points):", "",
            loco_wide.to_markdown(floatfmt=".1f"), ""]
    (OUT_TABLES / "model2_regional.md").write_text("\n".join(text))
    print("\n".join(text))


if __name__ == "__main__":
    main()
