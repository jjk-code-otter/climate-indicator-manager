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

import numpy as np
import logging

import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt

from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR


def run_the_numbers(datasets: list, match_year: int):
    """
    Given a list of datasets calculate various statistics relating to ranking and values

    Parameters
    ----------
    datasets: list
        List of data sets
    match_year:
        Year of interest. Stats will be calculated up to the year of interest, but note that rankings will
        include years after the year of interest if it is not the most recent year in the data sets

    Returns
    -------

    """
    all_match_values = []
    all_match_ranks = []

    # Table summary of all data sets
    out_line = 'Year '
    for ds in datasets:
        out_line += f"{ds.dataset_metadata['name']:10.10} "
    print(out_line)
    for year in range(match_year - 12, match_year + 1):

        out_line = f'{year} '
        for ds in datasets:
            rank = ds.get_rank_from_year(year)
            value = ds.get_value_from_year(year)
            if rank is not None:
                out_line += f'{value:.2f} ({rank:2d})  '
            else:
                out_line += f' _.__ (__) '
        print(out_line)

    # data set by dataset summary
    for ds in datasets:
        for year in range(match_year - 12, match_year + 1):
            rank = ds.get_rank_from_year(year)
            value = ds.get_value_from_year(year)

            if rank is not None:
                #                print(f'{year} Rank:{rank} Value:{value:.3f}')
                if year == match_year:
                    all_match_values.append(value)
                    all_match_ranks.append(rank)

    sd = np.std(all_match_values) * 1.645
    sd = np.sqrt(sd ** 2 + (0.24 / 2) ** 2)

    print()
    print(f'Mean for {match_year}: {np.mean(all_match_values):.2f} +- {sd:.2f} degC '
          f'[{np.min(all_match_values):.2f}-{np.max(all_match_values):.2f}]')
    print(f'Rank between {np.min(all_match_ranks)} and {np.max(all_match_ranks)}')
    print(f'Based on {len(all_match_values)} data sets.')


if __name__ == "__main__":

    final_year = 2022

    project_dir = DATA_DIR / "ManagedData"
    metadata_dir = METADATA_DIR

    data_dir = project_dir / "Data"
    figure_dir = project_dir / 'Figures'
    log_dir = project_dir / 'Logs'

    logging.basicConfig(filename=log_dir / 'example.log',
                        filemode='w', level=logging.INFO)

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)

    # some global temperature data sets are annual only, others are monthly so need to read these separately
    ann_archive = archive.select({'variable': 'tas',
                                  'type': 'timeseries',
                                  'time_resolution': 'annual',
                                  'name': [  # 'NOAA Interim',
                                      'Kadow IPCC',
                                      # 'Berkeley IPCC',
                                      'NOAA Interim IPCC']})

    ts_archive = archive.select({'variable': 'tas',
                                 'type': 'timeseries',
                                 'time_resolution': 'monthly'})

    sst_archive = archive.select({'variable': 'sst',
                                  'type': 'timeseries',
                                  'time_resolution': 'monthly'})

    lsat_archive = archive.select({'variable': 'lsat',
                                   'type': 'timeseries',
                                   'time_resolution': 'monthly'})

    all_datasets = ts_archive.read_datasets(data_dir)
    ann_datasets = ann_archive.read_datasets(data_dir)

    lsat_datasets = lsat_archive.read_datasets(data_dir)
    sst_datasets = sst_archive.read_datasets(data_dir)

    anns = []
    for ds in all_datasets:
        ds.rebaseline(1981, 2010)
        annual = ds.make_annual()
        annual.add_offset(0.69)
        annual.select_year_range(1850, final_year)
        anns.append(annual)

    for ds in ann_datasets:
        ds.rebaseline(1981, 2010)
        ds.add_offset(0.69)
        ds.select_year_range(1850, final_year)
        anns.append(ds)

    lsat_anns = []
    for ds in lsat_datasets:
        ds.rebaseline(1981, 2010)
        annual = ds.make_annual()
        annual.select_year_range(1850, final_year)
        lsat_anns.append(annual)

    sst_anns = []
    for ds in sst_datasets:
        ds.rebaseline(1981, 2010)
        annual = ds.make_annual()
        annual.select_year_range(1850, final_year)
        sst_anns.append(annual)

    pt.neat_plot(figure_dir, lsat_anns, 'annual_lsat.png', 'Global mean LSAT')

    pt.neat_plot(figure_dir, sst_anns, 'annual_sst.png', 'Global mean SST')

    pt.neat_plot(figure_dir, anns, 'annual.png', r'Global Mean Temperature Difference ($\degree$C)')
    pt.dark_plot(figure_dir, anns, 'annualdark.png', r'Global Mean Temperature Difference ($\degree$C)')

    print()
    print("SINGLES")
    run_the_numbers(anns, match_year=final_year)

    tens = []
    dtens = []

    sst_tens = []
    sst_dtens = []

    lsat_tens = []
    lsat_dtens = []

    fives = []

    for ds in anns:
        tens.append(ds.running_mean(10))
        dtens.append(ds.running_mean(10).select_decade())
        fives.append(ds.running_mean(5))

    for ds in sst_anns:
        sst_tens.append(ds.running_mean(10))
        sst_dtens.append(ds.running_mean(10).select_decade())
    for ds in lsat_anns:
        lsat_tens.append(ds.running_mean(10))
        lsat_dtens.append(ds.running_mean(10).select_decade())

    pt.neat_plot(figure_dir, sst_tens, 'ten_sst.png', r'10-year Global Mean SST Difference ($\degree$C))')
    pt.neat_plot(figure_dir, lsat_tens, 'ten_lsat.png', r'10-year Global Mean LSAT Difference ($\degree$C))')
    pt.neat_plot(figure_dir, tens, 'ten.png', r'10-year Global Mean Temperature Difference ($\degree$C))')

    pt.decade_plot(figure_dir, sst_dtens, 'dten_sst.png',
                   r'10-year Global Mean SST Difference ($\degree$C))')
    pt.decade_plot(figure_dir, lsat_dtens, 'dten_lsat.png',
                   r'10-year Global Mean LSAT Difference ($\degree$C))')
    pt.decade_plot(figure_dir, dtens, 'dten.png',
                   r'10-year Global Mean Temperature Difference ($\degree$C))')

    pt.neat_plot(figure_dir, fives, 'five.png', r'5-year Global Mean Temperature Difference ($\degree$C)')

    #    print()
    #    print("FIVES")
    #    run_the_numbers(fives, match_year=2022)

    print()
    print("TENS")
    run_the_numbers(tens, match_year=final_year)
    run_the_numbers(tens, match_year=final_year)
