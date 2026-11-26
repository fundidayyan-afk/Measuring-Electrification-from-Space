# Model 2 (first pass): regional access and light

208 region-surveys, 5 countries, 10 surveys.

## A. Fractional logit, unweighted

| Light measure                        | Country effects   |   AME (pp) |   AME s.e. | Change in light   |   R² (pred. vs actual) |   RMSE (pp) |
|:-------------------------------------|:------------------|-----------:|-----------:|:------------------|-----------------------:|------------:|
| People in lit pixels (EOG mask)      | no                |      7.435 |      0.360 | +10 pp            |                  0.736 |      12.532 |
| People in lit pixels (EOG mask)      | yes               |      7.301 |      0.393 | +10 pp            |                  0.824 |      10.224 |
| People in lit pixels (our threshold) | no                |      8.267 |      0.485 | +10 pp            |                  0.620 |      15.036 |
| People in lit pixels (our threshold) | yes               |      7.608 |      0.670 | +10 pp            |                  0.790 |      11.168 |
| Log brightness                       | no                |      5.124 |      0.963 | +0.1 log units    |                  0.536 |      16.625 |
| Log brightness                       | yes               |      3.882 |      0.604 | +0.1 log units    |                  0.642 |      14.600 |
| Land area lit (our threshold)        | no                |     13.834 |      2.476 | +10 pp            |                  0.389 |      19.069 |
| Land area lit (our threshold)        | yes               |     10.887 |      1.714 | +10 pp            |                  0.574 |      15.910 |

AME: average change in predicted household access (percentage points) for the stated change in light. Standard errors clustered by survey (10 clusters) and simulated for the AME; treat as indicative.

## A2. Same, weighted by DHS sample size (robustness)

| Light measure                        | Country effects   |   AME (pp) |   AME s.e. | Change in light   |   R² (pred. vs actual) |   RMSE (pp) |
|:-------------------------------------|:------------------|-----------:|-----------:|:------------------|-----------------------:|------------:|
| People in lit pixels (EOG mask)      | no                |      7.346 |      0.317 | +10 pp            |                  0.736 |      12.634 |
| People in lit pixels (EOG mask)      | yes               |      7.405 |      0.320 | +10 pp            |                  0.824 |      10.241 |
| People in lit pixels (our threshold) | no                |      8.074 |      0.430 | +10 pp            |                  0.621 |      15.044 |
| People in lit pixels (our threshold) | yes               |      7.619 |      0.515 | +10 pp            |                  0.784 |      11.393 |
| Log brightness                       | no                |      4.858 |      0.892 | +0.1 log units    |                  0.531 |      16.767 |
| Log brightness                       | yes               |      4.041 |      0.655 | +0.1 log units    |                  0.640 |      14.660 |
| Land area lit (our threshold)        | no                |     13.851 |      2.799 | +10 pp            |                  0.390 |      19.078 |
| Land area lit (our threshold)        | yes               |     11.640 |      2.150 | +10 pp            |                  0.567 |      16.115 |

Standard errors in this weighted table are approximate (statsmodels does not fully support clustered errors with weights); use it to check that the point estimates are stable.

## B. Leave one country out: predicting a country with no survey

| Light measure                        |   MAE, all held-out regions (pp) |   Worst country MAE (pp) |
|:-------------------------------------|---------------------------------:|-------------------------:|
| Land area lit (our threshold)        |                             17.8 |                     26.3 |
| Log brightness                       |                             15.5 |                     23.3 |
| People in lit pixels (EOG mask)      |                             11.1 |                     14.1 |
| People in lit pixels (our threshold) |                             14.0 |                     19.8 |

Mean bias by held-out country (prediction minus DHS, percentage points):

| Light measure                        |   COD |   KEN |   RWA |   TZA |   UGA |
|:-------------------------------------|------:|------:|------:|------:|------:|
| Land area lit (our threshold)        |  20.7 | -19.3 |  -4.9 |   1.4 |  -0.9 |
| Log brightness                       |  18.7 | -15.4 |  -0.3 |  -0.2 |  -2.6 |
| People in lit pixels (EOG mask)      |  11.5 |  -6.5 | -11.9 |   6.1 | -13.1 |
| People in lit pixels (our threshold) |  19.7 | -15.9 |  -8.4 |   2.3 |  -6.3 |
