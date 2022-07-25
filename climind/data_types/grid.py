import xarray as xa
import logging
from climind.data_manager.metadata import CombinedMetadata


def make_xarray(target_grid, times, latitudes, longitudes):
    """
    Make an xarray Dataset for a regular lat-lon grid from a numpy grid (ntime, nlat, nlon),
    and arrays of time (ntime), latitude (nlat) and longitude (nlon).

    Parameters
    ----------
    target_grid:
        numpy array of shape (ntime, nlat, nlon)
    times:
        Array of times, shape (ntime)
    latitudes:
        Array of latitudes, shape (nlat)
    longitudes
        Array of longitudes, shape (nlon)

    Returns
    -------

    """
    ds = xa.Dataset({
        'tas_mean': xa.DataArray(
            data=target_grid,
            dims=['time', 'latitude', 'longitude'],
            coords={'time': times, 'latitude': latitudes, 'longitude': longitudes},
            attrs={'long_name': '2m air temperature', 'units': 'K'}
        )
    },
        attrs={'project': 'NA'}
    )

    return ds


def log_activity(in_function):
    """
    Decorator function to log name of function run and with which arguments.
    This aims to provide some traceability in the output.

    Parameters
    ----------
    in_function: The function to be decorated

    Returns
    -------

    """

    def wrapper(*args, **kwargs):
        logging.info(f"Running: {in_function.__name__}")
        msg = []
        for a in args:
            if isinstance(a, GridMonthly) or isinstance(a, GridAnnual):
                logging.info(f"on {a.metadata['name']}")
            msg.append(str(a))
        if len(msg) > 0:
            logging.info(f"With arguments:")
            logging.info(', '.join(msg))

        msg = []
        for k in kwargs:
            msg.append(str(k))
        if len(msg) > 0:
            logging.info(f"And keyword arguments:")
            logging.info(', '.join(msg))
        return in_function(*args, **kwargs)

    return wrapper


class GridMonthly:

    def __init__(self, input_data: xa.Dataset, metadata: CombinedMetadata):
        """

        Parameters
        ----------
        input_data: xa.Dataset
            xarray dataset
        metadata: CombinedMetadata
            CombinedMetadata object
        """
        self.df = input_data

        if metadata is None:
            self.metadata = {"name": "", "history": []}
        else:
            self.metadata = metadata


class GridAnnual:

    def __init__(self, input_data, metadata: CombinedMetadata):
        """

        Parameters
        ----------
        input_data: xa.Dataset
            xarray dataset
        metadata: CombinedMetadata
            CombinedMetadata object
        """
        self.df = input_data

        if metadata is None:
            self.metadata = {"name": "", "history": []}
        else:
            self.metadata = metadata
