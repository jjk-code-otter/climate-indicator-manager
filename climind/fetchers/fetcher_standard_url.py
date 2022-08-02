from pathlib import Path
import requests
import shutil

from climind.fetchers.fetcher_utils import filename_from_url


def fetch(url: str, outdir: Path):

    filename = filename_from_url(url)
    out_path = outdir / filename

    r = requests.get(url, stream=True, headers={'User-agent': 'Mozilla/5.0'})
    if r.status_code == 200:
        with open(out_path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
