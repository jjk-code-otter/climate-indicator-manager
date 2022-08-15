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
import climind.data_types.timeseries as ts
import copy


def read_ts(out_dir: Path, metadata: dict):
    filename = metadata['filename'][0]
    filename = out_dir / filename

    construction_metadata = copy.deepcopy(metadata)

    if metadata['time_resolution'] == 'monthly':
        raise NotImplementedError('No official monthly version')
    elif metadata['time_resolution'] == 'annual':
        return read_annual_ts(filename, construction_metadata)
    else:
        raise KeyError(f'That time resolution is not known: {metadata["time_resolution"]}')


def read_annual_ts(filename: str, metadata: dict):
    years = []
    data = []
    # Data sample
    # t,category,cat_n_cum,cat_area_cum,cat_n_cum_prop,cat_area_cum_prop,first_n_cum,first_area_cum,first_n_cum_prop,first_area_cum_prop
    # 1982,I Moderate,12850343,6386898194.530531,18.5927,12.4937,236828,114353425.17467934,0.3427,0.2237
    # 1982,II Strong,1612165,901094650.2339222,2.3326,1.7627,184324,105015229.43934757,0.2667,0.2054
    # 1982,III Severe,147165,71382498.9825604,0.2129,0.1396,36762,21933262.28947978,0.0532,0.0429
    # 1982,IV Extreme,31823,11445828.214065524,0.046,0.0224,8620,4150179.8327680673,0.0125,0.0081
    with open(filename, 'r') as f:
        f.readline()
        for line in f:
            columns = line.split(',')

            if columns[1] == 'I Moderate':
                prop_area = 0.0

            prop_area += float(columns[5])

            if columns[1] == 'IV Extreme':
                year = columns[0]
                years.append(int(year))
                data.append(prop_area)

    metadata['history'] = [f"Time series created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]

    return ts.TimeSeriesAnnual(years, data, metadata=metadata)
