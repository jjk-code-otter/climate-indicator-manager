#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2022 John Kennedy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
