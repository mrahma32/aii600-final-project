# Decisions

This file is the history of the project. Append an entry when a choice changes the work: the quantity, the data, the split, the model, the loss, or the action. Leave old entries in place. A later entry can reverse an earlier one. If a result depends on a random draw, record the seed under Why. The split entry records the cutoff date, or the seed and the fraction. The pull request that merges the code names this entry.

## 2026-10-28: quantity and data

- Decision. Forecast tonight’s low at Dulles (KIAD), in °F, and use that to decide whether GMU grounds pretreats lots overnight. Data: NOAA daily climate records for the Dulles station.
- Why. The files are public and easy, the quantity is one number per night, and missing a freeze costs more than extra salt.
- Alternative. Next-day Capital Bikeshare trip counts for overnight rebalancing. Same “forecast, then staff” shape, but more download and cleaning for a two-person project that has to land a proposal today.
- Revisit. Switch if Dulles air temperature is too far from campus pavement, or if real freeze nights are too rare in the held-out window to score the decision.
