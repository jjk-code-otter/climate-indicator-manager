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

import os
from pathlib import Path
import requests
from dotenv import load_dotenv
from climind.fetchers.fetcher_utils import filename_from_url
from climind.config.config import DATA_DIR
from datetime import datetime


def fetch(url: str, outdir: Path):
    """
    Fetch files from the PODAAC website. Note that the API URL base is:
    API_url = "https://podaac-tools.jpl.nasa.gov/drive/files"

    Parameters
    ----------
    url: str
        URL for the file
    outdir: Path
        directory to which the file will be written.

    Returns
    -------
    None
    """
    load_dotenv()

    username = os.getenv('PODAAC_USER')
    password = os.getenv('PODAAC_PSWD')

    now = datetime.now()
    y = now.year
    m = now.month
    nsteps = 12

    # Search back through past 12 months to finding a matching filename
    for _ in range(1, nsteps + 1):

        filled_url = url.replace('YYYY', f'{y}')
        filled_url = filled_url.replace('MMMM', f'{m:02d}')

        req = requests.get(filled_url, auth=(username, password))

        filename = filename_from_url(filled_url)
        filename = outdir / filename

        if req.status_code != 404:
            with open(filename, 'wb') as outfile:
                chunk_size = 1048576
                for chunk in req.iter_content(chunk_size=chunk_size):
                    outfile.write(chunk)

        m -= 1
        if m == 0:
            y -= 1
            m = 12
