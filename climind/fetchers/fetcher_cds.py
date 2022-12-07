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
Fetcher which uses the Copernicus Climate Data Store to download ERA5 gridded data
"""
import cdsapi
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


def fetch_year(out_dir: Path, year: int) -> None:
    """
    Fetch a specified year of data and write it to the outdir. If the year is
    incomplete, only recover available months.

    Parameters
    ----------
    out_dir: Path
        directory to which the data will be written
    year: int
        the year of data we want

    Returns
    -------
    None
    """
    output_file = out_dir / f'era5_2m_tas_{year}.nc'

    now = datetime.now()

    if output_file.exists() and year != now.year:
        print(f'File for {year} already exists, not downloading')
        return

    months_to_download = pick_months(year, now)

    if len(months_to_download) == 0:
        print(f'No months available for {year}')
        return

    print(f'Downloading file for {year}')
    print(str(output_file))
    c = cdsapi.Client()

    c.retrieve(
        'reanalysis-era5-single-levels-monthly-means',
        {
            'product_type': 'monthly_averaged_reanalysis',
            'variable': '2m_temperature',
            'year': [str(year)],
            'month': months_to_download,
            'time': '00:00',
            'format': 'netcdf',
        },
        str(output_file))


def fetch(_, outdir: Path) -> None:
    """
    Fetch all data in the range 1979 to 2022.

    Parameters
    ----------
    _:
        dummy variable needed to match the interface.
    outdir: Path
        Path to the directory to which the data will be written.

    Returns
    -------
    None
    """
    for year in range(1979, 2023):
        fetch_year(outdir, year)
