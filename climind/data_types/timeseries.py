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

from typing import Optional, Tuple, List
import pandas as pd
import numpy as np
import logging
import copy
import pkg_resources
from pathlib import Path
from functools import reduce
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


class TimeSeries:

    def __init__(self, metadata: CombinedMetadata = None):
        self.df = None
        if metadata is None:
            self.metadata = {"name": "", "history": []}
        else:
            self.metadata = metadata

    @log_activity
    def select_year_range(self, start_year: int, end_year: int):
        self.df = self.df[self.df['year'] >= start_year]
        self.df = self.df[self.df['year'] <= end_year]
        self.df = self.df.reset_index()
        self.update_history(f'Selected years within the range {start_year} to {end_year}.')
        return self

    @log_activity
    def manually_set_baseline(self, baseline_start_year: int, baseline_end_year: int):
        """
        Manually set baseline.

        Parameters
        ----------
        baseline_start_year: int
            Start of baseline period
        baseline_end_year: int
            End of baseline period

        Returns
        -------
        None
        """
        # update attributes
        self.metadata['climatology_start'] = baseline_start_year
        self.metadata['climatology_end'] = baseline_end_year
        self.metadata['actual'] = False
        self.update_history(f'Manually changed baseline to {baseline_start_year}-{baseline_end_year}. '
                            f'Note that data values remain unchanged.')

    def get_first_and_last_year(self) -> Tuple[int, int]:
        """
        Get the first and last year in the series

        Returns
        -------
        Tuple[int, int]
            first and last year
        """
        first_year = self.df['year'].tolist()[0]
        last_year = self.df['year'].tolist()[-1]
        return first_year, last_year

    def update_history(self, message: str) -> None:
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

    @log_activity
    def add_offset(self, offset: float) -> None:
        """
        Add an offset to the data set.

        Parameters
        ----------
        offset : float
            offset to be added to all values in the data set.

        Returns
        -------
        None
        """

        self.df['data'] = self.df['data'] + offset
        self.metadata['derived'] = True
        self.update_history(f'Added offset of {offset} to all data values.')

    def write_generic_csv(self, filename, metadata_filename, monthly, uncertainty, irregular,
                          columns_to_write):

        if metadata_filename is not None:
            self.metadata['filename'] = [str(filename.name)]
            self.metadata['url'] = [""]
            self.metadata['reader'] = "reader_badc_csv"
            self.metadata['fetcher'] = "fetcher_no_url"
            self.update_history(f"Wrote to file {str(filename.name)}")
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
                                   metadata=self.metadata,
                                   monthly=monthly, irregular=irregular,
                                   time_units=time_units, uncertainty=uncertainty)

        with open(filename, 'w') as f:
            f.write(rendered)
            f.write(self.df.to_csv(index=False,
                                   line_terminator='\n',
                                   float_format='%.4f',
                                   header=False,
                                   columns=columns_to_write))
            f.write("end data\n")


class TimeSeriesIrregular(TimeSeries):

    def __init__(self, years: List[int], months: List[int], days: List[int], data: List[float],
                 metadata: CombinedMetadata = None,
                 uncertainty: Optional[List[float]] = None):
        """
        Create TimeSeriesIrregular

        Parameters
        ----------
        years: List[int]
            List of integers specifying the year of each data point
        months: List[int]
            List of integers specifying the month of each data point
        days: List[int]
            List of integers specifying the day of each data point
        data: List[float]
            List of floats with the data values
        metadata: CombinedMetadata
            CombinedMetadata object holding the metadata for the dataset
        uncertainty: List[float]
            List of floats with the uncertainty values for each data point
        """
        super().__init__(metadata)

        dico = {'year': years, 'month': months, 'day': days, 'data': data}
        if uncertainty is not None:
            dico['uncertainty'] = uncertainty
        self.df = pd.DataFrame(dico)

    def __str__(self) -> str:
        out_str = f'TimeSeriesIrregular: {self.metadata["name"]}'
        return out_str

    @log_activity
    def make_monthly(self):
        """
        Calculate a TimeSeriesMonthly from the TimeSeriesIrregular. The monthly average is
        calculated from the mean of values within the month.

        Returns
        -------
        TimeSeriesMonthly
            Return a monthly time series
        """
        self.df['yearmonth'] = 100 * self.df['year'] + self.df['month']

        grouped_data = self.df.groupby(['yearmonth'])['data'].mean().reset_index()
        grouped_years = self.df.groupby(['yearmonth'])['year'].mean().reset_index()
        grouped_months = self.df.groupby(['yearmonth'])['month'].mean().reset_index()

        grouped_months = grouped_months['month'].tolist()
        grouped_data = grouped_data['data'].tolist()
        grouped_years = grouped_years['year'].tolist()

        monthly_series = TimeSeriesMonthly(grouped_years, grouped_months, grouped_data, self.metadata)

        monthly_series.update_history(f'Calculated monthly average from values using arithmetic mean '
                                      f'of all dates that fall within each month')

        # update attributes
        monthly_series.metadata['time_resolution'] = 'monthly'
        monthly_series.metadata['derived'] = True

        return monthly_series

    def get_start_and_end_dates(self) -> Tuple[datetime, datetime]:
        """
        Get the first and last dates in the dataset

        Returns
        -------
        Tuple[datetime, datetime]
        """
        time_str = self.df.year.astype(str) + \
                   self.df.month.map('{:02d}'.format) + \
                   self.df.day.map('{:02d}'.format)
        self.df['time'] = pd.to_datetime(time_str, format='%Y%m%d')

        n_time = len(self.df['time'])

        start_date = self.df['time'][0]
        end_date = self.df['time'][n_time - 1]

        return start_date, end_date

    def generate_dates(self, time_units: str) -> List[int]:
        """
        Given a string specifying the required time units (something like days since 1800-01-01 00:00:00.0),
        generate a list of times from the time series corresponding to those units.

        Parameters
        ----------
        time_units: str
            String specifying the units to use for generating the times e.g. "days since 1800-01-01 00:00:00.0"

        Returns
        -------
        List[int]
        """
        time_str = self.df.year.astype(str) + \
                   self.df.month.map('{:02d}'.format) + \
                   self.df.day.map('{:02d}'.format)
        self.df['time'] = pd.to_datetime(time_str, format='%Y%m%d')
        dates = cf.date2num(self.df['time'].tolist(),
                            units=time_units,
                            has_year_zero=False,
                            calendar='standard')
        return dates

    def write_csv(self, filename: Path, metadata_filename: Path = None) -> None:
        """
        Write the timeseries to a csv file with the specified filename. The format used for writing is given
        by the BADC CSV format. This has a lot of upfront metadata before the data section. An option for writing a
        metadata file is also provided.

        Parameters
        ----------
        filename: Path
            Path of the filename to write the data to
        metadata_filename: Path
            Path of the filename to write the metadata to

        Returns
        -------
        None
        """
        monthly = False
        uncertainty = False
        irregular = True
        columns_to_write = ['time', 'year', 'month', 'day', 'data']
        super().write_generic_csv(filename, metadata_filename,
                                  monthly, uncertainty, irregular,
                                  columns_to_write)

    def get_year_axis(self):
        """
        Return a year axis

        Returns
        -------

        """
        year_axis = self.df['year'] + (self.df['month'] - 1) / 12. + (self.df['day'] - 1) / 365.
        return year_axis

    def get_string_date_range(self) -> str:
        start_date, end_date = self.get_start_and_end_dates()
        date_range = f"{start_date.year}.{start_date.month:02d}.{start_date.day:02d}-" \
                     f"{end_date.year}.{end_date.month:02d}.{end_date.day:02d}"
        return date_range


class TimeSeriesMonthly(TimeSeries):

    def __init__(self, years: List[int], months: List[int], data: List[float], metadata: CombinedMetadata = None,
                 uncertainty: Optional[List[float]] = None):
        """
        Monthly time series class

        Parameters
        ----------
        years : List[int]
            List of years
        months : List[int]
            List of months
        data : List[float]
            List of data values
        metadata : CombinedMetadata
            CombinedMetadata object containing the metadata
        uncertainty: Optional[List[float]]

        Attributes
        ----------
        df : pd.DataFrame
            Pandas dataframe used to contain the time and data information.
        metadata : dict
            Dictionary containing metadata. The only guaranteed entry is "history"
        """

        super().__init__(metadata)

        dico = {'year': years, 'month': months, 'data': data}
        if uncertainty is not None:
            dico['uncertainty'] = uncertainty
        self.df = pd.DataFrame(dico)

        if self.metadata is not None:
            start_date, end_date = self.get_start_and_end_dates()
            self.metadata.dataset['last_month'] = str(end_date)

    def __str__(self) -> str:
        out_str = f'TimeSeriesMonthly: {self.metadata["name"]}'
        return out_str

    @staticmethod
    def make_from_df(df: pd.DataFrame, metadata: CombinedMetadata):
        """
        Create a TimeSeriesMonthly from a pandas data frame.

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe containing columns 'year' 'month' and 'data' (optionally 'uncertainty')
        metadata : dict
            Dictionary containing the metadata

        Returns
        -------
        TimeSeriesMonthly
        """
        years = df['year'].tolist()
        months = df['month'].tolist()
        data = df['data'].tolist()
        if 'uncertainty' in df.columns:
            uncertainty = df['uncertainty'].tolist()
            return TimeSeriesMonthly(years, months, data, metadata, uncertainty=uncertainty)
        else:
            return TimeSeriesMonthly(years, months, data, metadata)

    @log_activity
    def make_annual(self, cumulative: bool = False):
        """
        Calculate a TimeSeriesAnnual from the TimeSeriesMonthly. The annual average is
        calculated from the mean of monthly values

        Parameters
        ----------
        cumulative : bool
            Set to true to sum rather than average the monthly values to get the annual value.

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

        if cumulative:
            annual_series.update_history('Calculated annual value from monthly values by summing')
        else:
            annual_series.update_history('Calculated annual average from monthly averages using arithmetic mean')

        # update attributes
        annual_series.metadata['time_resolution'] = 'annual'
        annual_series.metadata['derived'] = True

        return annual_series

    @log_activity
    def make_annual_by_selecting_month(self, month: int):
        """
        Calculate a TimeSeriesAnnual from the TimeSeriesMonthly. The annual value is
        taken from one of the monthly values specified by the user.

        Returns
        -------
        TimeSeriesAnnual
            Return an annual time series
        """
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']

        grouped = self.df[self.df['month'] == month].reset_index()
        annual_series = TimeSeriesAnnual.make_from_df(grouped, self.metadata)
        annual_series.metadata['history'].append(
            f'Calculated annual series by extracting {month_names[month - 1]} from each year'
        )

        # update attributes
        annual_series.metadata['time_resolution'] = 'annual'

        return annual_series

    @log_activity
    def rebaseline(self, baseline_start_year, baseline_end_year):
        """
        Shift the time series to a new baseline, specified by start and end years (inclusive).
        Each month is rebaselined separately, allowing for changes in seasonality. If years are
        incomplete, this might give a different result to the annual version.

        Parameters
        ----------
        baseline_start_year : int
            The first year of the climatology period
        baseline_end_year : int
            The last year of the climatology period

        Returns
        -------
            Action occurs in place
        """
        # select part of series in climatology period
        climatology_part = self.df[(self.df['year'] >= baseline_start_year) & (self.df['year'] <= baseline_end_year)]

        # calculate monthly climatology
        climatology = climatology_part.groupby(['month'])['data'].mean().reset_index()
        climatology.rename(columns={'data': 'climatology'}, inplace=True)

        # join climatology to main time series
        self.df = pd.merge(self.df, climatology, on='month', how='left')

        # subtract climatology
        self.df['data'] = self.df['data'] - self.df['climatology']

        # update attributes
        self.metadata['climatology_start'] = baseline_start_year
        self.metadata['climatology_end'] = baseline_end_year
        self.metadata['actual'] = False

        self.update_history(
            f'Rebaselined to {baseline_start_year}-{baseline_end_year} for each month separately by calculating the '
            f'arithmetic mean of the data over the baseline period and subtracting the mean from all data values. '
            f'This is done for each month separately (Januarys, Februarys etc).'
        )

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

    def get_uncertainty(self, year: int, month: int) -> Optional[float]:
        """
        Get the current uncertainty for a particular year and month

        Parameters
        ----------
        year: int
            Year requested
        month: int
            Month requested/

        Returns
        -------
        float
            Value for that year and month or None if it doesn't exist
        """

        if 'uncertainty' not in self.df.columns:
            return None
        selection = self.df[(self.df['year'] == year) & (self.df['month'] == month)]
        if len(selection) == 0:
            out_value = None
        elif len(selection) == 1:
            out_value = selection['uncertainty'].values[0]
        else:
            raise KeyError(f"Selection is not unique {year} {month}")

        return out_value

    @log_activity
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
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']

        zero_value = -1 * self.get_value(year, month)
        self.update_history(f'Zeroed series on {month_names[month - 1]} {year} by subtracting the value for that '
                            f'month from all data values (see next entry)')
        self.add_offset(zero_value)
        self.manually_set_baseline(year, year)

    @log_activity
    def get_rank_from_year_and_month(self, year: int, month: int, versus_all_months=False) -> Optional[int]:
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

    def generate_dates(self, time_units: str) -> List[int]:
        """
        Given a string specifying the required time units (something like days since 1800-01-01 00:00:00.0),
        generate a list of times from the time series corresponding to those units.

        Parameters
        ----------
        time_units: str
            String specifying the units to use for generating the times e.g. "days since 1800-01-01 00:00:00.0"

        Returns
        -------
        List[int]
        """
        time_str = self.df.year.astype(str) + self.df.month.astype(str)
        self.df['time'] = pd.to_datetime(time_str, format='%Y%m')
        dates = cf.date2num(self.df['time'].tolist(),
                            units=time_units,
                            has_year_zero=False,
                            calendar='standard')
        return dates

    def write_csv(self, filename: Path, metadata_filename: Path = None):
        """
        Write the timeseries to a csv file with the specified filename. The format used for writing is given
        by the BADC CSV format. This has a lot of upfront metadata before the data section. An option for writing a
        metadata file is also provided.

        Parameters
        ----------
        filename: Path
            Path of the filename to write the data to
        metadata_filename: Path
            Path of the filename to write the metadata to

        Returns
        -------
        None
        """
        columns_to_write = ['time', 'year', 'month', 'data']
        monthly = True
        uncertainty = False
        irregular = False
        super().write_generic_csv(filename, metadata_filename,
                                  monthly, uncertainty, irregular,
                                  columns_to_write)

    def get_start_and_end_dates(self) -> Tuple[datetime, datetime]:
        """
        Get the first and last dates in the dataset

        Returns
        -------
        Tuple[datetime, datetime]
        """
        time_str = self.df.year.astype(int).astype(str) + self.df.month.astype(int).astype(str)
        self.df['time'] = pd.to_datetime(time_str, format='%Y%m')

        n_time = len(self.df['time'])

        start_date = self.df['time'][0]
        end_date = self.df['time'][n_time - 1]

        return start_date, end_date

    def get_year_axis(self):
        """
        Return a year axis

        Returns
        -------

        """
        year_axis = self.df['year'] + (self.df['month'] - 1) / 12.
        return year_axis

    def get_string_date_range(self) -> str:
        start_date, end_date = self.get_start_and_end_dates()
        date_range = f"{start_date.year}.{start_date.month:02d}-" \
                     f"{end_date.year}.{end_date.month:02d}"
        return date_range


class TimeSeriesAnnual(TimeSeries):

    def __init__(self, years: list, data: list, metadata=None, uncertainty: Optional[list] = None):
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

        super().__init__(metadata)

        dico = {'year': years, 'data': data}
        if uncertainty is not None:
            dico['uncertainty'] = uncertainty
        self.df = pd.DataFrame(dico)

    def __str__(self):
        out_str = f'TimeSeriesAnnual: {self.metadata["name"]}'
        return out_str

    @staticmethod
    def make_from_df(df: pd.DataFrame, metadata: CombinedMetadata):
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
        if 'uncertainty' in df.columns:
            uncertainty = df['uncertainty'].tolist()
            return TimeSeriesAnnual(years, data, metadata, uncertainty=uncertainty)
        else:
            return TimeSeriesAnnual(years, data, metadata)

    @log_activity
    def rebaseline(self, baseline_start_year: int, baseline_end_year: int):
        """
        Shift the time series to a new baseline, specified by start and end years (inclusive).

        Parameters
        ----------
        baseline_start_year : int
            First year of the climatology period
        baseline_end_year : int
            Last year of the climatology period

        Returns
        -------
            Action occurs in place.
        """
        # select part of series in climatology period
        climatology_part = self.df[(self.df['year'] >= baseline_start_year) & (self.df['year'] <= baseline_end_year)]

        # calculate monthly climatology
        climatology = climatology_part['data'].mean()

        # subtract climatology
        self.df['data'] = self.df['data'] - climatology

        # update attributes
        self.metadata['climatology_start'] = baseline_start_year
        self.metadata['climatology_end'] = baseline_end_year
        self.metadata['actual'] = False

        self.update_history(f'Rebaselined to {baseline_start_year}-{baseline_end_year} by subtracting the arithemtic '
                            f'mean for that period from all data values.')

    @log_activity
    def get_rank_from_year(self, year: int) -> Optional[int]:
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
    def get_value_from_year(self, year: int) -> Optional[float]:
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
    def get_uncertainty_from_year(self, year: int) -> Optional[float]:
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
        if 'uncertainty' not in self.df.columns:
            return None
        val = self.df[self.df['year'] == year]['uncertainty']
        if len(val) == 0:
            return None
        return val.iloc[0]

    @log_activity
    def get_year_from_rank(self, rank: int) -> List[int]:
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
        years = self.df[ranked['data'] == rank]['year'].tolist()
        return years

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
    def select_decade(self, end_year: int = 0):
        """
        Select every tenth year from the time series, the last digit of the years can
        be selected using the end_year keyword argument.

        Parameters
        ----------
        end_year: int
            Last digit of the years to be selected. e.g. set to 0 to pick 1850, 1860... 2010, 2020 etc.

        Returns
        -------
        TimeSeriesAnnual
        """
        self.df = self.df[self.df['year'] % 10 == end_year]
        self.df = self.df.reset_index()
        self.metadata['derived'] = True
        self.update_history(f'Selected years ending in {end_year}')
        return self

    def generate_dates(self, time_units: str) -> List[int]:
        """
        Given a string specifying the required time units (something like days since 1800-01-01 00:00:00.0),
        generate a list of times from the time series corresponding to those units.

        Parameters
        ----------
        time_units: str
            String specifying the units to use for generating the times e.g. "days since 1800-01-01 00:00:00.0"

        Returns
        -------
        List[int]
        """
        self.df['time'] = pd.to_datetime(self.df.year, format='%Y')
        dates = cf.date2num(self.df['time'].tolist(),
                            units=time_units,
                            has_year_zero=False,
                            calendar='standard')
        return dates

    def write_csv(self, filename, metadata_filename=None):
        """
        Write the timeseries to a csv file with the specified filename. The format used for writing is given
        by the BADC CSV format. This has a lot of upfront metadata before the data section. An option for writing a
        metadata file is also provided.

        Parameters
        ----------
        filename: Path
            Path of the filename to write the data to
        metadata_filename: Path
            Path of the filename to write the metadata to

        Returns
        -------
        None
        """
        monthly = False
        irregular = False
        uncertainty = False
        columns_to_write = ['time', 'year', 'data']
        if 'uncertainty' in self.df.columns:
            uncertainty = True
            columns_to_write = ['time', 'year', 'data', 'uncertainty']

        super().write_generic_csv(filename, metadata_filename,
                                  monthly, uncertainty, irregular, columns_to_write)

    def get_year_axis(self):
        """
        Return a year axis

        Returns
        -------

        """
        year_axis = self.df['year']
        return year_axis

    def get_string_date_range(self) -> str:
        start_year, end_year = self.get_first_and_last_year()
        date_range = f"{start_year}-{end_year}"
        return date_range

    def add_year(self, year: int, value: float, uncertainty: float = None) -> None:
        """
        Add a year of data.

        Parameters
        ----------
        year: int
            the year to be added
        value: float
            the data value to be added
        uncertainty:
            the uncertainty of the data value to be added (optional)

        Returns
        -------
        None
        """
        dict_to_add = {'year': year, 'data': value}
        if uncertainty is not None:
            dict_to_add['uncertainty'] = uncertainty
        self.df = self.df.append(dict_to_add, ignore_index=True)


def get_start_and_end_year(all_datasets: List[TimeSeriesAnnual]) -> (int, int):
    """

    Parameters
    ----------
    all_datasets: List[TimeSeriesAnnual]
        List of datasets from which to extract the earliest first year and latest final year.

    Returns
    -------
    (int, int)
    """
    if len(all_datasets) == 0:
        return None, None

    first_years = []
    last_years = []
    for ds in all_datasets:
        first_year, last_year = ds.get_first_and_last_year()
        first_years.append(first_year)
        last_years.append(last_year)

    return min(first_years), max(last_years)


def make_combined_series(all_datasets: List[TimeSeriesAnnual]) -> TimeSeriesAnnual:
    """
    Combine a list of datasets into a single TimeSeriesAnnual by taking the arithmetic mean
    of all available datasets for each year. Merges the metadata for all the input time series.

    Parameters
    ----------
    all_datasets: List[TimeSeriesAnnual]
        List of datasets to be combined
    Returns
    -------
    TimeSeriesAnnual
    """
    data_frames = []
    metadata = copy.deepcopy(all_datasets[0].metadata)
    metadata['name'] = 'Combined'
    metadata['display_name'] = 'Combined series'
    metadata['version'] = ''
    metadata['colour'] = '#ff0000'
    metadata['zpos'] = 0

    list_attributes = ['citation', 'citation_url', 'data_citation', 'url', 'filename', 'history']
    for i, ds in enumerate(all_datasets):
        data_frames.append(ds.df)
        if i > 0:
            for att in list_attributes:
                metadata[att].extend(ds.metadata[att])

    df_merged = reduce(lambda left, right: pd.merge(left, right, on=['year'], how='outer'), data_frames)

    columns = []
    for col in df_merged.columns:
        if 'data' in col:
            columns.append(col)

    df_merged['combined'] = df_merged[columns].mean(axis=1)
    df_merged['uncertainty'] = df_merged[columns].std(axis=1)

    df_merged['uncertainty'] = df_merged['uncertainty'] * 1.645
    df_merged['uncertainty'] = np.sqrt(df_merged['uncertainty'] ** 2 + 0.12 ** 2)

    df_merged = df_merged.drop(columns=columns)
    df_merged = df_merged.rename(columns={'combined': 'data'})

    return TimeSeriesAnnual.make_from_df(df_merged, metadata)


def get_list_of_unique_variables(all_datasets: List[TimeSeriesAnnual]) -> List[str]:
    """
    Given a list of datasets, get a list of the unique variable names

    Parameters
    ----------
    all_datasets: List[TimeSeriesAnnual]

    Returns
    -------
    List[str]
    """
    # get list of all unique variables
    variables = []
    for ds in all_datasets:
        if ds.metadata['variable'] not in variables:
            variables.append(ds.metadata['variable'])

    return variables


def superset_dataset_list(all_datasets: List[TimeSeriesAnnual], variables: List[str]) -> List[List[TimeSeriesAnnual]]:
    """
    Given a list of variables, create a list where each entry is a list of all data sets
    corresponding to the variable in that index position.

    Parameters
    ----------
    all_datasets: List[TimeSeriesAnnual]
        List of datasets
    variables: List[str]
        List of variable names
    Returns
    -------
    List[List[TimeSeriesAnnual]]
    """
    superset = []
    for _ in variables:
        superset.append([])

    for ds in all_datasets:
        i = variables.index(ds.metadata['variable'])
        superset[i].append(ds)

    return superset
