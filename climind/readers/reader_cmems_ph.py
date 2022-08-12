from pathlib import Path
import xarray as xa
import pandas as pd
import numpy as np
import climind.data_types.timeseries as ts
import climind.data_types.grid as gd
import copy

from climind.data_manager.metadata import CombinedMetadata


def read_ts(out_dir: Path, metadata: CombinedMetadata, **kwargs):
    filenames = []
    for filename in out_dir.glob(metadata['filename'][0]):
        filenames.append(filename)
    filenames.sort()
    filename = filenames[-1]

    construction_metadata = copy.deepcopy(metadata)

    if metadata['type'] == 'timeseries':
        if metadata['time_resolution'] == 'monthly':
            raise NotImplementedError
        elif metadata['time_resolution'] == 'annual':
            return read_annual_ts(filename, construction_metadata)
        else:
            raise KeyError(f'That time resolution is not known: {metadata["time_resolution"]}')
    elif metadata['type'] == 'gridded':
        raise NotImplementedError


def read_annual_ts(filename: str, metadata: CombinedMetadata):
    df = xa.open_dataset(filename)

    data = df.ph.values.tolist()
    years = df.time.dt.year.data.tolist()

    metadata['history'] = [f"Time series created from file {metadata['filename']} "
                           f"downloaded from {metadata['url']}"]

    return ts.TimeSeriesAnnual(years, data, metadata=metadata)
