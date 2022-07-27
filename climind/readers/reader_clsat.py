from pathlib import Path
import xarray as xa
import climind.data_types.grid as gd
import copy


def read_ts(out_dir: Path, metadata: dict):
    filename = out_dir / metadata['filename'][0]

    construction_metadata = copy.deepcopy(metadata)

    if metadata['type'] == 'timeseries':
        if metadata['time_resolution'] == 'monthly':
            return read_monthly_ts(filename, construction_metadata)
        elif metadata['time_resolution'] == 'annual':
            return read_annual_ts(filename, construction_metadata)
        else:
            raise KeyError(f'That time resolution is not known: {metadata["time_resolution"]}')

    elif metadata['type'] == 'gridded':
        return read_monthly_grid(filename, construction_metadata)


def read_monthly_grid(filename: str, metadata):
    df = xa.open_dataset(filename)
    return gd.GridMonthly(df, metadata)


def read_monthly_ts(filename: str, metadata: dict):
    raise NotImplementedError


def read_annual_ts(filename: str, metadata: dict):
    raise NotImplementedError
