from pathlib import Path
import climind.data_types.timeseries as ts
import numpy as np


def read_ts(out_dir: Path, metadata: dict):
    filename = out_dir / metadata['filename'][0]

    if metadata['time_resolution'] == 'monthly':
        return read_monthly_ts(filename, metadata)
    elif metadata['time_resolution'] == 'annual':
        return read_annual_ts(filename, metadata)
    else:
        raise KeyError(f'That time resolution is not known: {metadata["time_resolution"]}')


def read_monthly_ts(filename: str, metadata: dict):
    years = []
    months = []
    anomalies = []

    with open(filename, 'r') as f:
        for i in range(35):
            f.readline()

        for line in f:
            columns = line.split()
            year = columns[0]
            month = columns[1]

            years.append(int(year))
            months.append(int(month))
            if columns[2] != '' and int(year) >= 1850:
                anomalies.append(float(columns[2]))
            else:
                anomalies.append(np.nan)


    metadata['history'] = [f'Time series created from file {filename}']

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)


def read_annual_ts(filename: str, metadata: dict):
    monthly = read_monthly_ts(filename, metadata)
    annual = monthly.make_annual()

    return annual
