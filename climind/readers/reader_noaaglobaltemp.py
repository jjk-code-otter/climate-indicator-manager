from pathlib import Path
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
    list_of_files = list(out_dir.glob(filename_with_wildcards))
    list_of_files.sort()
    out_filename = list_of_files[-1]
    return out_filename


def read_ts(out_dir: Path, metadata: dict):
    url = metadata['url'][0]
    filename_with_wildcards = metadata['filename'][0]
    filename = find_latest(out_dir, filename_with_wildcards)

    construction_metadata = copy.deepcopy(metadata)

    if metadata['time_resolution'] == 'monthly':
        return read_monthly_ts(filename, construction_metadata)
    elif metadata['time_resolution'] == 'annual':
        return read_annual_ts(filename, construction_metadata)
    else:
        raise KeyError(f'That time resolution is not known: {metadata["time_resolution"]}')


def read_monthly_ts(filename: str, metadata: dict):
    """
    Read in monthly file

    Parameters
    ----------
    filename : str
        Filename for monthly file
    metadata : dict
        Dictionary containing metadata
    Returns
    -------
    ts.TimeSeriesMonthly
    """
    years = []
    months = []
    anomalies = []

    with open(filename, 'r') as f:
        for line in f:
            columns = line.split()
            years.append(int(columns[0]))
            months.append(int(columns[1]))
            anomalies.append(float(columns[2]))

    metadata['history'] = [f'Time series created from file {filename}']

    return ts.TimeSeriesMonthly(years, months, anomalies, metadata=metadata)


def read_annual_ts(filename: str, metadata: dict):
    """
    Read in annual file

    Parameters
    ----------
    filename : str
        Filename for annual file
    metadata : dict
        Dictionary containing metadata
    Returns
    -------
    ts.TimeSeriesAnnual
    """
    years = []
    anomalies = []

    with open(filename, 'r') as f:
        for line in f:
            columns = line.split()
            years.append(int(columns[0]))
            anomalies.append(float(columns[1]))

    metadata['history'] = [f'Time series created from file {filename}']

    return ts.TimeSeriesAnnual(years, anomalies, metadata=metadata)
