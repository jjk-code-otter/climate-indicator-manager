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

from pathlib import Path
import requests
import shutil

from climind.fetchers.fetcher_utils import filename_from_url


def fetch_year(url: str, outdir: Path, year: int):
    for month in range(1, 13):
        filled_url = url.replace('YYYY', f'{year}')
        filled_url = filled_url.replace('MMMM', f'{month:02d}')

        inferred_filename = filename_from_url(filled_url)
        out_path = outdir / inferred_filename

        if not out_path.exists():
            try:
                r = requests.get(filled_url, stream=True, headers={'User-agent': 'Mozilla/5.0'})

                if r.status_code == 200:
                    with open(out_path, 'wb') as f:
                        r.raw.decode_content = True
                        shutil.copyfileobj(r.raw, f)

            except requests.exceptions.ConnectionError:
                print(f"Couldn't connect to {filled_url}")

def fetch(url: str, outdir: Path, _) -> None:

    if 'normals' in url:
        fetch_year(url, outdir, 2222)
    elif 'monitoring' in url:
        for year in range(1982, 2025):
            fetch_year(url, outdir, year)
    elif 'first_guess' in url:
        for year in range(2022, 2025):
            fetch_year(url, outdir, year)