"""Is the machine-learning gain real? Paired bootstrap of the out-of-sample errors.

Resamples regions within each country (5,000 draws), holding the leave-one-country-out
predictions fixed, and reports the difference in mean absolute error against the
fractional-logit baseline. This captures sampling variation across regions, not the
variation from re-fitting the models, so it is a lower bound on the uncertainty.

Input:  data/processed/ml_predictions.csv (from ml_models.py)
Output: outputs/tables/ml_compare.md
"""

import numpy as np
import pandas as pd

from config import DATA_PROCESSED, OUT_TABLES

p = pd.read_csv(DATA_PROCESSED / "ml_predictions.csv")
err = {c: (p[c] - p["dhs_access"]).abs().to_numpy() * 100
       for c in ["pred_fractional_logit", "pred_random_forest", "pred_gradient_boosting"]}
groups = [np.where(p["iso3"] == c)[0] for c in sorted(p["iso3"].unique())]
rng = np.random.default_rng(20261126)
rows = []
for name, col in [("Random forest", "pred_random_forest"), ("Gradient boosting", "pred_gradient_boosting")]:
    d = []
    for _ in range(5000):
        ix = np.concatenate([rng.choice(g, len(g)) for g in groups])
        d.append(err[col][ix].mean() - err["pred_fractional_logit"][ix].mean())
    d = np.array(d)
    wins = sum(err[col][g].mean() < err["pred_fractional_logit"][g].mean() for g in groups)
    rows.append({"Model vs. fractional logit": name, "Change in MAE (pp)": d.mean(),
                 "95% interval low": np.percentile(d, 2.5), "95% interval high": np.percentile(d, 97.5),
                 "Countries where it is better": f"{wins} of {len(groups)}"})
t = pd.DataFrame(rows)
text = ("# Machine-learning gain over the one-measure baseline\n\n" + t.to_markdown(index=False, floatfmt=".2f") +
        "\n\nNegative = smaller errors than the fractional logit. Regions resampled within countries; "
        "model re-fitting variation not included.\n")
(OUT_TABLES / "ml_compare.md").write_text(text)
print(text)
