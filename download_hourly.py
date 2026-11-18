"""Download official NOAA hourly snapshots and create a deterministic archive."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import urlopen
import gzip
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parent
BASE = 'https://noaa-isd-pds.s3.amazonaws.com/'
items = {f'724030-93738-{year}.gz': f'{BASE}isd-lite/data/{year}/724030-93738-{year}.gz' for year in range(2000, 2026)}
items.update({name: BASE + suffix for name, suffix in {
    'isd-lite-format.txt': 'isd-lite/isd-lite-format.txt',
    'isd-lite-technical-document.txt': 'isd-lite/isd-lite-technical-document.txt',
    'isd-history.csv': 'isd-history.csv',
}.items()})

def get(item):
    name, url = item
    with urlopen(url, timeout=90) as response:
        data = response.read()
    if name.endswith('.gz'):
        assert data[:2] == b'\x1f\x8b', f'Not gzip: {url}'
        assert len(gzip.decompress(data).splitlines()) > 1000
    return name, data

if __name__ == '__main__':
    downloaded = dict(ThreadPoolExecutor(max_workers=4).map(get, items.items()))
    archive = ROOT / 'data/dulles-hourly-2000-2025.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(downloaded.items()):
            z.writestr(zipfile.ZipInfo(name, date_time=(1980,1,1,0,0,0)), data)
    manifest = {'downloaded': '2026-11-17', 'archive': archive.name,
                'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
                'files': {name: {'source': items[name], 'sha256': hashlib.sha256(data).hexdigest()} for name, data in sorted(downloaded.items())}}
    (ROOT/'hourly_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print('Downloaded', len(downloaded), 'files;', archive.stat().st_size, 'bytes; SHA-256', manifest['sha256'])
