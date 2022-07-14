from pathlib import Path
import climind.data_types.timeseries as ts


def read_ts(out_dir: Path, metadata: dict):
    url = metadata['url'][0]
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
        for i in range(86):
            f.readline()

        for line in f:
            columns = line.split()
            if len(columns) < 2:
                break
            years.append(int(columns[0]))
            months.append(int(columns[1]))
            anomalies.append(float(columns[2]))

    metadata['history'] = [f'Time series created from file {filename}']

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)


def read_annual_ts(filename: str, metadata: dict):
    monthly = read_monthly_ts(filename, metadata)
    annual = monthly.make_annual()

    return annual
