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

import itertools
from pathlib import Path
import requests
import shutil
from climind.fetchers.fetcher_utils import filename_from_url


def fetch(url: str, out_dir: Path, _) -> None:
    """
    Fetch ERSST gridded dataset from NOAA. There is one file per month. Only
    files that have not already been downloaded will be downloaded.

    Parameters
    ----------
    url: str
        URL of the file
    out_dir: Path
        Path of the directory to which output will be written
    Returns
    -------
    None
    """
    for year, month in itertools.product(range(1854, 2024), range(1, 13)):

        filled_url = url.replace('*', f'{year}{month:02d}')

        filename = filename_from_url(filled_url)
        out_path = out_dir / filename

        if not out_path.exists():

            r = requests.get(filled_url, stream=True, headers={'User-agent': 'Mozilla/5.0'})
            if r.status_code == 200:
                with open(out_path, 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
