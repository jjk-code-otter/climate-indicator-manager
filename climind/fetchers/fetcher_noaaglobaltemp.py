import re
from pathlib import Path
import requests
import shutil
from bs4 import BeautifulSoup, SoupStrainer

from climind.fetchers.fetcher_utils import dir_and_filename_from_url, url_from_filename


def fetch(url: str, outdir: Path):
    dirname, filename = dir_and_filename_from_url(url)

    # get contents of the directory
    r = requests.get(dirname)

    # compile filename with wildcards into regular expression
    pattern = re.compile(filename)

    # get all <a> tags from the directory and find the one that matches our reg ex
    matched_file = None
    for link in BeautifulSoup(r.text, "html.parser", parse_only=SoupStrainer('a')):
        if link.has_attr('href'):
            if pattern.match(link['href']):
                matched_file = link['href']

    # make the URL for the file that matches and the output file name to save to
    matched_url = url_from_filename(url, matched_file)
    out_path = outdir / matched_file

    # download the matching file
    r = requests.get(matched_url, stream=True, headers={'User-agent': 'Mozilla/5.0'})
    if r.status_code == 200:
        with open(out_path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
