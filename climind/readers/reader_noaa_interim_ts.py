from pathlib import Path
import climind.data_types.timeseries as ts


def read_ts(out_dir: Path, metadata: dict):
    filename = metadata['filename'][0]
    filename = out_dir / filename

    if metadata['time_resolution'] == 'monthly':
        raise NotImplementedError('No official monthly version')
    elif metadata['time_resolution'] == 'annual':
        return read_annual_ts(filename, metadata)
    else:
        raise KeyError(f'That time resolution is not known: {metadata["time_resolution"]}')


def read_monthly_ts(filename: str, metadata: dict):

    raise NotImplementedError


def read_annual_ts(filename: str, metadata: dict):
    years = []
    anomalies = []

    with open(filename, 'r') as f:
        f.readline()
        f.readline()
        for line in f:
            columns = line.split()
            if len(columns) != 4:
                break
            year = columns[0]
            years.append(int(year))
            anomalies.append(float(columns[1]))

    metadata['history'] = [f'Time series created from file {filename}']

    return ts.TimeSeriesAnnual(years, anomalies, metadata=metadata)
