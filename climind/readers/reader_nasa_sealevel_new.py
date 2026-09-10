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

import numpy as np
import polars as pl
from astropy.time import Time
from statsmodels.tsa.seasonal import MSTL
import xarray as xa
from scipy.signal import savgol_filter
import climind.data_types.timeseries as ts

from climind.data_manager.metadata import CombinedMetadata
from climind.readers.generic_reader import read_ts

from datetime import timedelta, datetime


def parse_spaced_txt(gmsl: pl.DataFrame, column_names: list):
    parsed = (
        gmsl.with_row_index("id")
        .with_columns(pl.col("line").str.split(r"\s+", literal=False))
        .with_columns(pl.col("line").list.filter(pl.element() != ""))
        .explode("line")
        .with_columns(
            ("col_" + pl.int_range(pl.len()).cast(pl.String).str.zfill(2))
            .over("id")
            .alias("col_nm")
        )
        .pivot(on="col_nm", index=["id"], values=["line"])
    )
    gmsl = parsed.rename({f"col_{i:02d}": name for i, name in enumerate(column_names)})
    gmsl = gmsl.with_columns(pl.all().cast(pl.Float64))
    return gmsl


def convert_partial_year(number):
    year = int(number)
    d = timedelta(days=(number - year) * 365)
    day_one = datetime(year, 1, 1)
    date = d + day_one
    return date


def read_monthly_ts(filename: List[Path], metadata: CombinedMetadata) -> ts.TimeSeriesMonthly:
    aviso_gmsl = xa.open_dataset(filename[1])
    aviso_gmsl = aviso_gmsl.resample(time="MS").mean()

    nasa_gmsl = pl.read_csv(
        filename[0],
        skip_rows=42,
        has_header=False,
        new_columns=["line"],
    )

    nasa_gmsl = parse_spaced_txt(
        nasa_gmsl, column_names=["decyear", "GMSL", "GMSL_filt_2m"]
    )

    # monthly resample
    nasa_gmsl = (
        nasa_gmsl.with_columns(
            date=Time(nasa_gmsl["decyear"], format="decimalyear").ut1.datetime64
        )
        .with_columns(pl.col("date").dt.date())
        .group_by_dynamic("date", every="1mo")
        .agg(pl.col("^GMSL.*$").mean())
    )
    # make decimal year
    nasa_gmsl = nasa_gmsl.with_columns(
        decyear=Time(nasa_gmsl["date"].cast(pl.Datetime), format="datetime64").decimalyear
    )
    # GIA correction
    nasa_gmsl = nasa_gmsl.with_columns(
        GMSL_filt_2m_gia=pl.col("GMSL_filt_2m")
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
                     * 100  # NASA data are in cm
        )
    elif len(aviso_gmsl.time) > len(nasa_gmsl["date"]):
        nasa_gmsl = nasa_gmsl.with_columns(
            TPA_corr=aviso_gmsl.TPA_correction.to_numpy()[0:len(nasa_gmsl["date"])] * 100  # NASA data are in cm
        )
    else:
        nasa_gmsl = nasa_gmsl.with_columns(
            TPA_corr=aviso_gmsl.TPA_correction.to_numpy() * 100  # NASA data are in cm
        )

    nasa_gmsl = nasa_gmsl.with_columns(
        GMSL_filt_2m_gia_tpa=pl.col("GMSL_filt_2m_gia") - pl.col("TPA_corr")
    )

    # deseasonalize
    for var in ["GMSL_filt_2m_gia", "GMSL_filt_2m_gia_tpa"]:
        res = MSTL(nasa_gmsl[var], periods=[12, 6]).fit()
        nasa_gmsl = nasa_gmsl.with_columns(pl.Series(f"{var}_ds", res.trend + res.resid))

    years = [x.year for x in nasa_gmsl["date"]]
    months = [x.month for x in nasa_gmsl["date"]]
    data = nasa_gmsl["GMSL_filt_2m_gia_tpa_ds"].to_numpy() * 10

    return ts.TimeSeriesMonthly(years, months, data, metadata=metadata)
