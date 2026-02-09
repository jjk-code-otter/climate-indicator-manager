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
import copy

import numpy as np
import climind.plotters.plot_utils as pu
from typing import Union, List
from climind.data_types.timeseries import TimeSeriesMonthly, TimeSeriesAnnual, \
    get_start_and_end_year, AveragesCollection

ordinal = lambda n: "%d%s" % (n, "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])


def get_last_month(in_str):
    year = in_str[0:4]
    year = int(year)
    month = in_str[5:7]
    month = int(month)
    return year, month


def rank_ranges(low: int, high: int) -> str:
    """
    Given an upper and lower limit on the rank, return a string which describes the range. e.g. 'the 2nd' or
    'between the 4th and 8th'.

    Parameters
    ----------
    low: int
        Lower of the two ranks.
    high: int
        Higher of the two ranks.

    Returns
    -------
    str
        Short string which describes the range. e.g. 'the 2nd' or 'between the 4th and 8th' or similar.
    """
    if low == high:
        return f"the {ordinal(low)}"
    elif low < high:
        return f"between the {ordinal(low)} and {ordinal(high)}"
    else:
        return f"between the {ordinal(high)} and {ordinal(low)}"


def nice_list(names):
    if len(names) == 1:
        name_list = f"{names[0]}"
    elif len(names) == 2:
        name_list = f"{names[0]} and {names[1]}"
    else:
        name_list = f"{', '.join(names[0:-1])}, and {names[-1]}"
    return name_list


def dataset_name_list(all_datasets: List[Union[TimeSeriesMonthly, TimeSeriesAnnual]], year: int = None) -> str:
    """
    Given a list of dataset, return a comma-and-and separated list of the names.

    Parameters
    ----------
    all_datasets: List[Union[TimeSeriesMonthly, TimeSeriesAnnual]]
        List of data sets whose names you want in a list
    year: int
        If year is specified, the name list will specify to what month data are available if the year is incomplete.

    Returns
    -------
    str
        A list of the dataset names separated by commas and, where appropriate, 'and'
    """
    str_month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov']
    names = []
    for ds in all_datasets:
        entry = ds.metadata['display_name']
        if year is not None and 'last_month' in ds.metadata:
            lyear, lmonth = get_last_month(ds.metadata['last_month'])
            if lmonth != 12 and year == lyear:
                entry += f" (to {str_month[lmonth - 1]} {year})"
        names.append(entry)

    return nice_list(names)


def fancy_html_units(units: str) -> str:
    """
    Convert plain text units into html fancy units, which use subscripts and special characters to render.

    Parameters
    ----------
    units: str
        Units to be rendered into fancy units

    Returns
    -------
    str
        Units in fancy html form, or unchanged.
    """
    equivalence = {
        "degC": "&deg;C",
        "millionkm2": "million km<sup>2</sup>",
        "ph": "pH",
        "mwe": "m w.e."
    }

    if units in equivalence:
        fancy = equivalence[units]
    else:
        fancy = units

    return fancy


def superlative(variable):
    lookup = {'tas': 'warmest'}
    if variable in lookup:
        return lookup[variable]

    return 'highest'


def basic_anomaly_and_rank(all_datasets: List[TimeSeriesAnnual], year: int) -> str:
    if len(all_datasets) == 0:
        raise RuntimeError("No datasets provided")

    first_year, last_year = get_start_and_end_year(all_datasets)

    variable = all_datasets[0].metadata['variable']
    super_text = superlative(variable)

    if year > last_year:
        out_text = f'The most recent available year is {last_year}. '
        year = last_year
    else:
        out_text = ''

    try:
        min_rank, max_rank = pu.calculate_ranks(all_datasets, year)
    except ValueError:
        return f"No data for {year}."

    mean_anomaly, min_anomaly, max_anomaly = pu.calculate_values(all_datasets, year)

    units = fancy_html_units(all_datasets[0].metadata['units'])

    out_text += f'The year {year} was ranked {rank_ranges(min_rank, max_rank)} {super_text} ' \
                f'on record. The mean value for {year} was ' \
                f'{mean_anomaly:.2f}{units} '

    if not all_datasets[0].metadata['actual']:
        clim_start = all_datasets[0].metadata['climatology_start']
        clim_end = all_datasets[0].metadata['climatology_end']
        out_text += f"relative to the {clim_start}-{clim_end} average "

    out_text += f'({min_anomaly:.2f}-{max_anomaly:.2f}{units} depending on the data set used). ' \
                f'{len(all_datasets)} data sets were used in this assessment: {dataset_name_list(all_datasets, year)}.'

    return out_text


def compare_to_highest_anomaly_and_rank(all_datasets: List[TimeSeriesAnnual], year: int) -> str:
    if len(all_datasets) == 0:
        raise RuntimeError("No datasets provided")

    first_year, last_year = get_start_and_end_year(all_datasets)

    variable = all_datasets[0].metadata['variable']
    super_text = superlative(variable)

    out_text = ''
    if year > last_year:
        out_text = f'The most recent available year is {last_year}. '
        year = last_year

    try:
        min_rank, max_rank = pu.calculate_ranks(all_datasets, year)
    except ValueError:
        return f"No data for {year}."
    units = fancy_html_units(all_datasets[0].metadata['units'])

    # If this is the highest year in all data sets, leave the text as is
    if max_rank == 1 and min_rank == 1:
        return out_text

    # if this is highest year in some data sets, but not all
    elif min_rank == 1 and max_rank != 1:
        highest_years, highest_values = pu.calculate_highest_year_and_values(all_datasets)
        highest_years = [str(x) for x in highest_years]
        out_text += f'{year} is joint {super_text} on record together with {nice_list(highest_years)}.'

    # if this is highest year in no data sets
    elif min_rank > 1:
        highest_years, highest_values = pu.calculate_highest_year_and_values(all_datasets)

        if len(highest_years) == 1:
            out_text += f'The {super_text} year on record was {highest_years[0]} with a value ' \
                        f'between {highest_values[0][0]:.2f} and {highest_values[0][1]:.2f} {units}.'
        if len(highest_years) > 1:
            highest_year_entry = []
            for i, high_year in enumerate(highest_years):
                highest_year_entry.append(f'{high_year} ({highest_values[i][0]:.2f}-{highest_values[i][1]:.2f}{units})')
            out_text += f'The {super_text} year on record was one of {nice_list(highest_year_entry)}.'

    return out_text


def global_anomaly_and_rank(all_datasets: List[TimeSeriesAnnual], year: int) -> str:
    """

    Parameters
    ----------
    all_datasets
    year

    Returns
    -------

    """
    if len(all_datasets) == 0:
        raise RuntimeError("No datasets provided")

    first_year, last_year = get_start_and_end_year(all_datasets)

    variable = all_datasets[0].metadata['variable']
    super_text = superlative(variable)

    if year > last_year:
        out_text = f'The most recent available year is {last_year}. '
        year = last_year
    else:
        out_text = ''

    try:
        min_rank, max_rank = pu.calculate_ranks(all_datasets, year)
    except ValueError:
        return f"No data for {year}."
    mean_anomaly, min_anomaly, max_anomaly = pu.calculate_values_ipcc_style(all_datasets, year)

    units = fancy_html_units(all_datasets[0].metadata['units'])

    out_text += f'The year {year} was ranked {rank_ranges(min_rank, max_rank)} {super_text} ' \
                f'on record. The anomaly for {year} was ' \
                f'{mean_anomaly:.2f} [{min_anomaly:.2f} to {max_anomaly:.2f}]{units} '

    if not all_datasets[0].metadata['actual']:
        clim_start = all_datasets[0].metadata['climatology_start']
        clim_end = all_datasets[0].metadata['climatology_end']
        out_text += f"relative to the {clim_start}-{clim_end} average "

    out_text += f'{len(all_datasets)} data sets were used in this assessment: {dataset_name_list(all_datasets, year)}.'

    return out_text


def anomaly_and_rank(all_datasets: List[TimeSeriesAnnual], year: int) -> str:
    """
    Write a short paragraph, returned as a string, which gives the rank range and data value for the chosen year,
    as well as saying how many data sets and which datasets were used.

    Parameters
    ----------
    all_datasets: List[TimeSeriesAnnual]
        List of datasets to be used to derive the ranks and values
    year: int
        Year for which the paragraph should be generated.
    Returns
    -------
    str

    """
    out_text = basic_anomaly_and_rank(all_datasets, year)
    out_text += compare_to_highest_anomaly_and_rank(all_datasets, year)
    out_text += "</p><p>"
    out_text += basic_anomaly_and_rank(all_datasets, year - 1)

    return out_text


def pre_industrial_estimate(all_datasets: List[TimeSeriesAnnual], _) -> str:
    """
    Write a short paragraph estimating the difference between the modern baseline and
    1850 to 1900.

    Parameters
    ----------
    all_datasets: List[TimeSeriesAnnual]
        List of all the data sets to be analysed

    Returns
    -------
    str
        Returns a paragraph of text stating an estimate of the pre-industrial temperature
        from these data sets
    """
    out_text = ''

    holder = AveragesCollection(all_datasets)

    the_mean = holder.best_estimate()
    the_range = holder.range()
    lower = holder.lower_range()
    upper = holder.upper_range()

    out_text += f"The mean: {the_mean:.2f} and the range {the_range:.2f} " \
                f"from {lower:.2f} to {upper:.2f}. Using {holder.count()} datasets."

    holder.expand = True
    out_text += f"Narrow expanded range is {holder.range():.2f} " \
                f"[{holder.lower_range():.2f} to {holder.upper_range():.2f}] or "

    holder.widest = True
    out_text += f"Wide expanded range is {holder.range():.2f} " \
                f"[{holder.lower_range():.2f} to {holder.upper_range():.2f}] or "

    return out_text


def anomaly_and_rank_plus_new_base(all_datasets: List[TimeSeriesAnnual], year: int) -> str:
    """
    Write a short paragraph, returned as a string, which gives the rank range and data value for the chosen year,
    as well as saying how many data sets and which datasets were used. Then it adds the anomalies relative to
    the 1961-1990 baseline, with information about the number of datasets.

    Parameters
    ----------
    all_datasets: List[TimeSeriesAnnual]
        List of datasets to be used to derive the ranks and values
    year: int
        Year for which the paragraph should be generated.
    Returns
    -------
    str

    """
    out_text = basic_anomaly_and_rank(all_datasets, year)

    processed_data = []
    for ds in all_datasets:
        first_year, last_year = ds.get_first_and_last_year()
        if first_year <= 1961:
            ds.rebaseline(1961, 1990)
            processed_data.append(ds)

    # min_rank, max_rank = pu.calculate_ranks(processed_data, year)
    mean_anomaly, min_anomaly, max_anomaly = pu.calculate_values(processed_data, year)
    units = fancy_html_units(all_datasets[0].metadata['units'])

    out_text += f' Relative to a 1961-1990 baseline, the mean value for {year} was ' \
                f'{mean_anomaly:.2f}{units} ' \
                f'({min_anomaly:.2f}-{max_anomaly:.2f}{units} depending on the data set used). ' \
                f'{len(processed_data)} data sets were used in the assessment relative to 1961-1990.'

    return out_text


def max_monthly_value(all_datasets: List[TimeSeriesMonthly], year: int) -> str:
    """
    Find the highest monthly data value within the chosen year and return a paragraph, as a string, which gives the
    value and rank for that month.

    Parameters
    ----------
    all_datasets: List[TimeSeriesMonthly]
        List of datasets to be used in the evaluation
    year: int
        Year to be analysed

    Returns
    -------
    str
        Short paragraph of text
    """
    if len(all_datasets) == 0:
        raise RuntimeError("No datasets provided")

    all_ranks = []
    all_ranks_months = []
    all_values = []
    for ds in all_datasets:
        min_rank = 9999
        min_rank_month = 99
        min_value = -99
        for month in range(1, 13):
            rank = ds.get_rank_from_year_and_month(year, month, versus_all_months=True)
            if rank is not None and rank < min_rank:
                min_rank = rank
                min_rank_month = month
                min_value = ds.get_value(year, month)
        if min_rank != 9999:
            all_ranks.append(min_rank)
            all_ranks_months.append(min_rank_month)
            all_values.append(min_value)

    units = fancy_html_units(all_datasets[0].metadata['units'])

    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    out_text = f'The monthly value for {month_names[all_ranks_months[0] - 1]} {year} was the ' \
               f'{ordinal(all_ranks[0])} highest on record at {all_values[0]:.1f}{units}.'

    return out_text


def arctic_ice_paragraph(all_datasets: List[TimeSeriesMonthly], year: int) -> str:
    """
    Generate a paragraph of some standard stats for the Arctic sea ice: rank and value for max and min extents in the
    year (March and September).

    Parameters
    ----------
    all_datasets: List[TimeSeriesMonthly]
        List of datasets on which the assessment will be based
    year: int
        Chosen year to focus on
    Returns
    -------
    str
        Paragraph of text
    """
    if len(all_datasets) == 0:
        raise RuntimeError('No datasets provided')

    march = []
    september = []
    for ds in all_datasets:
        march.append(ds.make_annual_by_selecting_month(3))
        september.append(ds.make_annual_by_selecting_month(9))

    units = fancy_html_units(all_datasets[0].metadata['units'])

    out_text = ''

    try:
        min_march_rank, max_march_rank = pu.calculate_ranks(march, year, ascending=True)
        mean_march_value, min_march_value, max_march_value = pu.calculate_values(march, year)

        out_text = f'Arctic sea ice extent in March {year} was between {min_march_value:.2f} and ' \
                   f'{max_march_value:.2f}{units}. ' \
                   f'This was {rank_ranges(min_march_rank, max_march_rank)} lowest extent on record. '
    except:
        out_text += f"March data are not yet available for {year}."

    try:
        min_september_rank, max_september_rank = pu.calculate_ranks(september, year, ascending=True)
        mean_september_value, min_september_value, max_september_value = pu.calculate_values(september, year)
        out_text += f'In September the extent was between {min_september_value:.2f} and ' \
                    f'{max_september_value:.2f}{units}. ' \
                    f'This was {rank_ranges(min_september_rank, max_september_rank)} lowest extent on record. ' \
                    f'Data sets used were: {dataset_name_list(all_datasets)}'
    except:
        out_text += f"September data are not yet available for {year}."

    return out_text


def antarctic_ice_paragraph(all_datasets: List[TimeSeriesMonthly], year: int) -> str:
    """
    Generate a paragraph of some standard stats for the Antarctic sea ice: rank and value for max and min extents in the
    year (Feb and September).

    Parameters
    ----------
    all_datasets: List[TimeSeriesMonthly]
        List of datasets on which the assessment will be based
    year: int
        Chosen year to focus on
    Returns
    -------
    str
        Paragraph of text
    """
    if len(all_datasets) == 0:
        raise RuntimeError('No datasets provided')

    march = []
    september = []
    for ds in all_datasets:
        march.append(ds.make_annual_by_selecting_month(2))
        september.append(ds.make_annual_by_selecting_month(9))

    units = fancy_html_units(all_datasets[0].metadata['units'])

    out_text = ''

    try:
        min_february_rank, max_february_rank = pu.calculate_ranks(march, year, ascending=True)
        mean_february_value, min_february_value, max_february_value = pu.calculate_values(march, year)
    except ValueError:
        out_text += 'No data available yet for February. '
    else:
        out_text += f'Antarctic sea ice extent in February {year} was between {min_february_value:.2f} and ' \
                    f'{max_february_value:.2f}{units}. ' \
                    f'This was {rank_ranges(min_february_rank, max_february_rank)} lowest extent on record. '

    try:
        min_september_rank, max_september_rank = pu.calculate_ranks(september, year, ascending=True)
        mean_september_value, min_september_value, max_september_value = pu.calculate_values(september, year)
    except ValueError:
        out_text += 'No data available yet for September. '
    else:
        out_text += f'In September the extent was between {min_september_value:.2f} and ' \
                    f'{max_september_value:.2f}{units}. ' \
                    f'This was {rank_ranges(min_september_rank, max_september_rank)} lowest extent on record. '

    out_text += f'Data sets used were: {dataset_name_list(all_datasets)}'

    return out_text


def glacier_paragraph(all_datasets: List[Union[TimeSeriesMonthly, TimeSeriesAnnual]], year: int) -> str:
    """
    Write the glacier paragraph
    Parameters
    ----------
    all_datasets: list[Union[TimeSeriesMonthly, TimeSeriesAnnual]]
        list of data sets to be processed
    year: int
        Year for which to do the evaluation

    Returns
    -------
    str
    """
    if len(all_datasets) == 0:
        raise RuntimeError('No datasets provided')

    first_year, last_year = get_start_and_end_year(all_datasets)

    if year > last_year:
        out_text = f'The most recent available year is {last_year}. '
        year = last_year
    else:
        out_text = ''

    counter = 0
    last_positive = -999
    for ds in all_datasets:
        first_year = ds.df['year'][0]
        for check_year in range(first_year + 1, year + 1):
            value1 = ds.get_value_from_year(check_year - 1)
            value2 = ds.get_value_from_year(check_year)
            diff = value2 - value1
            if diff >= 0.0:
                counter = 0
                last_positive = check_year
            else:
                counter += 1

    units = fancy_html_units(all_datasets[0].metadata['units'])

    out_text += f'This was the {ordinal(counter)} consecutive year of negative mass balance ' \
                f'since {last_positive + 1}. ' \
                f'Cumulative glacier loss since 1970 is {all_datasets[0].get_value_from_year(year):.1f}{units}.'

    return out_text


def co2_paragraph_update(all_datasets: List[TimeSeriesAnnual], year: int) -> str:
    return co2_paragraph(all_datasets, year, update=True)


def co2_paragraph(all_datasets: List[TimeSeriesAnnual], year: int, update=False) -> str:
    """
    Generate a paragraph of some standard stats for greenhouse gases

    Parameters
    ----------
    all_datasets: List[TimeSeriesAnnual]
        List of datasets on which the assessment will be based
    year: int
        Chosen year to focus on
    update: bool
        If set to True treat this as an update
    Returns
    -------
    str
        Paragraph of text
    """
    if len(all_datasets) == 0:
        raise RuntimeError('No datasets provided')

    tb = {}
    # pre-industrual values
    cl = {'co2': 278.3, 'ch4': 729.2, 'n2o': 270.1}

    last_year = -9999

    matcher = 'WDCGG'
    if update:
        matcher = 'WDCGG update'

    for ds in all_datasets:
        if ds.metadata['display_name'] == matcher:
            variable = ds.metadata['variable']
            first_year, last_year = ds.get_first_and_last_year()
            rank = ds.get_rank_from_year(last_year)
            value = ds.get_value_from_year(last_year)
            uncertainty = ds.get_uncertainty_from_year(last_year)
            tb[variable] = [rank, value, uncertainty]

    if last_year == -9999:
        raise RuntimeError("No greenhouse gas data sets found")

    if tb['co2'][0] == 1 and tb['ch4'][0] == 1 and tb['n2o'][0] == 1:
        out_text = f"In {last_year}, greenhouse gas mole fractions reached new highs, " \
                   f"with globally averaged surface mole fractions of " \
                   f"carbon dioxide (CO<sub>2</sub>) at {tb['co2'][1]:.1f} " \
                   f"&plusmn; {tb['co2'][2]:.1f} parts per million (ppm), " \
                   f"methane (CH<sub>4</sub>) at {tb['ch4'][1]:.0f} " \
                   f"&plusmn; {tb['ch4'][2]:.0f} parts per billion (ppb) and " \
                   f"nitrous oxide (N<sub>2</sub>O) at {tb['n2o'][1]:.1f} " \
                   f"&plusmn; {tb['n2o'][2]:.1f} ppb, respectively " \
                   f"{100. * tb['co2'][1] / cl['co2']:.0f}%, " \
                   f"{100. * tb['ch4'][1] / cl['ch4']:.0f}% and " \
                   f"{100. * tb['n2o'][1] / cl['n2o']:.0f}% of pre-industrial (1750) levels."

    else:
        out_text = f"In {last_year}, globally averaged greenhouse gas mole fractions were: " \
                   f"carbon dioxide (CO<sub>2</sub>) at {tb['co2'][1]:.1f} " \
                   f"&plusmn; {tb['co2'][2]:.1f} parts per million (ppm), " \
                   f"{tb['co2'][0]} highest on record, " \
                   f"methane (CH<sub>4</sub>) at {tb['ch4'][1]:.0f} " \
                   f"&plusmn; {tb['ch4'][2]:.0f} parts per billion (ppb)," \
                   f"{tb['ch4'][0]} highest on record, and " \
                   f"nitrous oxide (N<sub>2</sub>O) at {tb['n2o'][1]:.1f} " \
                   f"&plusmn; {tb['n2o'][2]:.1f} ppb, " \
                   f"{tb['n2o'][0]} highest on record, respectively " \
                   f"{100. * tb['co2'][1] / cl['co2']:.0f}%, " \
                   f"{100. * tb['ch4'][1] / cl['ch4']:.0f}% and " \
                   f"{100. * tb['n2o'][1] / cl['n2o']:.0f}% of pre-industrial (1750) levels"

    if last_year < year:

        all_highest = True
        upupup = True
        for ds in all_datasets:
            if ds.metadata['display_name'] != 'WDCGG' and ds.metadata['display_name'] != 'WDCGG CO2 update':
                rank = ds.get_rank_from_year(year)
                if rank is None:
                    upupup = False
                else:
                    value = ds.get_value_from_year(year) - ds.get_value_from_year(last_year)
                    if rank != 1:
                        all_highest = False
                    if value <= 0:
                        upupup = False

        if upupup and all_highest:
            out_text = out_text + f' Real-time data from specific locations, including Mauna Loa (Hawaii) and ' \
                                  f'Kennaook/Cape Grim (Tasmania) indicate that levels of ' \
                                  f'CO<sub>2</sub>, CH<sub>4</sub> and N<sub>2</sub>O continued to ' \
                                  f'increase in {year}.'

    return out_text


def marine_heatwave_and_cold_spell_paragraph(all_datasets: List[TimeSeriesAnnual], year: int) -> str:
    first_year, last_year = get_start_and_end_year(all_datasets)

    if last_year is not None and year > last_year:
        out_text = f'The most recent available year is {last_year}. '
        year = last_year
    else:
        out_text = ''

    mhw_area = None
    mhw_rank = None
    mhw_max_area = None
    mhw_max_year = None
    mcs_area = None
    mcs_rank = None
    mcs_max_area = None
    mcs_max_year = None

    mhw_check = False
    mcs_check = False

    for ds in all_datasets:
        # get the % area of marine heatwaves
        if ds.metadata['variable'] == 'mhw':
            mhw_check = True
            mhw_area = ds.get_value_from_year(year)
            mhw_rank = ds.get_rank_from_year(year)
            mhw_max_year = ds.get_year_from_rank(1)[0]
            mhw_max_area = ds.get_value_from_year(mhw_max_year)
        if ds.metadata['variable'] == 'mcs':
            mcs_check = True
            mcs_area = ds.get_value_from_year(year)
            mcs_rank = ds.get_rank_from_year(year)
            mcs_max_year = ds.get_year_from_rank(1)[0]
            mcs_max_area = ds.get_value_from_year(mcs_max_year)

    if mhw_check:
        out_text += f"In {year}, {mhw_area:.1f}% of the ocean was affected by at least one marine heatwave. " \
                    f"The {ordinal(mhw_rank)} highest on record. " \
                    f"The highest ocean area affected in any year was {mhw_max_area:.1f}% in {mhw_max_year}. "
    if mcs_check:
        out_text += f"The area of the ocean affected by at least one marine cold spells was {mcs_area:.1f}%. " \
                    f"The {ordinal(mcs_rank)} highest on record. " \
                    f"The highest area affected in any year by marine cold spells " \
                    f"was {mcs_max_area:.1f}% in {mcs_max_year}."

    if not mcs_check and not mhw_check:
        raise RuntimeError("One of MHW or MCS data not found in the data set list")

    return out_text


def greenland_ice_sheet_monthly(all_datasets: List[TimeSeriesMonthly], year: int) -> str:
    summary = []
    for ds in all_datasets:
        this_year = ds.get_value(year, 8)
        last_year = ds.get_value(year - 1, 8)
        if this_year is not None and last_year is not None:
            this_difference = this_year - last_year
            ds_copy = copy.deepcopy(ds)
            subset = ds_copy.select_year_range(2005, year - 1)
            comparison_set = []
            for y in range(2006, year):
                temp_this_year = subset.get_value(y, 8)
                temp_last_year = subset.get_value(y - 1, 8)
                # need to catch nones because of the gap in GRACE/GRACE-FO
                if temp_this_year is not None and temp_last_year is not None:
                    temp_difference = temp_this_year - temp_last_year
                    comparison_set.append(temp_difference)

            mean_change = np.mean(comparison_set)
            summary.append([ds.metadata['display_name'], this_difference, mean_change])

    out_text = ""
    for entry in summary:
        out_text += f"In the {entry[0]} data set, the mass change between September {year - 1} and " \
                    f"August {year} was {entry[1]:.2f}Gt, which is "
        if entry[2] > entry[1] and entry[1] < 0:
            out_text += f" a greater loss than the average for 2005-{year - 1} of {entry[2]:.2f}Gt. "
        elif entry[2] < entry[1] < 0:
            out_text += f" a smaller loss than the average for 2005-{year - 1} of {entry[2]:.2f}Gt. "
        elif entry[2] == entry[1] and entry[1] < 0:
            out_text += f" equal to the average loss for 2005-{year - 1}. "
        elif entry[1] > 0:
            pass

    return out_text


def ice_sheet_monthly_sm_grace_version(all_datasets: List[TimeSeriesMonthly], year: int) -> str:
    """
    This is the method used by Shawn Marshall to deal with the GRACE approx mid-month values.

    Parameters
    ----------
    all_datasets: List[TimeSeriesMonthly]
        List of datasets to be processed.
    year: int
        Year of focus
    Returns
    -------
    str
    """
    summary = []
    for ds in all_datasets:

        this_year_1 = ds.get_value(year, 8)
        this_year_2 = ds.get_value(year, 9)
        last_year_1 = ds.get_value(year - 1, 8)
        last_year_2 = ds.get_value(year - 1, 9)

        if (
                this_year_1 is not None and
                last_year_1 is not None and
                this_year_2 is not None and
                last_year_2 is not None
        ):

            this_year = (this_year_1 + this_year_2) / 2
            last_year = (last_year_1 + last_year_2) / 2

            this_difference = this_year - last_year
            ds_copy = copy.deepcopy(ds)
            subset = ds_copy.select_year_range(2005, year - 1)
            comparison_set = []
            for y in range(2006, year):
                # Average the august and september values
                temp_this_year = (subset.get_value(y, 8) + subset.get_value(y, 9)) / 2
                temp_last_year = (subset.get_value(y - 1, 8) + subset.get_value(y - 1, 9)) / 2
                # need to catch nones because of the gap in GRACE/GRACE-FO
                if temp_this_year is not None and temp_last_year is not None:
                    temp_difference = temp_this_year - temp_last_year
                    comparison_set.append(temp_difference)

            mean_change = np.mean(comparison_set)
            summary.append([ds.metadata['display_name'], this_difference, mean_change])

    out_text = ""
    for entry in summary:
        out_text += f"In the {entry[0]} data set of {ds.metadata['long_name']}, the mass change between September {year - 1} and " \
                    f"August {year} was {entry[1]:.0f}Gt."

    return out_text


def greenland_ice_sheet(all_datasets: List[TimeSeriesAnnual], year: int) -> str:
    summary = []
    for ds in all_datasets:
        this_year = ds.get_value_from_year(year)
        last_year = ds.get_value_from_year(year - 1)
        if this_year is not None and last_year is not None:
            this_difference = this_year - last_year
            ds_copy = copy.deepcopy(ds)
            subset = ds_copy.select_year_range(2005, year - 1)
            comparison_set = []
            for y in range(2006, year):
                temp_this_year = subset.get_value_from_year(y)
                temp_last_year = subset.get_value_from_year(y - 1)
                # need to catch nones because of the gap in GRACE/GRACE-FO
                if temp_this_year is not None and temp_last_year is not None:
                    temp_difference = temp_this_year - temp_last_year
                    comparison_set.append(temp_difference)

            mean_change = np.mean(comparison_set)
            summary.append([ds.metadata['display_name'], this_difference, mean_change])

    out_text = f"There are {len(summary)} data sets of Greenland mass balance. "
    for entry in summary:
        out_text += f"In the {entry[0]} data set, the mass change between {year - 1} and " \
                    f"{year} was {entry[1]:.2f}Gt, which is "
        if entry[2] > entry[1] and entry[1] < 0:
            out_text += f" a greater loss than the average for 2005-{year - 1} of {entry[2]:.2f}Gt/year. "
        elif entry[2] < entry[1] < 0:
            out_text += f" a smaller loss than the average for 2005-{year - 1} of {entry[2]:.2f}Gt/year. "
        elif entry[1] > 0:
            out_text += f" {year} saw an increase in the mass of Greenland ice."

    return out_text


def long_term_trend_paragraph(all_datasets: List[TimeSeriesMonthly], year: int) -> str:
    all_trends = []
    all_initial_trends = []
    all_recent_trends = []
    all_semi_recent_trends = []

    out_text = ""
    for ds in all_datasets:
        times = ds.df['year'] + (ds.df['month'] - 1) / 12.
        data = ds.df['data']

        result = np.polyfit(times, data, 1)
        trend1 = result[0]
        all_trends.append(trend1)

        selection = times < 2003
        result = np.polyfit(times[selection], data[selection], 1)
        trend2 = result[0]
        all_initial_trends.append(trend2)

        selection = times >= (year - 9)
        result = np.polyfit(times[selection], data[selection], 1)
        trend3 = result[0]
        all_recent_trends.append(trend3)

        selection = (times >= 2015) & (times < 2025)
        result = np.polyfit(times[selection], data[selection], 1)
        trend4 = result[0]
        all_semi_recent_trends.append(trend4)

        first_year, last_year = ds.get_first_and_last_year()

        units = fancy_html_units(ds.metadata['units'])
        out_text += (f"The rate of change in the {ds.metadata['display_name']} data set is {trend1:.2f} {units}/yr "
                     f"between {first_year} and {last_year}. The rate of change in the past decade {year - 9}-{year} is "
                     f"{trend3:.2f} {units}/yr which is higher than the trend for the first decade of the satellite "
                     f"record 1993-2002 which was {trend2:.2f} {units}/yr. The trend for 2015-2014 was {trend4:.2f} "
                     f"{units}/yr.")

    return out_text


def precip_paragraph(_, year) -> str:
    if year == 2023:
        out_text = "Accumulated precipitation totals in 2023 were above the long-term average in East and Central Asia "
        out_text += "and parts of northern Asia; the western Indian summer monsoon region; "
        out_text += "parts of the Maritime Continent; northern New Zealand; parts of West, Central, "
        out_text += "Southern and East Africa; West, Central and Southeast Europe; southern Scandinavia; "
        out_text += "the western Middle East; northwest, southwest and southeast North America; Greater Antilles; "
        out_text += "and parts of southeast South America."

        out_text += "Regions with a marked rainfall deficit included: southeast South America, the Amazon Basin, and "
        out_text += "much of Central America; southern Canada; the western Mediterranean region and Southwest Europe; "
        out_text += "parts of northwest, central, and southern Africa; parts of central Asia; "
        out_text += "the eastern Indian Monsoon region; parts of southeast Asia and the Maritime Continent; "
        out_text += "southwest and coastal north Australia; and many of the Pacific Islands."

        out_text += "The onset of the West African Monsoon was around normal. The start of the Gu rain season "
        out_text += "(April to June) in the Greater Horn of Africa brought unusually large rainfalls "
        out_text += "amounts in some areas."
    elif year == 2024:
        out_text = 'Nothing to see here yet.'
    elif year == 2025:
        out_text = 'Nothing to see here yet'

    return out_text


def convert_to_percentages(ts, min_screen=90, max_screen=40):
    n_years = len(ts.df.data)

    years = np.array(ts.get_year_axis())
    datas = np.array(ts.df.data)

    year0 = years[0]
    yearz = years[-1]

    max_data = np.max(datas)
    min_data = np.min(datas)

    outstr = '100,0 0, 0'
    for i in range(n_years):
        year = 100 * (years[i] - year0) / (yearz - year0)
        data = min_screen + (max_screen - min_screen) * (datas[i] - min_data) / (max_data - min_data)

        outstr += f' {year:.2f}, {data:.2f}'

    return outstr


def svg_background(all_datasets, year):
    out_text = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" preserveAspectRatio="none" style="background-color:var(--dashblue);">'
    out_text += '<polygon points="' + convert_to_percentages(
        all_datasets[0]) + '"  style="fill:var(--dashorange);stroke:var(--dashwhite);stroke-width:0" />'
    out_text += '</svg>'
    return out_text
