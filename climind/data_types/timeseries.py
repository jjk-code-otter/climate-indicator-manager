#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2022 John Kennedy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pandas as pd
import logging
import copy
import pkg_resources
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
import cftime as cf
from climind.data_manager.metadata import CombinedMetadata
from climind.definitions import ROOT_DIR


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
            if isinstance(a, TimeSeriesMonthly) or isinstance(a, TimeSeriesAnnual):
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


class TimeSeriesMonthly:

    def __init__(self, years: list, months: list, data: list, metadata=None):
        """
        Monthly time series class

        Parameters
        ----------
        years : list
            List of years
        months : list
            List of months
        data : list
            List of data values
        metadata : CombinedMetadata
            CombinedMetadata object containing the metadata

        Attributes
        ----------
        df : pd.DataFrame
            Pandas dataframe used to contain the time and data information.
        metadata : dict
            Dictionary containing metadata. The only guaranteed entry is "history"
        """
        dico = {'year': years, 'month': months, 'data': data}
        self.df = pd.DataFrame(dico)
        if metadata is None:
            self.metadata = {"name": "", "history": []}
        else:
            self.metadata = metadata

    def __str__(self):
        out_str = f'TimeSeriesMonthly: {self.metadata["name"]}'
        return out_str

    @log_activity
    def make_annual(self, cumulative=False):
        """
        Calculate a TimeSeriesAnnual from the TimeSeriesMonthly. The annual average is
        calculated from the mean of monthly values

        Returns
        -------
        TimeSeriesAnnual
            Return an annual time series
        """
        if cumulative:
            grouped = self.df.groupby(['year'])['data'].sum().reset_index()
        else:
            grouped = self.df.groupby(['year'])['data'].mean().reset_index()
        annual_series = TimeSeriesAnnual.make_from_df(grouped, self.metadata)
        annual_series.metadata['history'].append('Calculated annual average')

        # update attributes
        annual_series.metadata['time_resolution'] = 'annual'
        annual_series.metadata['derived'] = True

        return annual_series

    @log_activity
    def make_annual_by_selecting_month(self, month):
        """
        Calculate a TimeSeriesAnnual from the TimeSeriesMonthly. The annual value is
        taken from one of the monthly values specified by the user3

        Returns
        -------
        TimeSeriesAnnual
            Return an annual time series
        """
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']

        grouped = self.df[self.df['month'] == month].reset_index()
        annual_series = TimeSeriesAnnual.make_from_df(grouped, self.metadata)
        annual_series.metadata['history'].append(f'Extracted {month_names[month - 1]} from each year')

        # update attributes
        annual_series.metadata['time_resolution'] = 'annual'

        return annual_series

    @log_activity
    def manually_set_baseline(self, y1: int, y2: int):
        """
        Manually set baseline.

        Parameters
        ----------
        y1: int
            Start of baseline period
        y2: int
            End of baseline period

        Returns
        -------
        None
        """
        # update attributes
        self.metadata['climatology_start'] = y1
        self.metadata['climatology_end'] = y2
        self.metadata['actual'] = False
        self.metadata['history'].append(f'Manually changed baseline to {y1}-{y2}')

    @log_activity
    def rebaseline(self, y1, y2):
        """
        Shift the time series to a new baseline, specified by start and end years (inclusive).
        Each month is rebaselined separately, allowing for changes in seasonality. If years are
        incomplete, this might give a different result to the annual version.

        Parameters
        ----------
        y1 : int
            The first year of the climatology period
        y2 : int
            The last year of the climatology period

        Returns
        -------
            Action occurs in place
        """
        # select part of series in climatology period
        climatology_part = self.df[(self.df['year'] >= y1) & (self.df['year'] <= y2)]

        # calculate monthly climatology
        climatology = climatology_part.groupby(['month'])['data'].mean().reset_index()
        climatology.rename(columns={'data': 'climatology'}, inplace=True)

        # join climatology to main time series
        self.df = pd.merge(self.df, climatology, on='month', how='left')

        # subtract climatology
        self.df['data'] = self.df['data'] - self.df['climatology']

        # update attributes
        self.metadata['climatology_start'] = y1
        self.metadata['climatology_end'] = y2
        self.metadata['actual'] = False

        self.metadata['history'].append(f'Rebaselined to {y1}-{y2}')

    def get_value(self, year: int, month: int):
        """
        Get the current value for a particular year and month

        Parameters
        ----------
        year: int
            Year requested
        month: int
            Month requested/

        Returns
        -------
        float
            Value for that year and month
        """

        selection = self.df[(self.df['year'] == year) & (self.df['month'] == month)]
        if len(selection) == 0:
            out_value = None
        elif len(selection) == 1:
            out_value = selection['data'].values[0]
        else:
            raise KeyError(f"Selection is not unique {year} {month}")

        return out_value

    def add_offset(self, offset: float):
        """
        Add an offset to the whole data series

        Parameters
        ----------
        offset: float

        Returns
        -------
        None
        """
        self.df['data'] = self.df['data'] + offset

    def zero_on_month(self, year: int, month: int):
        """
        Zero data set on the value for a single month in a single year

        Parameters
        ----------
        year: int
            Year required
        month: int
            Month required

        Returns
        -------
        None
        """

        zero_value = -1 * self.get_value(year, month)
        self.add_offset(zero_value)

    @log_activity
    def select_year_range(self, start_year: int, end_year: int):
        self.df = self.df[self.df['year'] >= start_year]
        self.df = self.df[self.df['year'] <= end_year]
        self.df = self.df.reset_index()
        return self

    @log_activity
    def get_rank_from_year_and_month(self, year: int, month: int, versus_all_months=False) -> int:
        """
        Given a year and month, extract the rank of the data for that month. Ties are given the
        same rank, which is the lowest rank of the group. Default behaviour is to rank the month
        against the same month in all other years. Setting all to True as a keyword argument ranks
        the month against all other months in all other years.

        Parameters
        ----------
        year : int
            Year of year-month pair for which we want the rank
        month : int
            Month of year-month pair for which we want the rank
        versus_all_months : bool
            If set then the ranking is done for the monthly value relative to all other months.

        Returns
        -------
        int
            Returns the rank of the specified year-month pair as compared to the same month in
            all other years. If "versus_all_months" is set then returns rank of the anomaly for a particular year
            and month ranked against all other years and months.
        """
        if versus_all_months:
            month_select = self.df
        else:
            month_select = self.df[self.df['month'] == month]
        ranked = month_select.rank(method='min', ascending=False)
        rank = ranked[(month_select['year'] == year) & (month_select['month'] == month)]['data']

        if len(rank) > 0:
            return int(rank.iloc[0])
        else:
            return None

    def generate_dates(self, time_units):
        time_str = self.df.year.astype(str) + self.df.month.astype(str)
        self.df['time'] = pd.to_datetime(time_str, format='%Y%m')
        dates = cf.date2num(self.df['time'].tolist(),
                            units=time_units,
                            has_year_zero=False,
                            calendar='standard')
        return dates

    def write_csv(self, filename, metadata_filename=None):

        if metadata_filename is not None:
            self.metadata['filename'] = [str(filename.name)]
            self.metadata['url'] = [""]
            self.metadata['reader'] = "reader_badc_csv"
            self.metadata['fetcher'] = "fetcher_no_url"
            self.metadata['history'].append(f"Wrote to file {str(filename.name)}")
            self.metadata.write_metadata(metadata_filename)

        now = datetime.today()
        climind_version = pkg_resources.get_distribution("climind").version

        time_units = 'days since 1800-01-01 00:00:00.0'
        self.df['time'] = self.generate_dates(time_units)

        # populate template to make webpage
        env = Environment(
            loader=FileSystemLoader(ROOT_DIR / "climind" / "data_types" / "jinja_templates"),
            autoescape=select_autoescape()
        )
        template = env.get_template("badc_boilerplate.jinja2")

        rendered = template.render(now=now, climind_version=climind_version,
                                   metadata=self.metadata, monthly=True)

        with open(filename, 'w') as f:
            f.write(rendered)
            f.write(self.df.to_csv(index=False,
                                   line_terminator='\n',
                                   float_format='%.4f',
                                   header=False,
                                   columns=['time', 'year', 'month', 'data']))
            f.write("end data\n")


class TimeSeriesAnnual:

    def __init__(self, years: list, data: list, metadata=None):
        """

        Parameters
        ----------
        years : list
            List of years
        data : list
            List of data values
        metadata : CombinedMetadata
            Dictionary containing the metadata

        Attributes
        ----------
        df : pd.DataFrame
            Pandas dataframe containing the time and data information
        metadata : dict
            Dictionary containing the metadata. The only guaranteed entry is 'history'
        """
        dico = {'year': years, 'data': data}
        self.df = pd.DataFrame(dico)
        if metadata is None:
            self.metadata = {"name": "", "history": []}
        else:
            self.metadata = metadata

    def __str__(self):
        out_str = f'TimeSeriesAnnual: {self.metadata["name"]}'
        return out_str

    @staticmethod
    def make_from_df(df: pd.DataFrame, metadata: dict):
        """
        Create a TimeSeriesAnnual from a pandas data frame.

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe containing columns 'year' and 'data'
        metadata : dict
            Dictionary containing the metadata

        Returns
        -------
        TimeSeriesAnnual
        """
        years = df['year'].tolist()
        data = df['data'].tolist()
        return TimeSeriesAnnual(years, data, metadata)

    @log_activity
    def manually_set_baseline(self, y1: int, y2: int):
        """
        Manually set baseline.

        Parameters
        ----------
        y1: int
            Start of baseline period
        y2: int
            End of baseline period

        Returns
        -------
        None
        """
        # update attributes
        self.metadata['climatology_start'] = y1
        self.metadata['climatology_end'] = y2
        self.metadata['actual'] = False
        self.metadata['history'].append(f'Manually changed baseline to {y1}-{y2}')

    @log_activity
    def rebaseline(self, y1: int, y2: int):
        """
        Shift the time series to a new baseline, specified by start and end years (inclusive).

        Parameters
        ----------
        y1 : int
            First year of the climatology period
        y2 : int
            Last year of the climatology period

        Returns
        -------
            Action occurs in place.
        """
        # select part of series in climatology period
        climatology_part = self.df[(self.df['year'] >= y1) & (self.df['year'] <= y2)]

        # calculate monthly climatology
        climatology = climatology_part['data'].mean()

        # subtract climatology
        self.df['data'] = self.df['data'] - climatology

        # update attributes
        self.metadata['climatology_start'] = y1
        self.metadata['climatology_end'] = y2
        self.metadata['actual'] = False

        self.update_history(f'Rebaselined to {y1}-{y2}')

    @log_activity
    def get_rank_from_year(self, year: int) -> int:
        """
        Given a year, extract the rank of the data for that year. Ties are given the
        same rank, which is the lowest rank of the group.

        Parameters
        ----------
        year : int
            Year for which we want the rank

        Returns
        -------
        int
            Rank of specified year
        """
        ranked = self.df.rank(method='min', ascending=False)
        rank = ranked[self.df['year'] == year]['data']
        if len(rank) == 0:
            return None
        return int(rank.iloc[0])

    @log_activity
    def get_value_from_year(self, year: int) -> float:
        """
        Get the data value for a specified year.

        Parameters
        ----------
        year : int
            Year for which a value is desired

        Returns
        -------
        float
            Or None if year is not in the data set
        """
        val = self.df[self.df['year'] == year]['data']
        if len(val) == 0:
            return None
        return val.iloc[0]

    @log_activity
    def get_year_from_rank(self, rank: int) -> list:
        """
        Given a particular rank, extract a list of years which match that rank.
        Returns a list because years can (theoretically) be tied with each other. Rank
        1 corresponds to the highest value.

        Parameters
        ----------
        rank : int
            Rank for which we want the year which as that rank

        Returns
        -------
        list
            List of years that have the specified rank
        """
        ranked = self.df.rank(method='min', ascending=False)
        years = self.df[ranked['data'] == rank]['year']
        return years.tolist()

    @log_activity
    def running_mean(self, run_length: int):
        """
        Calculate running mean of the data for a specified run length

        Parameters
        ----------
        run_length : int
            length of the run

        Returns
        -------
        TimeSeriesAnnual
            Time series with running average of run_length
        """
        moving_average = copy.deepcopy(self)
        moving_average.df['data'] = moving_average.df['data'].rolling(run_length).mean()
        moving_average.update_history(f'Calculated {run_length}-year moving average')

        moving_average.metadata['derived'] = True

        return moving_average

    @log_activity
    def add_offset(self, offset: float):
        """
        Add an offset to the data set

        Parameters
        ----------
        offset : float
            offset to be added to the data set.

        Returns
        -------

        """

        self.df['data'] = self.df['data'] + offset
        self.metadata['derived'] = True
        self.update_history(f'Added offset of {offset}')

    @log_activity
    def select_decade(self, end_year: int = 0):
        self.df = self.df[self.df['year'] % 10 == end_year]
        self.df = self.df.reset_index()
        self.metadata['derived'] = True
        self.update_history(f'Selected years ending in {end_year}')
        return self

    @log_activity
    def select_year_range(self, start_year: int, end_year: int):
        self.df = self.df[self.df['year'] >= start_year]
        self.df = self.df[self.df['year'] <= end_year]
        self.df = self.df.reset_index()
        return self

    def update_history(self, message: str):
        """
        Update the history metadata

        Parameters
        ----------
        message : str
            Message to be added to history

        Returns
        -------
        None
        """
        self.metadata['history'].append(message)

    def generate_dates(self, time_units):
        self.df['time'] = pd.to_datetime(self.df.year, format='%Y')
        dates = cf.date2num(self.df['time'].tolist(),
                            units=time_units,
                            has_year_zero=False,
                            calendar='standard')
        return dates

    def write_csv(self, filename, metadata_filename=None):

        if metadata_filename is not None:
            self.metadata['filename'] = [str(filename.name)]
            self.metadata['url'] = [""]
            self.metadata['reader'] = "reader_badc_csv"
            self.metadata['fetcher'] = "fetcher_no_url"
            self.metadata['history'].append(f"Wrote to file {str(filename.name)}")
            self.metadata.write_metadata(metadata_filename)

        now = datetime.today()
        climind_version = pkg_resources.get_distribution("climind").version

        time_units = 'days since 1800-01-01 00:00:00.0'
        self.df['time'] = self.generate_dates(time_units)

        # populate template to make webpage
        env = Environment(
            loader=FileSystemLoader(ROOT_DIR / "climind" / "data_types" / "jinja_templates"),
            autoescape=select_autoescape()
        )
        template = env.get_template("badc_boilerplate.jinja2")

        rendered = template.render(now=now, climind_version=climind_version,
                                   metadata=self.metadata, monthly=False)

        with open(filename, 'w') as f:
            f.write(rendered)
            f.write(self.df.to_csv(index=False,
                                   line_terminator='\n',
                                   float_format='%.4f',
                                   header=False,
                                   columns=['time', 'year', 'data']))
            f.write("end data\n")
