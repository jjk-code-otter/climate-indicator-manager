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
from typing import List
from astropy.time import Time
from statsmodels.tsa.seasonal import MSTL
import xarray as xa
import pandas as pd
import polars as pl
import numpy as np
import climind.data_types.timeseries as ts

from climind.data_manager.metadata import CombinedMetadata
from climind.readers.generic_reader import read_ts

from datetime import timedelta, datetime
from scipy.signal import savgol_filter

def convert_partial_year(number):
    year = int(number)
    d = timedelta(days=(number - year) * 365)
    day_one = datetime(year, 1, 1)
    date = d + day_one
    return date


def read_irregular_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesIrregular:
    anomalies = []
    years = []
    months = []
    days = []
    time = []

    with open(filename[0], 'r') as f:
        f.readline()
        for line in f:
            columns = line.split()

            converted_date = convert_partial_year(float(columns[0]))
            anomalies.append(float(columns[1]) + 31.072)
            years.append(converted_date.year)
            months.append(converted_date.month)
            days.append(converted_date.day)

            dt = datetime(converted_date.year, converted_date.month, converted_date.day)
            dt2 = datetime(converted_date.year,12, 31)
            tt = dt.timetuple().tm_yday
            tt2 = dt2.timetuple().tm_yday
            time.append(converted_date.year + tt/tt2)

    # time = np.array(time)
    # time = time - time[0]
    # glacial_isostatic_adjustment = time * 0.3
    smoothed = savgol_filter(anomalies, 31, 2)
    smoothed = smoothed - smoothed[0]
    smoothed = smoothed # + glacial_isostatic_adjustment

    metadata.creation_message()
    outseries = ts.TimeSeriesIrregular(years, months, days, smoothed, metadata=metadata)

    return outseries

def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesMonthly:
    aviso_gmsl = xa.open_dataset(filename[1])
    aviso_gmsl = aviso_gmsl.resample(time="MS").mean()

    nasa_gmsl = pd.read_csv(filename[0], sep="\s+", names=["decyear", "GMSL"], skiprows=1)

    nasa_gmsl = pl.from_pandas(nasa_gmsl)

    # monthly resample
    nasa_gmsl = (
        nasa_gmsl.with_columns(
            date=Time(nasa_gmsl["decyear"], format="decimalyear").ut1.datetime64
        )
        .with_columns(pl.col("date").dt.date())
        .group_by_dynamic("date", every="1mo")
        .agg(pl.col("GMSL").mean())
    )
    # make decimal year
    nasa_gmsl = nasa_gmsl.with_columns(
        decyear=Time(nasa_gmsl["date"].cast(pl.Datetime), format="datetime64").decimalyear
    )
    # GIA correction
    nasa_gmsl = nasa_gmsl.with_columns(
        GMSL_filt_2m_gia=pl.col("GMSL")
                         + 0.03 * (pl.col("decyear") - pl.col("decyear").first())
    )
    # merge TPA correction
    if len(aviso_gmsl.time) < len(nasa_gmsl["date"]):
        nasa_gmsl = nasa_gmsl.with_columns(
            TPA_corr=np.concatenate(
                [
                    aviso_gmsl.TPA_correction.to_numpy(),
                    np.zeros(len(nasa_gmsl["date"]) - len(aviso_gmsl.time)),
                ]
            )
                     * 1000  # NASA data are in cm
        )
    elif len(aviso_gmsl.time) > len(nasa_gmsl["date"]):
        nasa_gmsl = nasa_gmsl.with_columns(
            TPA_corr=aviso_gmsl.TPA_correction.to_numpy()[0:len(nasa_gmsl["date"])] * 1000  # NASA data are in cm
        )
    else:
        nasa_gmsl = nasa_gmsl.with_columns(
            TPA_corr=aviso_gmsl.TPA_correction.to_numpy() * 1000  # NASA data are in cm
        )

    nasa_gmsl = nasa_gmsl.with_columns(
        GMSL_filt_2m_gia_tpa=pl.col("GMSL") - pl.col("TPA_corr")
    )

    # deseasonalize
    for var in ["GMSL_filt_2m_gia_tpa"]:
        res = MSTL(nasa_gmsl[var], periods=[12, 6]).fit()
        nasa_gmsl = nasa_gmsl.with_columns(pl.Series(f"{var}_ds", res.trend + res.resid))

    years = [x.year for x in nasa_gmsl["date"]]
    months = [x.month for x in nasa_gmsl["date"]]
    data = nasa_gmsl["GMSL_filt_2m_gia_tpa_ds"].to_numpy()

    return ts.TimeSeriesMonthly(years, months, data, metadata=metadata)
