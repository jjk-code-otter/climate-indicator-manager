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

from pathlib import Path
import urllib.request
from climind.fetchers.fetcher_utils import filename_from_url


def fetch(url: str, out_dir: Path) -> None:
    """
    Generic fetcher for ftp files

    Parameters
    ----------
    url: str
        URL of the file
    out_dir: Path
        Path of the direcotry to which the output will be written.

    Returns
    -------
    None
    """
    filename = filename_from_url(url)
    out_path = out_dir / filename

    with urllib.request.urlopen(url) as r:
        data = r.read()

    with open(out_path, 'wb') as f:
        f.write(data)
