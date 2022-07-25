from pathlib import Path
import xarray as xa
import climind.data_types.grid as gd
import climind.data_types.timeseries as ts
import copy

def find_latest(out_dir: Path, filename_with_wildcards: str) -> str:
    """
    Find the most recent file that matches

    Parameters
    ----------
    filename_with_wildcards : str
        Filename including wildcards
    out_dir : Path
        Path of data directory

    Returns
    -------

    """
    # look in directory to find all matching
    filename_with_wildcards = filename_with_wildcards.replace('YYYYMMMM', '*')
    list_of_files = list(out_dir.glob(filename_with_wildcards))
    list_of_files.sort()
    out_filename = list_of_files[-1]
    return out_filename


def read_ts(out_dir: Path, metadata: dict):
    url = metadata['url'][0]
    filename_with_wildcards = metadata['filename'][0]
    filename = find_latest(out_dir, filename_with_wildcards)

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



    df = xa.open_mfdataset(filename, combine='nested', concat_dim=["time"])
    return gd.GridMonthly(df, metadata)


def read_monthly_ts(filename: str, metadata: dict):
    years = []
    months = []
    anomalies = []

    with open(filename, 'r') as f:
        for i in range(9):
            f.readline()

        for line in f:
            columns = line.split(',')
            year = columns[0][0:4]
            month = columns[0][4:6]

            years.append(int(year))
            months.append(int(month))
            anomalies.append(float(columns[1]))

    metadata['history'] = [f'Time series created from file {filename}']

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)


def read_annual_ts(filename: str, metadata: dict):
    monthly = read_monthly_ts(filename, metadata)
    annual = monthly.make_annual()

    return annual
