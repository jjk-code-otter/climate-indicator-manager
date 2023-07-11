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

from pathlib import Path
import logging

import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt
import climind.stats.utils as utils

from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR

if __name__ == "__main__":

    final_year = 2023

    project_dir = DATA_DIR / "ManagedData"
    metadata_dir = METADATA_DIR

    data_dir = project_dir / "Data"
    figure_dir = project_dir / 'Figures'
    log_dir = project_dir / 'Logs'
    report_dir = project_dir / 'Reports'
    report_dir.mkdir(exist_ok=True)

    script = Path(__file__).stem
    logging.basicConfig(filename=log_dir / f'{script}.log',
                        filemode='w', level=logging.INFO)

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)

    # some global temperature data sets are annual only, others are monthly so need to read these separately
    ts_archive = archive.select({'variable': 'tas',
                                 'type': 'timeseries',
                                 'time_resolution': 'monthly'})

    nice_archive = archive.select({'variable': 'arctic_ice', 'type': 'timeseries', 'time_resolution': 'monthly'})
    sice_archive = archive.select({'variable': 'antarctic_ice', 'type': 'timeseries', 'time_resolution': 'monthly'})

    ohc_archive = archive.select({
        'variable': 'ohc',
        'type': 'timeseries',
        'time_resolution': 'annual',
        'name': 'GCOS'
    })

    sst_archive = archive.select({'variable': 'sst',
                                  'type': 'timeseries',
                                  'time_resolution': 'monthly'})

    lsat_archive = archive.select({'variable': 'lsat',
                                   'type': 'timeseries',
                                   'time_resolution': 'monthly'})

    all_datasets = ts_archive.read_datasets(data_dir)

    nice_datasets = nice_archive.read_datasets(data_dir)
    sice_datasets = sice_archive.read_datasets(data_dir)

    ohc_datasets = ohc_archive.read_datasets(data_dir)

    lsat_datasets = lsat_archive.read_datasets(data_dir)
    sst_datasets = sst_archive.read_datasets(data_dir)

    anns = []
    for ds in all_datasets:
        ds.rebaseline(1981, 2010)
        annual = ds.make_annual()
        annual.add_offset(0.69)
        annual.manually_set_baseline(1850, 1900)
        annual.select_year_range(1850, final_year)
        anns.append(annual)

    nice_anns_3 = []
    nice_anns_9 = []
    for ds in nice_datasets:
        ds.rebaseline(1991, 2020)
        annual = ds.make_annual_by_selecting_month(3)
        nice_anns_3.append(annual.running_mean(5))
        annual = ds.make_annual_by_selecting_month(9)
        nice_anns_9.append(annual.running_mean(5))

    sice_anns_2 = []
    sice_anns_9 = []
    for ds in sice_datasets:
        ds.rebaseline(1991, 2020)
        annual = ds.make_annual_by_selecting_month(2)
        sice_anns_2.append(annual.running_mean(5))
        annual = ds.make_annual_by_selecting_month(9)
        sice_anns_9.append(annual.running_mean(5))

    ohc_fives = []
    for ds in ohc_datasets:
        ds.add_year(2022, 66.9148993, 3.9471033)
        ohc_fives.append(ds.running_mean(5))

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

    fives = []
    for ds in anns:
        fives.append(ds.running_mean(5))

    pt.neat_plot(figure_dir, fives, 'five.png', r'5-year Global Mean Temperature Difference ($\degree$C)')

    pt.neat_plot(figure_dir, nice_anns_3, 'five_nice3.png', '5-year Arctic sea ice March')
    pt.neat_plot(figure_dir, nice_anns_9, 'five_nice9.png', '5-year Arctic sea ice September')
    pt.neat_plot(figure_dir, sice_anns_2, 'five_sice2.png', '5-year Antarctic sea ice February')
    pt.neat_plot(figure_dir, sice_anns_9, 'five_sice9.png', '5-year Antarctic sea ice September')

    pt.neat_plot(figure_dir, ohc_fives, 'five_ohc.png', '5-year Ocean Heat Content')

    print()
    print("Five-year stats")
    utils.run_the_numbers(fives, final_year, 'fiveyear_stats', report_dir)
