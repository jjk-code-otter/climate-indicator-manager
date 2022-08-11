from pathlib import Path
import climind.data_types.timeseries as ts
import numpy as np
import copy
from climind.data_manager.metadata import CombinedMetadata


def read_ts(out_dir: Path, metadata: CombinedMetadata, **kwargs):
    filename = out_dir / metadata['filename'][0]

    construction_metadata = copy.deepcopy(metadata)

    if metadata['type'] == 'timeseries':
        if metadata['time_resolution'] == 'monthly':
            return read_monthly_ts(filename, construction_metadata)
        elif metadata['time_resolution'] == 'annual':
            raise NotImplementedError
        else:
            raise KeyError(f'That time resolution is not known: {metadata["time_resolution"]}')

    elif metadata['type'] == 'gridded':
        raise NotImplementedError


def read_monthly_ts(filename: str, metadata: CombinedMetadata):
    years = []
    months = []
    anomalies = []

    with open(filename, 'r') as f:
        for line in f:
            columns = line.split(',')
            if len(columns) == 8 and columns[0] != 'YYYY':
                year = columns[0]
                month = columns[1]
                years.append(int(year))
                months.append(int(month))
                anomalies.append(float(columns[4]))

    metadata['history'] = [f"Time series created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)
