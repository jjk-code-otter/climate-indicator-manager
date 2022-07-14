import os
import itertools
from pathlib import Path
from urllib.parse import urlparse
import requests
import shutil


def filename_from_url(url: str) -> str:
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)

    return filename


def fetch(url: str, outdir: Path):

    for year, month in itertools.product(range(1854,2023), range(1,13)):

        filled_url = url.replace('*', f'{year}{month:02d}')

        filename = filename_from_url(filled_url)
        out_path = outdir / filename

        if not out_path.exists():

            r = requests.get(filled_url, stream=True, headers={'User-agent': 'Mozilla/5.0'})
            if r.status_code == 200:
                with open(out_path, 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
