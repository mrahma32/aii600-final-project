# This week's project results, in plain language

We want to help GMU decide at **4 p.m. whether to salt before tonight**. We compare using a forecast with waiting until ice appears.

## What we changed after the professor's feedback

| What he asked for | What we did |
|---|---|
| Predict tonight, not a whole calendar day | Use hourly Dulles readings from 6 p.m. through 8 a.m. the next morning. |
| State a temperature margin below 32°F | Try assumed margins of 2, 4, and 6°F. These give warning cutoffs of 30, 28, and 26°F. |
| Let the two costs set the action | Try missed-night costs of 2, 5, and 10 times the cost of unnecessary salting. |
| Compare with waiting to see ice | Count that rule as missing the night the ice first forms, as his example says. |
| Compare both rules fairly | Use the same 1,093 test nights and the same scoring rules. Report missed nights and unnecessary salting separately. |

The temperature margins are assumptions. We do not have campus measurements showing which margin is right, or even confirming the direction of the airport-to-campus difference. We show all three rather than picking the one that makes our results look best.

## Why we split the years

- **2000–2018:** teach the model the temperature patterns.
- **2019–2021:** use its errors to estimate how uncertain a forecast is.
- **2022–2024:** test on later nights that were not used in either step above.

Testing on later years is closer to predicting future weather than mixing the years randomly. The archive stops partway through 2025, so 2024 is the last complete year. The first morning of 2025 finishes the overnight window that started December 31, 2024.

## How the model works

We use a linear regression: it combines the lows from the two earlier nights with the time of year. At 4 p.m., both earlier nights are already finished. We also try a simple forecast that repeats the previous night's low; this is called **persistence**.

We chose regression because we can explain what it uses. A more complex model might handle sudden weather changes better. A key weakness is assuming earlier temperature patterns and errors still apply in future cold weather.

## When we would send trucks

The professor's rule is:

**Send trucks when the predicted freeze-warning chance is above Cw / (Cm + Cw).**

Cm is the cost of missing a night. Cw is the cost of salting for nothing. If missing a night costs 5 times as much, we salt when the predicted chance is above **1/6, or 16.67%**. If missing a freeze becomes more expensive, we act at a lower probability.

We do not have GMU's actual dollar costs. We give one unnecessary salting night a score of one penalty unit. The score is:

**missed-night cost × missed nights + nights salted for nothing.**

We try all three cost ratios with all three margins: nine cases in total. These are examples, not a chosen policy. We count warnings based on airport temperature, not observed campus ice.

## One example of the results

Assume a **4°F margin**, so the Dulles warning cutoff is **28°F**, and a missed night costs **5 times** unnecessary salting:

| Rule | Nights missed | Nights salted for nothing | Total penalty score |
|---|---:|---:|---:|
| Wait to see ice | 104 | 0 | 520 |
| Use the afternoon forecast | 10 | 153 | 203 |

The forecast misses fewer nights but sometimes sends trucks unnecessarily. Its total score is lower in this example and in all eight other cases. The waiting rule allows the crew to react later; it simply misses the chance to prevent that night's first freeze. This is the professor's comparison rule, not a record of what GMU actually did.

Our temperature forecast is off by **5.74°F on average**, compared with **6.46°F** for repeating the previous night's low. Those are average absolute errors.

The model also gives a temperature range meant to include 90% of nights. It includes **88.11% overall**, but only **80.40% in November–March**. It is too confident during cold weather, which matters for this decision.

## What each plot shows

- `fig/decision_loss.png`: the forecast's penalty score versus waiting for ice in all nine cases. Lower is better.
- `fig/missed_and_wasted_nights.png`: missed nights and unnecessary salting shown separately.
- `fig/cost_thresholds.png`: why different costs lead to different probability thresholds.
- `fig/nightly_probability.png`: the predicted warning chance over the first 60 winter test nights, with each action threshold shown.
- `fig/raw_temperature.png`: the observed overnight temperatures and assumed cutoffs.
- `fig/residuals_calibration.png`: whether predicted chances match how often airport warnings happen.
- `fig/temperature_residuals.png`: where temperature predictions are too warm or too cold.

## What we still need to check

Airport air is not campus pavement. We did not measure actual ice, wetness, how well salt works, injuries, or dollar savings. Readings once an hour may miss the coldest moment. The smaller NOAA dataset does not include the original quality flags. Leaving out incomplete nights may affect the results. Archived readings may also have been corrected or published too late for a real-time decision.

The earlier whole-day/32°F results used a different target and sample. The current results replace them; they do not show that one unchanged model suddenly improved. We had already viewed that earlier test before making the professor's requested corrections.

## Data and submission

NOAA Dulles station 724030-93738 / KIAD supplies the hourly readings. There are 9,132 possible nights in 2000–2024 and 9,077 with all hourly readings. Requiring two complete earlier nights leaves 6,795 training nights, 1,096 uncertainty-check nights, and 1,093 test nights. The saved data is on the GitHub release named `data`. `hourly_manifest.json` lists the source files and their SHA-256 fingerprints; `data/README.md` explains how to download them.

These explanations summarize this week's entries in `decisions.md`. The original entries remain there as the required history. ChatGPT/Codex helped with the code and writing; we must understand and check the work ourselves.

**Another teammate must review and merge PR #2 into main by November 18, 2026, at 7 p.m. Eastern.** The final presentation and remaining final checklist are for December.
