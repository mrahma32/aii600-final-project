# NOAA Dulles hourly snapshot — feedback revision

The current notebook reads **data/dulles-hourly-2000-2025.zip** and the tracked **hourly_manifest.json**. It no longer reads the earlier daily snapshot. No raw observations or per-night prediction tables are committed to Git.

## Source and measurement

NOAA ISD-Lite station 724030-93738, WASHINGTON DULLES INTERNATIONAL AP, ICAO KIAD, latitude 38.935, longitude -77.447, elevation 89.5 m, verified against the archived isd-history.csv row. Source collection is station surface observations, rounded/selected near the top of the hour and aggregated by NOAA from multiple reporting sources. Lite duplicate selection considers timing, quality and source ranking; it adds no further quality control and omits individual quality flags. We cannot claim all readings passed quality checks.

- Annual files: https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/YYYY/724030-93738-YYYY.gz
- Format: https://noaa-isd-pds.s3.amazonaws.com/isd-lite/isd-lite-format.txt
- Processing and limitations: https://noaa-isd-pds.s3.amazonaws.com/isd-lite/isd-lite-technical-document.txt
- Station history: https://noaa-isd-pds.s3.amazonaws.com/isd-history.csv
- UTC timestamp documentation: https://noaa-isd-pds.s3.amazonaws.com/isd-format-document.pdf
- Archive migration/cessation: https://www.nesdis.noaa.gov/news/service-location-change-integrated-surface-data-global-hourly
- NOAA data access policy: https://www.noaa.gov/information-technology/open-data-dissemination

NOAA U.S. government observations may be redistributed; retain attribution. Downloaded 2026-11-17. The zip contains 26 original annual gzip files (2000–2025) and three source documentation/metadata text files. The notebook verifies the archive hash and every member against the manifest before parsing. The manifest records every member's URL and SHA-256.

## Retrieve the published snapshot

From the repository root:

```powershell
gh release download data --repo mrahma32/aii600-final-project --dir data --pattern dulles-hourly-2000-2025.zip
```

To fetch source files independently and reproduce the archive:

```powershell
python download_hourly.py
```

No source account or key is needed. This command updates the local manifest: if the source has changed, review and document that revision rather than replacing the notebook's expected hash to bypass verification. The release snapshot is the reproducible record.

Publisher (inspect an existing asset first; do not silently replace it):

```powershell
gh release upload data data/dulles-hourly-2000-2025.zip --repo mrahma32/aii600-final-project
```

## Time window and sample

Convert UTC to America/New_York with daylight-saving handling. Each decision date has a 16:00 forecast origin and a target window 18:00 that evening through 08:00 the next morning, inclusive of the hourly timestamps. There are normally 15 expected samples, 14/16 over daylight-saving changes. Reject missing -9999 temperatures, convert tenths Celsius to Fahrenheit, and require all expected overnight slots. Do not interpolate. A sampled minimum can exceed the true continuous overnight minimum.

Decision dates 2000-01-01–2024-12-31: 9,132 candidate nights; 9,077 have complete target observations; 55 are excluded for missing hourly samples. Two prior complete nights are required as predictors, leaving 8,984 modeling nights: train 6,795 (2000–2018), calibration 1,096 (2019–2021), test 1,093 (2022–2024). The 2025 archive is partial and only supplies the morning of 1 January 2025 for the last 2024 night. The cutoff is due to source coverage, not chosen from scores.

Airport air is not campus pavement or observed ice. The notebook explicitly compares assumed Dulles margins 2,4,6°F below 32°F; neither the offsets nor real-time release availability are validated. Missingness, no Lite flags, and between-hour extremes remain limitations.

## Snapshot hashes

Current archive SHA-256:

```text
eae3997bb1d911aed49bdb0c974aaac8d0aa389695f0e2483b4ea2cee827ee74
```

Each included source member is listed in hourly_manifest.json. The notebook pins the expected archive hash too.

## Earlier snapshot retained for history

The data release also contains USW00093738.dly, the earlier NOAA GHCN-Daily source (https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/USW00093738.dly). Its SHA-256 is 5740ef38697685f37a90dd81b3b9dedd2b67e9fa7a4ed2164850f16aaba6ef84. This revision does not read that file; the earlier daily/32°F analysis is superseded. It remains on the release so its historical decision-log entries can be reproduced from the earlier commit.
