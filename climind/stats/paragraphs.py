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

import climind.plotters.plot_utils as pu
from typing import Union, List
from climind.data_types.timeseries import TimeSeriesMonthly, TimeSeriesAnnual

ordinal = lambda n: "%d%s" % (n, "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])


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


def dataset_name_list(all_datasets: List[Union[TimeSeriesMonthly, TimeSeriesAnnual]]) -> str:
    """
    Given a list of dataset, return a comma-and-and separated list of the names.

    Parameters
    ----------
    all_datasets: List[Union[TimeSeriesMonthly, TimeSeriesAnnual]]
        List of data sets whose names you want in a list

    Returns
    -------
    str
        A list of the dataset names separated by commas and, where appropriate, 'and'
    """
    names = []
    for ds in all_datasets:
        names.append(ds.metadata['display_name'])

    if len(names) == 1:
        name_list = f"{names[0]}"
    elif len(names) == 2:
        name_list = f"{names[0]} and {names[1]}"
    else:
        name_list = f"{', '.join(names[0:-1])}, and {names[-1]}"

    return name_list


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
    if len(all_datasets) == 0:
        raise RuntimeError("No datasets provided")

    min_rank, max_rank = pu.calculate_ranks(all_datasets, year)
    mean_anomaly, min_anomaly, max_anomaly = pu.calculate_values(all_datasets, year)

    units = fancy_html_units(all_datasets[0].metadata['units'])

    out_text = f'The year {year} was ranked {rank_ranges(min_rank, max_rank)} highest ' \
               f'on record. The mean value for {year} was ' \
               f'{mean_anomaly:.2f}{units} '

    if not all_datasets[0].metadata['actual']:
        clim_start = all_datasets[0].metadata['climatology_start']
        clim_end = all_datasets[0].metadata['climatology_end']
        out_text += f"relative to the {clim_start}-{clim_end} average "

    out_text += f'({min_anomaly:.2f}-{max_anomaly:.2f}{units} depending on the data set used). ' \
                f'{len(all_datasets)} data sets were used in this assessment: {dataset_name_list(all_datasets)}.'

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
    out_text = anomaly_and_rank(all_datasets, year)

    processed_data = []
    for ds in all_datasets:
        first_year, last_year = ds.get_first_and_last_year()
        if first_year <= 1961:
            ds.rebaseline(1961, 1990)
            processed_data.append(ds)

    min_rank, max_rank = pu.calculate_ranks(processed_data, year)
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

    min_march_rank, max_march_rank = pu.calculate_ranks(march, year, ascending=True)
    mean_march_value, min_march_value, max_march_value = pu.calculate_values(march, year)

    min_september_rank, max_september_rank = pu.calculate_ranks(september, year, ascending=True)
    mean_september_value, min_september_value, max_september_value = pu.calculate_values(september, year)

    out_text = f'Arctic sea ice extent in March {year} was between {min_march_value:.2f} and ' \
               f'{max_march_value:.2f}{units}. ' \
               f'This was {rank_ranges(min_march_rank, max_march_rank)} lowest extent on record. ' \
               f'In September the extent was between {min_september_value:.2f} and ' \
               f'{max_september_value:.2f}{units}. ' \
               f'This was {rank_ranges(min_september_rank, max_september_rank)} lowest extent on record. ' \
               f'Data sets used were: {dataset_name_list(all_datasets)}'

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

    out_text = f'This was the {ordinal(counter)} consecutive year of negative mass balance ' \
               f'since {last_positive + 1}. ' \
               f'Cumulative glacier loss since 1970 is {all_datasets[0].get_value_from_year(year):.1f}{units}.'

    return out_text


def co2_paragraph(all_datasets: List[TimeSeriesAnnual], year: int) -> str:
    """
    Generate a paragraph of some standard stats for greenhouse gases

    Parameters
    ----------
    all_datasets: List[TimeSeriesAnnual]
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

    tb = {}
    cl = {'co2': 277.3, 'ch4': 721.0, 'n2o': 270.9}

    last_year = 9999
    for ds in all_datasets:
        if ds.metadata['display_name'] == 'WDCGG':
            variable = ds.metadata['variable']
            first_year, last_year = ds.get_first_and_last_year()
            rank = ds.get_rank_from_year(last_year)
            value = ds.get_value_from_year(last_year)
            uncertainty = ds.get_uncertainty_from_year(last_year)
            tb[variable] = [rank, value, uncertainty]

    if last_year == 9999:
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
            if ds.metadata['display_name'] != 'WDCGG':
                rank = ds.get_rank_from_year(year)
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
        out_text = f"In {year}, {mhw_area:.1f}% of the ocean was affected by at least one marine heatwave. " \
                   f"The {ordinal(mhw_rank)} highest on record. " \
                   f"The highest ocean area affected in any year was {mhw_max_area:.1f}% in {mhw_max_year}. "
    if mcs_check:
        out_text = f"The area of the ocean affected by at least one marine cold spells was {mcs_area:.1f}%. " \
                   f"The {ordinal(mcs_rank)} highest on record. " \
                   f"The highest area affected in any year by marine cold spells was {mcs_max_area:.1f}% in {mcs_max_year}."

    if not mcs_check and not mhw_check:
        raise RuntimeError("One of MHW or MCS data not found in the data set list")

    return out_text
