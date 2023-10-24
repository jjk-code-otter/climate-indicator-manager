#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2023 John Kennedy
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
import itertools
import re
from datetime import datetime
from pathlib import Path
import requests
import shutil
from bs4 import BeautifulSoup, SoupStrainer

from climind.fetchers.fetcher_utils import dir_and_filename_from_url, url_from_filename, get_n_months_back, \
    fill_year_month


def fetch(url: str, outdir: Path, _) -> None:
    """
    Fetch GPCC quantile data. The script scrapes the directory specified in the URL for a file
    that matches the pattern specified in the URL.

    Parameters
    ----------
    url: str
        URL of the file to be downloaded, containing wildcards for information that needs to be matched
        on a case by case basis.
    outdir: Path
        Path of the directory to which the output will be written

    Returns
    -------
    None
    """

    # substitute YYYY and MMMM
    now = datetime.now()
    this_year = now.year
    this_month = now.month

    for y, m in itertools.product(range(1982, this_year + 1), range(1, 13)):

        # Construct the filename for the year and month which covers a 12 month period
        filled_url = fill_year_month(url, y, m)

        if '1month' in filled_url:
            back = 1
        elif '3month' in filled_url:
            back = 3
        elif '6month' in filled_url:
            back = 6
        elif '9month' in filled_url:
            back = 9
        elif '12month' in filled_url:
            back = 12

        y2, m2 = get_n_months_back(y, m, back=back)
        filled_url = filled_url.replace('*', f'{y2}{m2:02d}')

        dirname, filename = dir_and_filename_from_url(filled_url)

        out_path = outdir / filename

        # Need to scoop up the past two years to make sure we get any updates from first guess to monitoring
        if not (out_path.exists()) or (y >= this_year - 1):
            try:
                r = requests.get(filled_url, stream=True, headers={'User-agent': 'Mozilla/5.0'})

                if r.status_code == 200:
                    with open(out_path, 'wb') as f:
                        r.raw.decode_content = True
                        shutil.copyfileobj(r.raw, f)

            except requests.exceptions.ConnectionError:
                print(f"Couldn't connect to {url}")
