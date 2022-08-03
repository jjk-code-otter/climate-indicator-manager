from pathlib import Path
import climind.data_types.timeseries as ts
import numpy as np
import copy
from climind.data_manager.metadata import CombinedMetadata


def read_ts(out_dir: Path, metadata: CombinedMetadata):
    filenames = []
    for filename in metadata['filename']:
        filenames.append(out_dir / filename)

    construction_metadata = copy.deepcopy(metadata)

    if metadata['time_resolution'] == 'monthly':
        return read_monthly_ts(filenames, construction_metadata)
    elif metadata['time_resolution'] == 'annual':
        raise NotImplementedError
    else:
        raise KeyError(f'That time resolution is not known: {metadata["time_resolution"]}')


def read_monthly_ts(filenames: list, metadata: CombinedMetadata):
    years = []
    months = []
    anomalies = []
    time = []

    for filename in filenames:
        with open(filename, 'r') as f:
            f.readline()
            for line in f:
                columns = line.split(',')
                year = columns[0]
                month = columns[1]
                data = float(columns[4])

                years.append(int(year))
                months.append(int(month))
                time.append(float(year) + (float(month) - 1) / 12.)

                if data == -9999:
                    anomalies.append(np.nan)
                else:
                    anomalies.append(data)

    # Sort based on time axis
    anomalies = [x for _, x in sorted(zip(time, anomalies))]
    years = [x for _, x in sorted(zip(time, years))]
    months = [x for _, x in sorted(zip(time, months))]

    metadata['history'] = [f'Time series created from file {filenames}']

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)
