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
import itertools

from climind.config.config import DATA_DIR
from urllib.request import build_opener
import xarray as xa
import pandas as pd
import numpy as np

def down_sample(x, f=4):
    # pad to a multiple of f, so we can reshape
    # use nan for padding, so we needn't worry about denominator in
    # last chunk
    xp = np.r_[x, np.nan + np.zeros((-len(x) % f,))]
    # reshape, so each chunk gets its own row, and then take mean
    return np.nanmean(xp.reshape(-1, f), axis=-1)


def get_and_process_year(year):

    tmp_jra_dir = DATA_DIR / 'JRA_temp'
    tmp_jra_dir.mkdir(exist_ok=True)

    web_root = "https://data.rda.ucar.edu/ds628.0/anl_surf125/"
    filename = f"anl_surf125.011_tmp.{year}010100_{year}123118"
    url = web_root+f"{year}/"+filename

    if not (tmp_jra_dir / filename).exists():
        opener = build_opener()
        infile = opener.open(url)
        with open(tmp_jra_dir / filename, "wb") as outfile:
            outfile.write(infile.read())
            outfile.close()

    # Read in the GRIB file and calculate global mean
    field = xa.open_dataset(tmp_jra_dir / filename, engine='cfgrib')
    weights = np.cos(np.deg2rad(field.latitude))
    regional_ts = field.weighted(weights).mean(dim=("latitude", "longitude"))

    # Reduce from 6-hourly to daily means
    temp_array = down_sample(regional_ts.t2m.data) - 273.15
    temp_array = temp_array.tolist()

    # Make time axis
    times = pd.date_range(start=f'{year}-01-01', freq='1D', periods=len(temp_array))
    years = times.year
    months = times.month
    days = times.day

    # Form into pandas DataFrame for saving
    df = pd.DataFrame(
        {
            'year': years,
            'month': months,
            'day': days,
            'data': temp_array
        }
    )
    df.to_csv(tmp_jra_dir / f"tas_{year}00.csv", index=False)

def get_and_process_year_2014on(year, month):

    tmp_jra_dir = DATA_DIR / 'JRA_temp'
    tmp_jra_dir.mkdir(exist_ok=True)

    # URLs are of the following form:
    # https://data.rda.ucar.edu/ds628.0/anl_surf125/2014/anl_surf125.011_tmp.2014090100_2014093018

    web_root = "https://data.rda.ucar.edu/ds628.0/anl_surf125/"

    month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if year in [2016,2020,2024,2028,2032]:
        month_lengths[1] = 29
    daysin = month_lengths[month-1]

    filename = f"anl_surf125.011_tmp.{year}{month:02d}0100_{year}{month:02d}{daysin:02d}18"
    url = web_root+f"{year}/"+filename

    if not (tmp_jra_dir / filename).exists():
        opener = build_opener()
        infile = opener.open(url)
        with open(tmp_jra_dir / filename, "wb") as outfile:
            outfile.write(infile.read())
            outfile.close()

    # Read in the GRIB file and calculate global mean
    field = xa.open_dataset(tmp_jra_dir / filename, engine='cfgrib')
    weights = np.cos(np.deg2rad(field.latitude))
    regional_ts = field.weighted(weights).mean(dim=("latitude", "longitude"))

    # Reduce from 6-hourly to daily means
    temp_array = down_sample(regional_ts.t2m.data) - 273.15
    temp_array = temp_array.tolist()

    # Make time axis
    times = pd.date_range(start=f'{year}-{month:02d}-01', freq='1D', periods=len(temp_array))
    years = times.year
    months = times.month
    days = times.day

    # Form into pandas DataFrame for saving
    df = pd.DataFrame(
        {
            'year': years,
            'month': months,
            'day': days,
            'data': temp_array
        }
    )
    df.to_csv(tmp_jra_dir / f"tas_{year}{month:02d}.csv", index=False)


for year in range(1958,2014):
    get_and_process_year(year)

for year, month in itertools.product(range(2014,2024), range(1,13)):
    get_and_process_year_2014on(year, month)



pass
