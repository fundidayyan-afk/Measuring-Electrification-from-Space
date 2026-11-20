# Analysis plan

This file records decisions before we see results, so the paper can show which choices were fixed in advance. Each entry gets a date.

## Fixed in advance

- Study countries: Kenya, Tanzania, Uganda, Rwanda.
- Light data: VIIRS annual V2.2, `average_masked` band; 2012 partial composite excluded.
- Three light measures per unit-year: log(1 + mean radiance), lit land share, lit population share.
- Lit-pixel threshold: set from background pixels in large unsettled protected areas, written here before any model is run.

## Open decisions (to settle with advisors)

1. **DHS reporting level per survey.** Kenya reports both former provinces and counties; we plan to use counties.
2. **Boundary harmonization.** Tanzania created Songwe region from Mbeya between the 2015-16 and 2022 surveys. For long differences, merge back to the older boundaries.
3. **Uganda second wave.** The 2022 Uganda DHS exists (15 statistical regions). Including it gives all four countries two waves.
4. **Survey uncertainty.** If the DHS API does not return confidence intervals for household electricity, options are:
   a. apply for DHS microdata (free) and compute design-based standard errors per region, or
   b. approximate the SE as sqrt(p(1-p)/n * deff) using the unweighted denominator and a stated design effect, with sensitivity to the deff.
5. **Model 1 inference.** With four clusters, a Rademacher wild cluster bootstrap has only 16 distinct draws. Use Webb six-point weights and treat Model 1 as descriptive.

## Survey uncertainty

To be filled in once we know what the DHS API returns.
