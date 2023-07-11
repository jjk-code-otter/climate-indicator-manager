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

import requests
import os
import tempfile
from dotenv import load_dotenv
from pathlib import Path

r = requests.get('https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-protected/ANTARCTICA_MASS_TELLUS_MASCON_CRI_TIME_SERIES_RL06.1_V3/antarctica_mass_200204_202302.txt')

with open('antarctica.txt', 'wb') as f:
    for chunk in r.iter_content(chunk_size=8192):
        f.write(chunk)
