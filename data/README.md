# The NOAA Dulles data we used

The notebook uses the saved hourly data in **data/dulles-hourly-2000-2025.zip**. **hourly_manifest.json** lists the files, source links, and file fingerprints. The older daily file is no longer used. The raw readings and individual-night prediction tables stay out of Git.

## Source and measurement

NOAA ISD-Lite station 724030-93738, WASHINGTON DULLES INTERNATIONAL AP, ICAO KIAD, latitude 38.935, longitude -77.447, elevation 89.5 m, verified against the archived isd-history.csv row. NOAA combines station weather reports and chooses readings close to the hour. When reports overlap, it chooses between them using timing, quality and source information. This smaller file format, ISD-Lite, does not keep the original quality flags or add more quality checks. We cannot check the quality of every reading.

- Annual files: https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/YYYY/724030-93738-YYYY.gz
- Format: https://noaa-isd-pds.s3.amazonaws.com/isd-lite/isd-lite-format.txt
- Processing and limitations: https://noaa-isd-pds.s3.amazonaws.com/isd-lite/isd-lite-technical-document.txt
- Station history: https://noaa-isd-pds.s3.amazonaws.com/isd-history.csv
- UTC timestamp documentation: https://noaa-isd-pds.s3.amazonaws.com/isd-format-document.pdf
- Archive migration/cessation: https://www.nesdis.noaa.gov/news/service-location-change-integrated-surface-data-global-hourly
- NOAA data access policy: https://www.noaa.gov/information-technology/open-data-dissemination

NOAA U.S. government observations may be redistributed; retain attribution. Downloaded 2026-11-17. The zip contains 26 original annual gzip files (2000–2025) and three source documentation/metadata text files. Before reading the temperatures, the notebook checks the zip and every file inside it against saved SHA-256 fingerprints. This confirms that everyone uses the same data. The file list records each source link and fingerprint.

## Retrieve the published snapshot

From the repository root:

```powershell
gh release download data --repo mrahma32/aii600-final-project --dir data --pattern dulles-hourly-2000-2025.zip
```

To fetch source files independently and reproduce the archive:

```powershell
python download_hourly.py
```

The NOAA download needs no account or key. This command also updates the local file list and fingerprints. If NOAA has changed a file, check and explain the change; do not simply change the expected fingerprint to skip the check. Download the saved release copy to use exactly the data we used.

Publisher (inspect an existing asset first; do not silently replace it):

```powershell
gh release upload data data/dulles-hourly-2000-2025.zip --repo mrahma32/aii600-final-project
```

## Time window and sample

Change UTC times to Eastern, including daylight-saving changes. We make the decision at 4 p.m. and measure the hourly low from 6 p.m. through 8 a.m. the next morning. That normally gives 15 readings, or 14/16 when the clocks change. The value -9999 means missing. Convert valid readings from tenths Celsius to Fahrenheit and keep only nights with every expected reading. Do not fill gaps. The real low could happen between the hourly readings.

Decision dates 2000-01-01–2024-12-31: 9,132 candidate nights; 9,077 have complete target observations; 55 are excluded for missing hourly samples. Two prior complete nights are required as predictors, leaving 8,984 modeling nights: train 6,795 (2000–2018), calibration 1,096 (2019–2021), test 1,093 (2022–2024). The 2025 archive is partial and only supplies the morning of 1 January 2025 for the last 2024 night. The cutoff is due to source coverage, not chosen from scores.

Airport air temperature does not tell us directly whether campus pavement is icy. We try assumed margins of 2, 4, and 6°F below 32°F; we have not measured which is right. We also need to check whether readings would have been available in time for a real decision. Missing data, absent quality flags, and colder temperatures between readings remain limits.

## Snapshot hashes

Current archive SHA-256:

```text
eae3997bb1d911aed49bdb0c974aaac8d0aa389695f0e2483b4ea2cee827ee74
```

Each source file and its fingerprint is listed in hourly_manifest.json. The notebook also checks that the zip has the expected fingerprint.

## Earlier snapshot retained for history

The data release also contains USW00093738.dly, the earlier NOAA GHCN-Daily source (https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/USW00093738.dly). Its SHA-256 is 5740ef38697685f37a90dd81b3b9dedd2b67e9fa7a4ed2164850f16aaba6ef84. The current notebook does not read this file. The hourly analysis replaces the earlier daily/32°F analysis. We kept the old file on the release so the earlier work can still be repeated from its older commit.
