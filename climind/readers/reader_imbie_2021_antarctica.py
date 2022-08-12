from pathlib import Path
import numpy as np
import climind.data_types.timeseries as ts
import copy

from climind.data_manager.metadata import CombinedMetadata


def read_ts(out_dir: Path, metadata: CombinedMetadata, **kwargs):
    filename = out_dir / metadata['filename'][0]

    construction_metadata = copy.deepcopy(metadata)

    if metadata['type'] == 'timeseries':
        if metadata['time_resolution'] == 'monthly':
            return read_monthly_ts(filename, construction_metadata, **kwargs)
        elif metadata['time_resolution'] == 'annual':
            return read_annual_ts(filename, construction_metadata, **kwargs)
        else:
            raise KeyError(f'That time resolution is not known: {metadata["time_resolution"]}')
    elif metadata['type'] == 'gridded':
        raise NotImplementedError


def read_monthly_ts(filename: Path, metadata: CombinedMetadata, **kwargs):
    if 'first_difference' in kwargs:
        first_diff = kwargs['first_difference']
    else:
        first_diff = False

    with open(filename, 'r') as in_file:

        in_file.readline()

        years = []
        months = []
        mass_balance = []

        for line in in_file:
            columns = line.split(',')

            decimal_year = float(columns[0])
            year_int = int(decimal_year)
            month = int(np.rint(12. * (decimal_year - year_int) + 1.0))

            if not first_diff:
                data = float(columns[3])
            else:
                data = float(columns[1])

            years.append(year_int)
            months.append(month)
            mass_balance.append(data)

    metadata['history'] = [f"Time series created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]

    return ts.TimeSeriesMonthly(years, months, mass_balance, metadata=metadata)


def read_annual_ts(filename: Path, metadata: CombinedMetadata, **kwargs):
    monthly = read_monthly_ts(filename, metadata, **kwargs)
    annual = monthly.make_annual(cumulative=True)
    return annual
