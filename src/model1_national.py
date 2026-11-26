"""Model 1 (first pass): do national changes in light track changes in access?

Data: data/processed/national_panel.csv (5 countries, World Bank access 2013-2024)

Specification
    d_access_ct = b * d_light_ct + country_c + e_ct
where d_ is the one-year change, in percentage points, and the country
effects allow each country its own trend. Inference uses a wild cluster
bootstrap with Webb six-point weights, clustering by country, with the
null (b = 0) imposed. With five clusters this is the honest way to get a
p-value; ordinary cluster-robust standard errors would be far too small.

Caveat recorded in the analysis plan: the World Bank series is partly
modeled between surveys, so its year-to-year changes are smoother than
reality. Model 1 is a descriptive check, not the core test.

Output: outputs/tables/model1_national.md
"""

import numpy as np
import pandas as pd

from config import DATA_PROCESSED, OUT_TABLES

MEASURES = {
    "lit_pop_share_eog": "People in lit pixels (EOG mask)",
    "lit_pop_share": "People in lit pixels (our threshold)",
    "log_rad": "Log brightness",
}
WEBB = np.array([-np.sqrt(1.5), -1, -np.sqrt(0.5), np.sqrt(0.5), 1, np.sqrt(1.5)])
B = 9999
SEED = 20261126


def design(df: pd.DataFrame, x: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return y, X (light change + country dummies), and cluster codes."""
    fe = pd.get_dummies(df["iso3"], dtype=float)
    X = np.column_stack([df[x].to_numpy(), fe.to_numpy()])
    return df["dy"].to_numpy(), X, df["iso3"].astype("category").cat.codes.to_numpy()


def ols(y, X):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta, y - X @ beta


def cluster_se(X, resid, groups, k=0):
    """CR1 cluster-robust standard error for coefficient k."""
    XtX_inv = np.linalg.inv(X.T @ X)
    meat = np.zeros((X.shape[1], X.shape[1]))
    G = np.unique(groups)
    for g in G:
        s = X[groups == g].T @ resid[groups == g]
        meat += np.outer(s, s)
    n, p = X.shape
    adj = len(G) / (len(G) - 1) * (n - 1) / (n - p)
    V = adj * XtX_inv @ meat @ XtX_inv
    return np.sqrt(V[k, k])


def wild_cluster_p(y, X, groups, rng):
    """Restricted wild cluster bootstrap-t p-value for H0: coefficient 0 = 0."""
    beta, resid = ols(y, X)
    t_obs = beta[0] / cluster_se(X, resid, groups)
    Xr = X[:, 1:]                       # model with the null imposed
    br, er = ols(y, Xr)
    fitted_r = Xr @ br
    G = np.unique(groups)
    t_star = np.empty(B)
    for b in range(B):
        w = rng.choice(WEBB, size=len(G))[np.searchsorted(G, groups)]
        ys = fitted_r + er * w
        bs, rs = ols(ys, X)
        t_star[b] = bs[0] / cluster_se(X, rs, groups)
    return float(np.mean(np.abs(t_star) >= abs(t_obs))), t_obs


def main() -> None:
    nat = pd.read_csv(DATA_PROCESSED / "national_panel.csv").sort_values(["iso3", "year"])
    rng = np.random.default_rng(SEED)
    rows = []
    for x, label in MEASURES.items():
        d = nat.copy()
        d["dy"] = d.groupby("iso3")["wb_access_total"].diff() * 100      # pp
        scale = 1 if x == "log_rad" else 100                                # shares -> pp
        d["dx"] = d.groupby("iso3")[x].diff() * scale
        d = d.dropna(subset=["dy", "dx"])
        y, X, g = design(d.rename(columns={"dx": "x"}), "x")
        beta, resid = ols(y, X)
        p, t = wild_cluster_p(y, X, g, rng)
        # Levels: share of cross-country-year variation in access matched by light
        lv = nat.dropna(subset=["wb_access_total"])
        r_level = lv["wb_access_total"].corr(lv[x])
        r_change = np.corrcoef(d["dx"], d["dy"])[0, 1]
        rows.append({"Light measure": label, "Coefficient": beta[0], "Wild bootstrap p": p,
                     "Corr. of changes": r_change, "Corr. of levels": r_level,
                     "Country-years": len(d), "Years": f"{int(d.year.min())}-{int(d.year.max())}"})
        print(f"{label:40s} b={beta[0]:7.3f}  p={p:.3f}  r_change={r_change:.2f}  r_level={r_level:.2f}  n={len(d)}")

    res = pd.DataFrame(rows)
    note = ("Dependent variable: one-year change in World Bank access (percentage points). "
            "Light shares are also in percentage points; log brightness is in log units. "
            "All models include country effects (country-specific trends). "
            f"p-values: restricted wild cluster bootstrap, Webb weights, {B} draws, 5 country clusters.")
    text = "# Model 1 (first pass): national changes\n\n" + res.to_markdown(index=False, floatfmt=".3f") + "\n\n" + note + "\n"
    (OUT_TABLES / "model1_national.md").write_text(text)
    res.to_csv(OUT_TABLES / "model1_national.csv", index=False)
    print("\nSaved outputs/tables/model1_national.md")


if __name__ == "__main__":
    main()
