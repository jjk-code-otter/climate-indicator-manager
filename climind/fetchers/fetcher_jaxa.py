#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2025 John Kennedy
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
import urllib.request
from climind.fetchers.fetcher_utils import dir_and_filename_from_url
from datetime import datetime

def fetch(url: str, out_dir: Path, filename: str) -> None:
    """
    Generic fetcher for ftp files

    Parameters
    ----------
    url: str
        URL of the file
    out_dir: Path
        Path of the directory to which the output will be written.
    filename: str
        Filename to save file to

    Returns
    -------
    None
    """
    if 'NHM' in filename:
        regexp = f"JASMES_CLIMATE_SIE_19781101_{datetime.now().year}" + "\\d{4}_5DAVG_PS_NHM_201"
    else:
        regexp = f"JASMES_CLIMATE_SIE_19781101_{datetime.now().year}" + "\\d{4}_5DAVG_PS_SHM_201"

    out_path = out_dir / filename

    with urllib.request.urlopen(url) as r:
        data = r.read()

    data = str(data)

    match = re.search(regexp, data)

    data = data[match.regs[0][0]:match.regs[0][0]+57]

    with urllib.request.urlopen('/'.join([url, data])) as r:
        file_data = r.read()

    with open(out_path, 'wb') as f:
        f.write(file_data)
