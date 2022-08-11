from pathlib import Path
import climind.data_types.timeseries as ts
import numpy as np
import copy
from climind.data_manager.metadata import CombinedMetadata


def read_ts(out_dir: Path, metadata: CombinedMetadata):
    filename = out_dir / metadata['filename'][0]

    construction_metadata = copy.deepcopy(metadata)

    if metadata['time_resolution'] == 'monthly':
        return read_monthly_ts(filename, construction_metadata)
    elif metadata['time_resolution'] == 'annual':
        raise NotImplementedError
    else:
        raise KeyError(f'That time resolution is not known: {metadata["time_resolution"]}')


def read_monthly_ts(filename: str, metadata: CombinedMetadata):
    years = []
    months = []
    anomalies = []

    with open(filename, 'r') as f:
        for i in range(7):
            f.readline()
        for line in f:
            columns = line.split()
            year = columns[1]
            month = columns[2]
            data = float(columns[4])

            years.append(int(year))
            months.append(int(month))
            if data == -999:
                anomalies.append(np.nan)
            else:
                anomalies.append(data/1e6)

    metadata['history'] = [f"Time series created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)
