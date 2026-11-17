# Preliminary checkpoint review

Due 18 November 2026, 7:00 pm Eastern per README. Only pushed `main` counts. Another team member must review and merge this branch's pull request.

## Computed findings

NOAA Dulles daily minima 2000–2025: 9,497 observations. Train 2000–2018, uncertainty calibration 2019–2021, test 2022–2025 (1,461 days, 342 freezing). Regression MAE 6.14°F versus persistence 7.40°F.

| Miss penalty | Persistence penalty units | Regression penalty units | Reduction |
|---|---:|---:|---:|
| 2 | 349 | 260 | 25.5% |
| 5 | 450 | 348 | 22.7% |
| 10 | 500 | 409 | 18.2% |

Units are assumed unnecessary-treatment penalties, not dollars. At ratio 5: regression misses 21 freezing days versus 36; unnecessary flags 243 versus 270. These are air-freezing days, not observed icy nights.

Nominal 90% interval coverage is 89.46% overall but 84.63% in November–March. Residual lag-1 correlation is 0.485. These weaknesses limit the model's reliability for freeze decisions.

## Before submission

- Review the new decisions: daily-air target proxy, forecast-time availability, split cutoffs, regression and sensitivity scenarios. Student approved comparing all three ratios; operational costs remain undecided.
- Publish the exact ignored NOAA snapshot on release `data` using data/README.md. A changing direct-source download does not replace the reproducible release snapshot.
- Have the other teammate review and merge the pull request into this fork's `main` before the deadline.
- Preserve the original proposal and log entry. New entries document this week's work, not reconstructed past studio work.

Presentation files remain the starter for the December checkpoint. CHECKLIST.md remains the final checklist; unverified final requirements have not been ticked.
