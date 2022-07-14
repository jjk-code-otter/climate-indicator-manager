import os
from pathlib import Path
from urllib.parse import urlparse
import requests
import shutil


def filename_from_url(url: str) -> str:
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)

    return filename


def fetch(url: str, outdir: Path):
    filename = filename_from_url(url)
    out_path = outdir / filename

    r = requests.get(url, stream=True, headers={'User-agent': 'Mozilla/5.0'})
    if r.status_code == 200:
        with open(out_path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
