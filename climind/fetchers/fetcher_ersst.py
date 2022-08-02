import itertools
from pathlib import Path
import requests
import shutil
from climind.fetchers.fetcher_utils import filename_from_url


def fetch(url: str, outdir: Path):
    for year, month in itertools.product(range(1854, 2023), range(1, 13)):

        filled_url = url.replace('*', f'{year}{month:02d}')

        filename = filename_from_url(filled_url)
        out_path = outdir / filename

        if not out_path.exists():

            r = requests.get(filled_url, stream=True, headers={'User-agent': 'Mozilla/5.0'})
            if r.status_code == 200:
                with open(out_path, 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
