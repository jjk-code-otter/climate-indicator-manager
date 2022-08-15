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
from urllib.parse import urlparse
import requests
import shutil
from datetime import datetime


def filename_from_url(url: str) -> str:
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)

    return filename


def fetch(url: str, outdir: Path):
    now = datetime.now()
    y = now.year
    m = now.month

    nsteps = 24

    for i in range(1, nsteps + 1):

        filled_url = url.replace('YYYY', f'{y}')
        filled_url = filled_url.replace('MMMM', f'{m:02d}')
        filled_url = filled_url.replace('VVVV', '')

        print(filled_url)

        filename = filename_from_url(filled_url)
        out_path = outdir / filename

        print(out_path)

        r = requests.get(filled_url, stream=True, headers={'User-agent': 'Mozilla/5.0'})
        if r.status_code == 200:
            with open(out_path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

        m -= 1
        if m == 0:
            y -= 1
            m = 12
