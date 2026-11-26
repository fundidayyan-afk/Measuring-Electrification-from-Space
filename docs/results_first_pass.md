# First-pass results (2026-11-26)

Status: preliminary. Survey standard errors and Kenya 2014 county estimates are pending DHS microdata approval, so all regional models are unweighted (a sample-size-weighted version is reported as a check). Numbers will change when those arrive.

Data: 208 DHS region-surveys in five countries (`data/processed/region_survey.csv`) and 65 country-years (`data/processed/national_panel.csv`). Lit threshold 1.771 nW/cm²/sr.

## Model 1: national changes (`outputs/tables/model1_national.md`)

- Within countries, one-year changes in light do not track one-year changes in World Bank access: coefficient 0.41 (people in lit pixels, EOG mask), wild cluster bootstrap p = 0.90 with five country clusters. The ordinary cluster-robust p-value is 0.34, so the result is weak under either method.
- Levels are related (correlation 0.78 across country-years), and pooled changes without country effects are related (p = 0.02), so the signal is mostly differences between countries, not year-to-year movement within them.
- Consistent with the proposal's caution: the World Bank series is partly modeled between surveys, so its annual changes are a weak benchmark.

## Model 2: regional levels (`outputs/tables/model2_regional.md`)

| Light measure | AME per +10 pp light (no country effects) | R² | RMSE (pp) |
|---|---|---|---|
| People in lit pixels, EOG mask | 7.4 pp | 0.74 | 12.5 |
| People in lit pixels, our threshold | 8.3 pp | 0.62 | 15.0 |
| Log brightness (per +0.1) | 5.1 pp | 0.54 | 16.6 |
| Land area lit | 13.8 pp | 0.39 | 19.1 |

- Population-weighted measures beat brightness and land area, as the proposal predicted.
- Adding country effects raises R² to 0.82 (EOG mask) and barely changes the slope (7.3 pp), so most of the gap between countries is a level shift, not a different slope.
- Sample-size weighting leaves the estimates essentially unchanged.

## Prediction for a country with no survey (leave one country out)

- Best measure (EOG mask): mean absolute error 11.1 pp across all held-out regions; worst country 14.1 pp.
- Bias has a clear country pattern: DR Congo overstated (+11.5 pp), Kenya (-6.5), Rwanda (-11.9) and Uganda (-13.1) understated, Tanzania overstated (+6.1).
- Candidate explanations to test, not yet claims: off-grid solar (Uganda, Rwanda) gives households power without much visible light; mining, ports and city spillover (DR Congo) light up places where few households are connected.

## To do

- Add survey standard errors and inverse-variance weights (microdata).
- Kenya 2014 county estimates (microdata), then Model 3 long differences.
- Test the solar explanation with the DHS electricity-source variable.
- Machine-learning models (random forest, gradient boosting) under the same leave-one-country-out test.
