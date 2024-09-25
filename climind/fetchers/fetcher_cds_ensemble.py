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
"""
Fetcher which uses the Copernicus Climate Data Store to download ERA5 gridded data. The first time it is run,
it will download *all* data. This will take a while.
"""
import itertools

import cdsapi
import zipfile
from pathlib import Path
from datetime import datetime
import xarray as xa
import numpy as np

from typing import List


def fetch_year(out_dir: Path, year: int, month: int, day: int, variable: str = 'tas') -> None:
    """
    Fetch a specified year of data and write it to the outdir. If the year is
    incomplete, only recover available months.

    Parameters
    ----------
    out_dir: Path
        directory to which the data will be written
    year: int
        the year of data we want
    variable: str
        Variable to be extracted - either tas or sealevel

    Returns
    -------
    None
    """

    output_file = out_dir / f'era5_ensemble_2m_tas_{year}{month:02d}{day:02d}.grib'
    output_csv_file = out_dir / f'era_5_ensemble_{year}{month:02d}{day:02d}.csv'
    name = 'reanalysis-era5-single-levels'
    request = {
        'product_type': 'ensemble_members',
        'variable': '2m_temperature',
        'year': f'{year}',
        'month': f'{month:02d}',
        'day': f'{day:02d}',
        'time': [
            '00:00', '03:00', '06:00',
            '09:00', '12:00', '15:00',
            '18:00', '21:00',
        ],
        'format': 'grib',
    }

    if output_file.exists() or output_csv_file.exists():
        print(f'File for {year} {month:02d} {day:02d} already exists, not downloading')
    else:
        print(f'Downloading file for {year} {month:02d} {day:02d}')
        print(str(output_file))
        c = cdsapi.Client()
        try:
            c.retrieve(name, request, str(output_file))
        except:
            print(f"Problem downloading {year} {month:02d} {day:02d}")

    if output_file.exists():
        df = xa.open_dataset(output_file, engine='cfgrib')
        weights = np.cos(np.deg2rad(df.latitude))
        area_average = df.weighted(weights).mean(dim=("latitude", "longitude"))
        area_average = area_average.t2m.data - 273.15
        area_average = np.mean(area_average, axis=1)
        area_average = area_average.tolist()
        area_average = [str(i) for i in area_average]
        area_average = ','.join(area_average)

        output_file.unlink()
    else:
        area_average = None

    if output_csv_file.exists() or area_average is None:
        pass
    else:
        with open(output_csv_file, 'w') as f:
            f.write('year,month,day,member1,member2,member3,member4,member5,member6,member7,member8,member9,member10\n')
            f.write(f'{year},{month},{day},{area_average}')


def fetch(url: str, outdir: Path, filename: str) -> None:
    """
    Fetch all data in the range 1979 to 2022.

    Parameters
    ----------
    url: str
        url of the file
    outdir: Path
        Path to the directory to which the data will be written.

    Returns
    -------
    None
    """
    variable = 'tas'

    for year, month in itertools.product(range(1979, 2023), range(1, 13)):
        month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if year % 4 == 0:
            month_lengths = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        for day in range(1, month_lengths[month - 1] + 1):
            fetch_year(outdir, year, month, day, variable)
