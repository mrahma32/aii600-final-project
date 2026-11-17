# Decisions

This file is the history of the project. Append an entry when a choice changes the work: the quantity, the data, the split, the model, the loss, or the action. Leave old entries in place. A later entry can reverse an earlier one. If a result depends on a random draw, record the seed under Why. The split entry records the cutoff date, or the seed and the fraction. The pull request that merges the code names this entry.

## 2026-10-28: quantity and data

- Decision. Forecast tonight’s low at Dulles (KIAD), in °F, and use that to decide whether GMU grounds pretreats lots overnight. Data: NOAA daily climate records for the Dulles station.
- Why. The files are public and easy, the quantity is one number per night, and missing a freeze costs more than extra salt.
- Alternative. Next-day Capital Bikeshare trip counts for overnight rebalancing. Same “forecast, then staff” shape, but more download and cleaning for a two-person project that has to land a proposal today.
- Revisit. Switch if Dulles air temperature is too far from campus pavement, or if real freeze nights are too rare in the held-out window to score the decision.

## 2026-11-17: preliminary target and data

- Decision. Evaluate next-day Dulles daily minimum air temperature using NOAA USW00093738, complete years 2000–2025, as an explicitly imperfect proxy for the proposed overnight campus-pavement target. Team review pending.
- Why/evidence. NOAA metadata identifies Dulles; 9,497 valid daily minima are available. Source and snapshot SHA-256 are in data/README.md. Daily records cannot isolate the overnight window or identify campus ice.
- Alternative. Time-aligned hourly or pavement observations fit the operational target better but need further data and availability checks. Do not claim the daily analysis measures the original overnight-pavement outcome.
- Revisit. Obtain hourly/pavement data or explicitly revise the final question before operational claims. Audit station history and historical publication timing. Archive the exact snapshot on the data release; no raw data enters Git.

## 2026-11-17: chronological split

- Decision. Train through 2018-12-31, calibrate uncertainty on 2019-01-01–2021-12-31, and test on 2022-01-01–2025-12-31. Forecast day t at afternoon t−1 with temperatures at t−2 and t−3 plus calendar season. Team review pending.
- Why/evidence. Future dates represent forecasting. Exclude the incomplete origin day's daily minimum. Calendar reindexing before lagging preserves gaps. Train/calibration/test sizes are 6,937/1,096/1,461. No random split, scaling, feature selection, or fitting uses test rows.
- Alternative. A random split interleaves future weather regimes with training. Lag-1 daily minima risk using incomplete/unavailable information.
- Revisit. Use rolling-origin evaluation if results vary by year. Audit release delays: final t−2 records do not prove historical real-time availability. No random split seed is needed.

## 2026-11-17: baseline, model, and uncertainty

- Decision. Compare persistence TMIN(t−2) with ordinary least-squares regression on TMIN(t−2), TMIN(t−3), and annual sine/cosine. Estimate each forecast distribution from its own calibration residuals. Team review pending.
- Why/evidence. These encode persistence and seasonality without hyperparameter search. Held-out MAE: regression 6.14°F, persistence 7.40°F. Regression nominal 90% coverage is 89.46% overall, 84.63% in November–March. Residual lag-1 correlation is 0.485, contradicting independent-noise behavior. Simulation seed: 600. Fits and empirical probabilities are deterministic.
- Alternative. Trees, neural networks, or archived operational forecasts may capture weather dynamics better but add complexity or data requirements. This analysis does not establish superiority over an operational weather forecast.
- Revisit. Cold-season undercoverage, serial correlation, extremes, and annual cold bias warrant better predictors and rolling-origin checks. Do not repeatedly tune against the existing test results.

## 2026-11-17: loss sensitivity

- Decision. Report r=2,5,10 assumed penalty units per missed freezing day versus one unit per unnecessary-treatment day. Regret is r×misses+unnecessary_flags. Flag when predicted freezing probability is at least 1/(r+1). Keep the operational ratio undecided.
- Why/evidence. The proposal supplies no actual GMU dollar costs. The student approved reporting all three scenarios. Test persistence/regression penalties: 349/260 (r=2), 450/348 (r=5), 500/409 (r=10). At r=5, misses are 36/21 and unnecessary flags 270/243. Always/never-flag policies are also reported.
- Alternative. Selecting one ratio would hide an unsupported assumption; claiming dollars would invent costs. RMSE alone does not measure the stated decision.
- Revisit. Get real treatment costs, effectiveness, wetness information, and missed-ice consequences. Freezing air is not an ice observation. Correct-treatment costs are omitted: these are regret comparisons, not full operating budgets.
