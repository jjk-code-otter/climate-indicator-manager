import pandas as pd
import logging
import copy
import pkg_resources
from datetime import datetime
import cftime as cf
from climind.data_manager.metadata import DatasetMetadata, CombinedMetadata


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
        metadata : DatasetMetadata
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
    def make_annual(self):
        """
        Calculate a TimeSeriesAnnual from the TimeSeriesMonthly. The annual average is
        calculated from the mean of monthly values

        Returns
        -------
        TimeSeriesAnnual
            Return an annual time series
        """
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

    @log_activity
    def select_year_range(self, start_year: int, end_year: int):
        self.df = self.df[self.df['year'] >= start_year]
        self.df = self.df[self.df['year'] <= end_year]
        self.df = self.df.reset_index()
        return self

    @log_activity
    def get_rank_from_year_and_month(self, year: int, month: int, all=False) -> int:
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
        all : bool
            If set then

        Returns
        -------
        int
            Returns the rank of the specified year-month pair as compared to the same month in
            all other years. If "all" is set then returns rank of the anomaly for a particular year
            and month ranked against all other years and months.
        """
        if all:
            month_select = self.df
        else:
            month_select = self.df[self.df['month'] == month]
        ranked = month_select.rank(method='min', ascending=False)
        rank = ranked[month_select['year'] == year]['data']
        return int(rank.iloc[0])

    def write_csv(self, filename):

        now = datetime.today()
        climind_version = pkg_resources.get_distribution("climind").version
        time_units = 'days since 1800-01-01 00:00:00.0'

        self.df['time'] = pd.to_datetime(self.df.year.astype(str)+self.df.month.astype(str), format='%Y%m')
        dates = cf.date2num(self.df['time'].tolist(),
                            units=time_units,
                            has_year_zero=False,
                            calendar='standard')
        self.df['time'] = dates

        with open(filename, 'w') as f:
            f.write("Conventions,G,BADC-CSV,1\n")

            f.write("title,G,Global mean temperature\n")
            f.write(f"last_revised_date,G,{now.year}-{now.month:02d}-{now.day:02d}\n")
            f.write(f"date_valid,G,{now.year}-{now.month:02d}-{now.day:02d}\n")

            f.write(f"feature_type,G,area average\n")
            f.write(f"creator,G,WMO\n")
            f.write(f"source,G,Produced by climind version {climind_version}\n")
            f.write(f"observation_station,G,derived data\n")
            f.write(f"location,G,90.,-180.,-90.,180.\n")
            f.write(f"activity,G,WMO\n")

            for history_element in self.metadata['history']:
                f.write(f'history,G,"{history_element}"\n')

            for citation in self.metadata['citation']:
                f.write(f'reference,G,"{citation}"\n')

            f.write(f"rights,G,TBD\n")
            f.write(f"comments,G,Data produced by climind version {climind_version}\n")
            f.write(f"comments,G,Format description https://help.ceda.ac.uk/article/105-badc-csv")

            f.write(f"long_name,time,time,{time_units}\n")
            f.write(f"type,time,int\n")

            f.write(f"long_name,year,year,0\n")
            f.write(f"type,year,int\n")

            f.write(f"long_name,month,month,0\n")
            f.write(f"type,month,int\n")

            f.write(f"long_name,data,{self.metadata['variable']},K\n")
            f.write(f"type,data,float\n")

            f.write(f"coordinate_variable,time,t\n")

            f.write("data\n")
            f.write("time,year,month,data\n")
            f.write(self.df.to_csv(index=False,
                                   line_terminator='\n',
                                   float_format='%.4f',
                                   header=False,
                                   columns=['time', 'year', 'month', 'data']))
            f.write("end data\n")

        pass

class TimeSeriesAnnual:

    def __init__(self, years: list, data: list, metadata=None):
        """

        Parameters
        ----------
        years : list
            List of years
        data : list
            List of data values
        metadata : dict
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

    def write_csv(self, filename):

        now = datetime.today()
        climind_version = pkg_resources.get_distribution("climind").version
        time_units = 'days since 1800-01-01 00:00:00.0'

        self.df['time'] = pd.to_datetime(self.df.year, format='%Y')
        dates = cf.date2num(self.df['time'].tolist(),
                            units=time_units,
                            has_year_zero=False,
                            calendar='standard')
        self.df['time'] = dates

        with open(filename, 'w') as f:
            f.write("Conventions,G,BADC-CSV,1\n")

            f.write("title,G,Global mean temperature\n")
            f.write(f"last_revised_date,G,{now.year}-{now.month:02d}-{now.day:02d}\n")
            f.write(f"date_valid,G,{now.year}-{now.month:02d}-{now.day:02d}\n")

            f.write(f"feature_type,G,area average\n")
            f.write(f"creator,G,WMO\n")
            f.write(f"source,G,Produced by climind version {climind_version}\n")
            f.write(f"observation_station,G,derived data\n")
            f.write(f"location,G,90.,-180.,-90.,180.\n")
            f.write(f"activity,G,WMO\n")

            for history_element in self.metadata['history']:
                f.write(f'history,G,"{history_element}"\n')

            for citation in self.metadata['citation']:
                f.write(f'reference,G,"{citation}"\n')

            f.write(f"rights,G,TBD\n")
            f.write(f"comments,G,Data produced by climind version {climind_version}\n")
            f.write(f"comments,G,Format description https://help.ceda.ac.uk/article/105-badc-csv")


            f.write(f"long_name,time,time,{time_units}\n")
            f.write(f"type,time,int\n")

            f.write(f"long_name,year,year,0\n")
            f.write(f"type,year,int\n")

            f.write(f"long_name,data,{self.metadata['variable']},K\n")
            f.write(f"type,data,float\n")

            f.write(f"coordinate_variable,time,t\n")

            f.write("data\n")
            f.write("time,year,data\n")
            f.write(self.df.to_csv(index=False,
                                   line_terminator='\n',
                                   float_format='%.4f',
                                   header=False,
                                   columns=['time', 'year', 'data']))
            f.write("end data\n")

        pass
