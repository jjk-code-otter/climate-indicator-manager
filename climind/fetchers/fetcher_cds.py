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
import cdsapi
import zipfile
from pathlib import Path
from datetime import datetime

from typing import List


def pick_months(year: int, now: datetime) -> List[str]:
    """
    For a given year, return a list of strings containing the months which are available in the
    CDS for ERA5. For years before the current year, return all months. For the current year
    return all months up to last month, but only include last month if the day of the month is
    after the 7th

    Parameters
    ----------
    year: int
        Year for which we want to pick months
    now: datetime
        Today, used to assess how incomplete is the current year.

    Returns
    -------
    List[str]
        List of the months to download for the specified year.
    """
    if year < now.year:
        months_to_download = [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
            '10', '11', '12',
        ]
    elif year == now.year:
        months_to_download = []
        for m in range(1, now.month):
            if (m < now.month - 1) or (m == now.month - 1 and now.day > 6):
                months_to_download.append(f'{m:02d}')
    else:
        months_to_download = []

    return months_to_download


def fetch_to_year(out_dir: Path, year: int, variable: str = 'tas') -> None:
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

    if variable == 'tas':
        output_file = out_dir / f'era5_2m_tas_1940_{year}.nc'
        name = 'reanalysis-era5-single-levels-monthly-means'

        years = [str(x) for x in range(1940, year + 1)]
        months = [f"{x:02d}" for x in range(1, 13)]

        request = {
            'product_type': ['monthly_averaged_reanalysis'],
            'variable': ['2m_temperature'],
            'year': years,
            'month': months,
            'time': ['00:00'],
            'data_format': 'netcdf',
            'download_format': 'unarchived'
        }
    elif variable == 'sealevel':
        output_file = out_dir / f'cds_sealevel_{year}.zip'
        name = 'satellite-sea-level-global'
        request = {
            'variable': 'monthly_mean',
            'version': 'vDT2021',
            'format': 'zip',
            'year': [str(year)],
        }
    else:
        raise ValueError(f"Unknown variable {variable}")

    print(f'Downloading file to {year}')
    print(str(output_file))
    c = cdsapi.Client()

    try:
        c.retrieve(name, request, str(output_file))
    except:
        print(f"Problem downloading {year}")

    if '.zip' in str(output_file) and output_file.exists():
        print(f'Unzipping the directory for {year}.')
        with zipfile.ZipFile(output_file, 'r') as zip_ref:
            zip_ref.extractall(out_dir)


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

    if 'sealevel' in filename:
        variable = 'sealevel'
    elif 'era5_2m_tas' in filename:
        variable = 'tas'
    else:
        raise ValueError(f'Filename {filename} corresponds to unknown variable')

    fetch_to_year(outdir, 2025, variable)
