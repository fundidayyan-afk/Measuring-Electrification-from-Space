# Model 3 (first pass): long differences

Change in DHS household access between survey waves on change in light, same boundaries in both years.

| Light measure                        | Country effects   |   Coefficient |   Cluster s.e. |   Wild bootstrap p |   Corr. of changes |   Regions |
|:-------------------------------------|:------------------|--------------:|---------------:|-------------------:|-------------------:|----------:|
| People in lit pixels (EOG mask)      | yes               |         0.569 |          0.086 |              0.041 |              0.628 |        84 |
| People in lit pixels (EOG mask)      | no                |         0.829 |          0.070 |              0.056 |              0.628 |        84 |
| People in lit pixels (our threshold) | yes               |         0.554 |          0.121 |              0.053 |              0.557 |        84 |
| People in lit pixels (our threshold) | no                |         0.805 |          0.136 |              0.081 |              0.557 |        84 |
| Log brightness                       | yes               |        -2.512 |          3.142 |              0.459 |              0.174 |        84 |
| Log brightness                       | no                |        12.191 |         11.224 |              0.509 |              0.174 |        84 |

Coefficient: percentage points of access per 1-point rise in the light share (per 1 log unit for brightness). Wild cluster bootstrap with Webb weights, 9,999 draws, 5 country clusters.

## By country

| iso3   |   Regions |   Mean change in access (pp) |   Mean change in lit people, EOG (pp) |   Corr. of changes |
|:-------|----------:|-----------------------------:|--------------------------------------:|-------------------:|
| COD    |     26.00 |                         3.02 |                                 -0.39 |               0.38 |
| KEN    |      8.00 |                        21.05 |                                 14.42 |               0.69 |
| RWA    |      5.00 |                        20.98 |                                  4.89 |               0.02 |
| TZA    |     30.00 |                        15.11 |                                 10.67 |               0.48 |
| UGA    |     15.00 |                        12.19 |                                  7.19 |               0.27 |
