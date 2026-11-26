"""Machine-learning models: can flexible models predict access better than one light measure?

Data: data/processed/region_survey.csv (208 region-surveys, 5 countries)

Design (matches the proposal)
  * Outer loop: leave one country out. Train on four countries, predict the fifth.
    Country is never a feature, so the model cannot memorise country levels.
  * Inner loop: hyperparameters are chosen by leave-one-country-out inside the
    four training countries only, so the held-out country never influences tuning.
  * Models: fractional logit on the best single measure (baseline), random forest,
    and gradient boosting, all on the same light features.
  * Feature importance: permutation importance on each held-out country, averaged.

Outputs:
    outputs/tables/ml_loco.md / ml_loco.csv        errors by model and held-out country
    outputs/tables/ml_importance.csv               permutation importance
    data/processed/ml_predictions.csv              out-of-sample predictions per region
"""

import itertools
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.inspection import permutation_importance

from config import DATA_PROCESSED, OUT_TABLES

warnings.filterwarnings("ignore", category=FutureWarning)
SEED = 20261126

FEATURES = {
    "lit_pop_share_eog": "People in lit pixels (EOG mask)",
    "lit_pop_share": "People in lit pixels (our threshold)",
    "lit_land_share_eog": "Land lit (EOG mask)",
    "lit_land_share": "Land lit (our threshold)",
    "log_rad": "Log brightness",
    "log_pop_density": "Log population per pixel",
    "cf_cvg_mean": "Cloud-free nights per pixel",
}

GRIDS = {
    "Random forest": {
        "make": lambda p: RandomForestRegressor(n_estimators=500, random_state=SEED, n_jobs=-1, **p),
        "grid": {"min_samples_leaf": [3, 8, 15], "max_features": [0.4, 0.7, 1.0]},
    },
    "Gradient boosting": {
        "make": lambda p: GradientBoostingRegressor(n_estimators=300, subsample=0.8, random_state=SEED, **p),
        "grid": {"learning_rate": [0.02, 0.05], "max_depth": [2, 3], "min_samples_leaf": [5, 15]},
    },
}


def grid(spec):
    keys = list(spec)
    return [dict(zip(keys, vals)) for vals in itertools.product(*spec.values())]


def loco_mae(make, params, X, y, groups):
    """Inner leave-one-country-out MAE for one parameter setting."""
    errs = []
    for g in np.unique(groups):
        tr, te = groups != g, groups == g
        m = make(params).fit(X[tr], y[tr])
        errs.append(np.abs(m.predict(X[te]) - y[te]))
    return np.concatenate(errs).mean()


def frac_logit(train, test, x="lit_pop_share_eog"):
    Xtr = sm.add_constant(train[[x]])
    res = sm.GLM(train["dhs_access"], Xtr, family=sm.families.Binomial()).fit()
    return res.predict(sm.add_constant(test[[x]], has_constant="add")).to_numpy()


def main():
    df = pd.read_csv(DATA_PROCESSED / "region_survey.csv")
    df["log_pop_density"] = np.log(df["pop_per_pixel"].clip(lower=1e-3))
    feats = list(FEATURES)
    X, y, countries = df[feats].to_numpy(), df["dhs_access"].to_numpy(), df["iso3"].to_numpy()

    preds = {name: np.full(len(df), np.nan) for name in ["Fractional logit (1 measure)", *GRIDS]}
    chosen, importances = [], []
    for held in sorted(np.unique(countries)):
        tr, te = countries != held, countries == held
        preds["Fractional logit (1 measure)"][te] = frac_logit(df[tr], df[te])
        for name, spec in GRIDS.items():
            scores = [(loco_mae(spec["make"], p, X[tr], y[tr], countries[tr]), p) for p in grid(spec["grid"])]
            best = min(scores, key=lambda s: s[0])[1]
            model = spec["make"](best).fit(X[tr], y[tr])
            preds[name][te] = model.predict(X[te])
            chosen.append({"model": name, "held_out": held, **best})
            pi = permutation_importance(model, X[te], y[te], n_repeats=30, random_state=SEED,
                                        scoring="neg_mean_absolute_error")
            importances += [{"model": name, "held_out": held, "feature": FEATURES[f],
                             "mae_increase_pp": v * 100} for f, v in zip(feats, pi.importances_mean)]
        print(f"held out {held}: done")

    rows = []
    for name, p in preds.items():
        err = (np.clip(p, 0, 1) - y) * 100
        for held in sorted(np.unique(countries)):
            m = countries == held
            rows.append({"Model": name, "Held-out country": held, "Regions": int(m.sum()),
                         "MAE (pp)": np.abs(err[m]).mean(), "Mean bias (pp)": err[m].mean()})
        rows.append({"Model": name, "Held-out country": "All", "Regions": len(y),
                     "MAE (pp)": np.abs(err).mean(), "Mean bias (pp)": err.mean(),
                     "R² (out of sample)": 1 - ((err / 100) ** 2).sum() / ((y - y.mean()) ** 2).sum()})
    res = pd.DataFrame(rows)
    res.to_csv(OUT_TABLES / "ml_loco.csv", index=False)

    imp = pd.DataFrame(importances)
    imp.to_csv(OUT_TABLES / "ml_importance.csv", index=False)
    imp_sum = (imp.groupby(["model", "feature"])["mae_increase_pp"].mean()
                  .unstack("model").sort_values("Gradient boosting", ascending=False))

    out = df[["iso3", "survey", "SurveyYearLabel", "uid", "REGNAME", "dhs_access"]].copy()
    for name, p in preds.items():
        out["pred_" + name.split(" (")[0].lower().replace(" ", "_")] = np.clip(p, 0, 1)
    out.to_csv(DATA_PROCESSED / "ml_predictions.csv", index=False)

    overall = res[res["Held-out country"] == "All"][["Model", "MAE (pp)", "Mean bias (pp)", "R² (out of sample)"]]
    by_country = res[res["Held-out country"] != "All"].pivot(index="Model", columns="Held-out country", values="MAE (pp)")
    bias = res[res["Held-out country"] != "All"].pivot(index="Model", columns="Held-out country", values="Mean bias (pp)")
    text = ["# Machine-learning models: leave one country out", "",
            f"{len(df)} region-surveys. Every prediction is for a country the model never saw. "
            "Hyperparameters were tuned by leave-one-country-out inside the training countries only.", "",
            "## Overall", "", overall.to_markdown(index=False, floatfmt=".2f"), "",
            "## Mean absolute error by held-out country (pp)", "", by_country.to_markdown(floatfmt=".1f"), "",
            "## Mean bias by held-out country (prediction minus survey, pp)", "", bias.to_markdown(floatfmt=".1f"), "",
            "## Permutation importance (increase in held-out MAE, pp, when a feature is shuffled)", "",
            imp_sum.to_markdown(floatfmt=".2f"), "",
            "## Tuned settings by fold", "", pd.DataFrame(chosen).to_markdown(index=False), ""]
    (OUT_TABLES / "ml_loco.md").write_text("\n".join(text))
    print("\n".join(text[:22]))


if __name__ == "__main__":
    main()
