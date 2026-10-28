# Proposal

At most one page. Replace the prompts under each heading. Leave the headings.

## Hypothesis

If GMU grounds treated parking lots from a forecast of tonight’s low at Dulles, instead of waiting to see ice, they would salt on the nights that matter and skip the ones that do not.

I will forecast **tonight’s minimum temperature at Washington Dulles (KIAD)**, in °F, for one overnight.

## Data

The numbers come from NOAA’s daily climate records for Dulles International (station KIAD). Each day has a minimum temperature, along with things like precipitation that we can use as extra predictors. The series goes back decades, so we will have thousands of nights. The airport station logs the reading automatically.

That reading is not the same thing as a Fairfax parking lot. Dulles is more open and windy than campus, and pavement can sit colder than the air. So we are modeling airport air temperature as a stand-in for the freeze the crew actually cares about. That gap is bias, not random noise.

NOAA data is public domain. We will not put the raw files in git. A cleaned daily table can go on the GitHub release tagged `data`. If we ever cannot post a copy, `data/README.md` will have the download command and the notebook will check file hashes.

## Decision affected by the model

GMU grounds decides, late afternoon, whether to pretreat lots and sidewalks tonight: send the brine/salt trucks, or stand down.

A forecast well below freezing means they roll. A forecast comfortably above means they stay in.

The expensive mistake is skipping a freeze. Ice means slips, injuries, and a much bigger bill than a night of salt they did not strictly need. Wasted salt and overtime are cheaper. We will score the model in those terms (nights missed, or dollars), not in \(R^2\).
