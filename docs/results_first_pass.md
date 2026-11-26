# First-pass results (updated 2026-11-26)

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

## Machine-learning models (`outputs/tables/ml_loco.md`, `ml_compare.md`)

Same leave-one-country-out test; hyperparameters tuned by leave-one-country-out inside the four training countries only; seven light and population features; country is never a feature.

| Model | MAE (pp) | Out-of-sample R² |
|---|---|---|
| Fractional logit, one measure | 11.1 | 0.67 |
| Random forest | 10.0 | 0.73 |
| Gradient boosting | 11.5 | 0.66 |

- Random forest beats the one-measure baseline by 1.1 points (95% interval 0.2 to 2.0, resampling regions within countries) and in 4 of 5 countries (not Kenya). Gradient boosting does not beat it.
- The gain comes mostly from Rwanda (MAE 12.5 to 7.3) and Uganda (14.1 to 10.7): with several light measures together, the bias there nearly disappears for Rwanda (-11.9 to -1.1) and shrinks for Uganda (-13.1 to -7.9).
- Most important features (held-out permutation importance): people in lit pixels (EOG mask), log brightness, people in lit pixels (our threshold). Population density and cloud cover add little.
- Takeaway: flexibility helps a little, but most of the predictive power is in one well-chosen measure, and the country-level biases remain. That supports the proposal's argument that the problem is what lights measure, not the model.

## Model 3: long differences (`outputs/tables/model3_long_differences.md`)

84 regions observed in two waves (Kenya 8 provinces, Tanzania 30 with Mbeya and Songwe recombined, Uganda 15, Rwanda 5, DR Congo 26), fixed first-wave boundaries.

- With country effects, a 10-point rise in the share of people in lit pixels (EOG mask) goes with a 5.7-point rise in household access (wild cluster bootstrap p = 0.04, five clusters). Our threshold: 5.5 points (p = 0.05). Brightness changes do not predict access changes (p = 0.46).
- Within-region changes are about 0.6 to 0.8 the size of the cross-sectional slope, so lights pick up real changes, not just fixed differences between places.
- Country contrasts: Rwanda's access rose 21 points while lit people rose only 5 (correlation of changes near zero across its 5 provinces); DR Congo's access rose 3 points with no change in lit people.

## Interactive map

`docs/index.html`, served by GitHub Pages. Latest survey per country, colored by lights minus survey, with a second layer for survey access and the random forest's out-of-sample prediction in the hover box. Built by `src/build_web_map.py`.

## To do

- Add survey standard errors and inverse-variance weights (microdata).
- Kenya 2014 county estimates (microdata), then Model 3 long differences.
- Test the solar explanation with the DHS electricity-source variable.
- Kenya county long differences once 2014 county estimates exist.
