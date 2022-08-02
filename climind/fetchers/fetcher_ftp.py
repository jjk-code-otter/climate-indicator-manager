from pathlib import Path
import urllib.request
from climind.fetchers.fetcher_utils import filename_from_url


def fetch(url: str, outdir: Path):
    filename = filename_from_url(url)
    out_path = outdir / filename

    with urllib.request.urlopen(url) as r:
        data = r.read()

    with open(out_path, 'wb') as f:
        f.write(data)
