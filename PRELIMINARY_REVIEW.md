# Preliminary review — revised for professor issue #1

Due 18 November 2026 at 7:00 pm Eastern per README. Another teammate must review and merge PR #2 into main; this branch alone is not submitted.

## How the analysis reflects the feedback

| Professor's requirement | Revised analysis and figure |
|---|---|
| One late-afternoon decision about tonight | 16:00 Eastern decision; target minimum of hourly readings 18:00–08:00; completed prior nights only as predictors. |
| State the margin below 32°F | Explicit assumed margins 2,4,6°F, cutoffs 30,28,26°F. All scenarios shown; none claimed calibrated. |
| Costs determine the probability threshold | Cm/Cw=2,5,10 gives p > 1/3, 1/6, 1/11. fig/cost_thresholds.png shows expected losses and intersections. |
| Baseline is waiting to see ice | Primary baseline misses every proxy-freeze night before reactive treatment, with zero unnecessary preventive salting. Persistence is additional only. |
| Same held-out nights and loss units | 1,093 complete test nights in 2022–2024 for every method/scenario. fig/decision_loss.png shows common penalty units; fig/missed_and_wasted_nights.png shows both counts. |
| Probability of tonight's freeze | fig/nightly_probability.png plots probabilities under each explicit temperature-margin mapping, with cost thresholds and observed proxy events. Actual campus-ice calibration is not claimed. |

## Computed example, not a chosen policy

For assumed margin 4°F (Dulles cutoff 28°F) and Cm/Cw=5:

| Rule | Nights missed | Nights salted for nothing | Penalty units |
|---|---:|---:|---:|
| Wait to see ice | 104 | 0 | 520 |
| Afternoon forecast | 10 | 153 | 203 |

The forecast has lower weighted penalty than waiting in all nine assumptions. This example was not selected as the operational policy. All outputs appear in fig/decision_scores.csv. No dollar costs, injuries or actual ice were measured.

Temperature forecast MAE 5.74°F versus persistence 6.46°F. Nominal 90% interval coverage 88.11% overall, only 80.40% in November–March. Cold-season uncertainty is a material weakness.

## Source and limits

NOAA hourly station 724030-93738 / KIAD, source hashes in hourly_manifest.json. Snapshot data/dulles-hourly-2000-2025.zip belongs on release data; instructions in data/README.md. Earlier daily snapshot remains available for history but is not read by the revised notebook.

2000–2024 has 9,132 candidate nights, 9,077 complete; after requiring two complete prior nights: train 6,795, calibration 1,096, test 1,093. The archive stops during 2025, so 2024 is the last complete calendar year. Some 2025 records supply the final test night's next-morning observations.

The margins follow the professor's requested below-32 convention but are not measured offsets. Pavement being colder than air alone does not establish this cross-location relation. Obtain paired campus/airport measurements to validate direction and magnitude. The probabilities are for a defined airport proxy, not validated campus ice probabilities. Wetness and treatment effectiveness are absent. Hourly sampling, missing-night selection, no Lite quality flags, and historical reporting delays remain limitations.

Review these assumptions and the appended decision entry before merging. Old daily/32°F results are superseded; new results use a different target/sample and cannot be described as a direct before/after model improvement. Preserve prior decision entries as history. Final presentation and final checklist remain for the December checkpoint.
