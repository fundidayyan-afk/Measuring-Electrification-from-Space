# Machine-learning models: leave one country out

208 region-surveys. Every prediction is for a country the model never saw. Hyperparameters were tuned by leave-one-country-out inside the training countries only.

## Overall

| Model                        |   MAE (pp) |   Mean bias (pp) |   R² (out of sample) |
|:-----------------------------|-----------:|-----------------:|---------------------:|
| Fractional logit (1 measure) |      11.09 |             0.49 |                 0.67 |
| Random forest                |       9.99 |             0.97 |                 0.73 |
| Gradient boosting            |      11.51 |             1.96 |                 0.66 |

## Mean absolute error by held-out country (pp)

| Model                        |   COD |   KEN |   RWA |   TZA |   UGA |
|:-----------------------------|------:|------:|------:|------:|------:|
| Fractional logit (1 measure) |  12.2 |  11.2 |  12.5 |   8.3 |  14.1 |
| Gradient boosting            |  16.1 |  11.7 |   7.8 |   8.1 |  11.5 |
| Random forest                |  11.3 |  11.9 |   7.3 |   7.3 |  10.7 |

## Mean bias by held-out country (prediction minus survey, pp)

| Model                        |   COD |   KEN |   RWA |   TZA |   UGA |
|:-----------------------------|------:|------:|------:|------:|------:|
| Fractional logit (1 measure) |  11.5 |  -6.5 | -11.9 |   6.1 | -13.1 |
| Gradient boosting            |  15.4 |  -7.6 |  -0.7 |   5.3 |  -9.6 |
| Random forest                |   9.7 |  -6.9 |  -1.1 |   5.4 |  -7.9 |

## Permutation importance (increase in held-out MAE, pp, when a feature is shuffled)

| feature                              |   Gradient boosting |   Random forest |
|:-------------------------------------|--------------------:|----------------:|
| People in lit pixels (EOG mask)      |                2.22 |            2.98 |
| People in lit pixels (our threshold) |                2.03 |            1.58 |
| Log brightness                       |                2.03 |            2.20 |
| Land lit (EOG mask)                  |                1.05 |            0.67 |
| Land lit (our threshold)             |                0.43 |            0.71 |
| Cloud-free nights per pixel          |                0.29 |            0.09 |
| Log population per pixel             |                0.17 |            0.13 |

## Tuned settings by fold

| model             | held_out   |   min_samples_leaf |   max_features |   learning_rate |   max_depth |
|:------------------|:-----------|-------------------:|---------------:|----------------:|------------:|
| Random forest     | COD        |                  3 |            0.4 |          nan    |         nan |
| Gradient boosting | COD        |                  5 |          nan   |            0.02 |           2 |
| Random forest     | KEN        |                  3 |            0.7 |          nan    |         nan |
| Gradient boosting | KEN        |                  5 |          nan   |            0.02 |           3 |
| Random forest     | RWA        |                  3 |            0.7 |          nan    |         nan |
| Gradient boosting | RWA        |                 15 |          nan   |            0.02 |           3 |
| Random forest     | TZA        |                  3 |            0.7 |          nan    |         nan |
| Gradient boosting | TZA        |                  5 |          nan   |            0.05 |           3 |
| Random forest     | UGA        |                  3 |            1   |          nan    |         nan |
| Gradient boosting | UGA        |                 15 |          nan   |            0.02 |           3 |
