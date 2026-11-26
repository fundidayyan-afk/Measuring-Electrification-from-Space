# Analysis plan

This file records decisions before we see results, so the paper can show which choices were fixed in advance. Each entry gets a date.

## Fixed in advance

- Study countries: Kenya, Tanzania, Uganda, Rwanda.
- Light data: VIIRS annual V2.2, `average_masked` band; 2012 partial composite excluded.
- Three light measures per unit-year: log(1 + mean radiance), lit land share, lit population share.
- Lit-pixel threshold (fixed 2026-11-20, before any light data were pulled): take protected areas in the four countries with IUCN category Ia, Ib or II, area over 1,000 km², and less than 10% marine area (WDPA); keep VIIRS pixels there with zero WorldPop population; compute the 99th percentile of the `average` band for each year; the threshold is the highest of those yearly values. A pixel is lit if `average` exceeds it.
- Robustness version of lit: the Earth Observation Group's own mask (`average_masked` > 0).
- Population for 2013 and 2014 light years uses the 2015 WorldPop R2025A grid (first year available).
- Cloud-free coverage flag: pixels with fewer than 10 cloud-free observations (`cf_cvg` < 10) are counted as low coverage.

## Change log

- 2026-11-25: Added DR Congo (DHS 2013-14 and 2023-24, both reported for the 26 post-2015 provinces). The lit threshold is recomputed with DR Congo's protected areas included, under the same rule. No models had been run when this change was made.

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
