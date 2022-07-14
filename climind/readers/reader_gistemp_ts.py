from pathlib import Path
import climind.data_types.timeseries as ts


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
        for i in range(2):
            f.readline()
        for line in f:
            columns = line.split(',')
            for i in range(1, 13):
                if columns[i] != '***':
                    years.append(int(columns[0]))
                    months.append(int(i))
                    anomalies.append(float(columns[i]))

    metadata['history'] = [f'Time series created from file {filename}']

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)


def read_annual_ts(filename: str, metadata: dict):
    pass
