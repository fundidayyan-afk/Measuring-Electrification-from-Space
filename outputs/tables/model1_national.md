# Model 1 (first pass): national changes

| Light measure                        |   Coefficient |   Wild bootstrap p |   Corr. of changes |   Corr. of levels |   Country-years | Years     |
|:-------------------------------------|--------------:|-------------------:|-------------------:|------------------:|----------------:|:----------|
| People in lit pixels (EOG mask)      |         0.405 |              0.896 |              0.305 |             0.779 |              55 | 2014-2024 |
| People in lit pixels (our threshold) |         0.648 |              0.686 |              0.269 |             0.733 |              55 | 2014-2024 |
| Log brightness                       |        60.090 |              0.928 |              0.361 |             0.531 |              55 | 2014-2024 |

Dependent variable: one-year change in World Bank access (percentage points). Light shares are also in percentage points; log brightness is in log units. All models include country effects (country-specific trends). p-values: restricted wild cluster bootstrap, Webb weights, 9999 draws, 5 country clusters.
