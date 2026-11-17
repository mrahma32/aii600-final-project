# NOAA Dulles data snapshot

NOAA GHCN-Daily station USW00093738, WASHINGTON DULLES INTL AP (KIAD), 38.9347 N, 77.4472 W, 89.6 m elevation. Downloaded 2026-11-17.

Source: https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/USW00093738.dly
Format and flags: https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt
Station metadata: https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt
Citation: Menne et al. (2012), GHCN-Daily Version 3, https://doi.org/10.7289/V5D21VHZ
NOAA data policy: https://www.noaa.gov/information-technology/open-data-dissemination

NOAA U.S. government climate data may be redistributed with attribution. The exact file belongs on the GitHub release tagged `data`, not in Git. The notebook reads only USW00093738.dly; metadata was used to verify station identity.

## Exact file hash

USW00093738.dly SHA-256:

```text
5740ef38697685f37a90dd81b3b9dedd2b67e9fa7a4ed2164850f16aaba6ef84
```

The notebook checks this hash before parsing. A later NOAA download can change: retrieve the release snapshot or document a revision and rerun; never bypass the hash check.

## Reproduction from the repository root

Once the release has been published:

```powershell
gh release download data --repo mrahma32/aii600-final-project --dir data --pattern USW00093738.dly
```

Publisher (requires GitHub write access; inspect an existing release before adding anything):

```powershell
gh release create data data/USW00093738.dly --repo mrahma32/aii600-final-project --title "NOAA Dulles data snapshot" --notes "Downloaded 2026-11-17; source and SHA-256 in data/README.md."
```

Direct source download, no account/key required:

```powershell
Invoke-WebRequest -Uri 'https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/USW00093738.dly' -OutFile 'data/USW00093738.dly'
Get-FileHash data/USW00093738.dly -Algorithm SHA256
```

## Sample and measurement

Unit of observation: station day, parsed from fixed-width station-month-element records. TMIN is tenths of degrees Celsius, converted to Fahrenheit. Exclude sentinel -9999 and nonblank quality flags. Preserve measurement/source flags in the parsed table and reindex the calendar before lagging. Daily station aggregates have NOAA quality processing; instrument history and real-time publication timing were not audited.

2000-01-01 through 2025-12-31: 9,497 valid TMIN days, zero missing/rejected. Three initial rows lack lag history. Modeling rows: 6,937 training (2000-01-04–2018-12-31), 1,096 calibration (2019–2021), 1,461 test (2022–2025). Test includes 342 days at or below 32°F.

Daily airport air temperature is not an exact overnight window, campus pavement temperature, or an ice observation.
