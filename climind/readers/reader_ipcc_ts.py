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
    anomalies = []
    """
    HadCRUT, NOAA, Berkeley, Kadow,, 
    HadCRUT confidence limit lower, HadCRUT confidence limit upper
    """
    name = metadata['name']
    if name == 'Kadow IPCC':
        col = 4
    elif name == 'Berkeley IPCC':
        col = 3
    elif name == 'NOAA Interim IPCC':
        col = 2
    else:
        raise KeyError(f"Oh honey, what you doin'  here? {name}")

    with open(filename, 'r') as f:
        f.readline()
        for line in f:
            columns = line.split(',')
            if columns[0] == '':
                break
            year = columns[0]
            years.append(int(year))
            anomalies.append(float(columns[col]))

    metadata['history'] = [f'Time series created from file {filename}']

    return ts.TimeSeriesAnnual(years, anomalies, metadata=metadata)
