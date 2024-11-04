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
import calendar

import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt
import climind.stats.utils as utils

from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR

if __name__ == "__main__":

    final_year = 2024

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

    for month in range(1, 13):
        month_word = calendar.month_name[month]

        # Read in the whole archive then select the various subsets needed here
        archive = dm.DataArchive.from_directory(metadata_dir)

        ts_archive = archive.select({'variable': 'tas',
                                     'type': 'timeseries',
                                     'time_resolution': 'monthly',
                                     'name': ['HadCRUT5', 'GISTEMP', 'NOAA v6', 'ERA5', 'Berkeley Earth',
                                              'JRA-3Q']})
                                     # 'name': ['HadCRUT5', 'GISTEMP', 'NOAA v6', 'JRA-55', 'ERA5', 'Berkeley Earth',
                                     #          'Kadow', 'JRA-3Q', 'Calvert 2024', 'NOAA Interim']})

        long_ts_archive = archive.select({'variable': 'tas',
                                          'type': 'timeseries',
                                          'time_resolution': 'monthly',
                                          'name': ['HadCRUT5', 'NOAA v6', 'Berkeley Earth', 'Kadow', 'Calvert 2024',
                                                   'NOAA Interim']})

        sst_archive = archive.select({'variable': 'sst',
                                      'type': 'timeseries',
                                      'time_resolution': 'monthly'})

        lsat_archive = archive.select({'variable': 'lsat',
                                       'type': 'timeseries',
                                       'time_resolution': 'monthly'})

        all_datasets = ts_archive.read_datasets(data_dir)
        run_datasets = long_ts_archive.read_datasets(data_dir)
        lsat_datasets = lsat_archive.read_datasets(data_dir)
        sst_datasets = sst_archive.read_datasets(data_dir)

        owns = []
        runs = []
        run_all = []
        for ds in run_datasets:
            ds.rebaseline(1850, 1900)
            annual = ds.make_annual_by_selecting_month(month)
            owns.append(annual)
            ds = ds.running_mean(12)
            run_all.append(ds)
            annual = ds.make_annual_by_selecting_month(month)
            annual.select_year_range(1851, final_year)
            runs.append(annual)
            if annual.metadata['name'] == 'NOAA v6':
                print(ds.df.data.tolist())

        if month == 1:
            pt.neat_plot(figure_dir, run_all, '12_month_running_mean.png', f'Global mean temperature 12-month running mean')

        anns = []
        for ds in all_datasets:
            ds.rebaseline(1981, 2010)
            annual = ds.make_annual_by_selecting_month(month)
            annual.select_year_range(1850, final_year)
            anns.append(annual)

        lsat_anns = []
        for ds in lsat_datasets:
            ds.rebaseline(1981, 2010)
            annual = ds.make_annual_by_selecting_month(month)
            annual.select_year_range(1850, final_year)
            lsat_anns.append(annual)

        sst_anns = []
        for ds in sst_datasets:
            ds.rebaseline(1981, 2010)
            annual = ds.make_annual_by_selecting_month(month)
            annual.select_year_range(1850, final_year)
            sst_anns.append(annual)

        pt.neat_plot(figure_dir, lsat_anns, f'lsat_{month:02d}_only.png', f'Global mean LSAT for {month_word}')

        pt.neat_plot(figure_dir, sst_anns, f'sst_{month:02d}_only.png', f'Global mean SST for {month_word}')

        pt.neat_plot(figure_dir, anns, f'{month:02d}_only.png',
                     f'Global Mean Temperature for {month_word} ($\degree$C)')
        pt.records_plot(figure_dir, anns, f'{month:02d}_only_records.png',
                        f'Global Mean Temperature for {month_word} ($\degree$C)')
        pt.dark_plot(figure_dir, anns, f'dark_{month:02d}_only.png',
                     f'Global Mean Temperature for {month_word} ($\degree$C)')

        print()
        print(f"Single month ({month_word}) statistics")
        utils.run_the_numbers(anns, final_year, f'{month:02d}_only_stats', report_dir)
        utils.run_the_numbers(runs, final_year, f'running_{month:02d}_only_stats', report_dir)
        utils.run_the_numbers(owns, final_year, f'own_{month:02d}_only_stats', report_dir)

        utils.record_margins(anns, final_year, f'{month:02d}_record_margins', report_dir)
        utils.record_margins(sst_anns, final_year, f'{month:02d}_sst_record_margins', report_dir)
        utils.record_margins(lsat_anns, final_year, f'{month:02d}_lsat_record_margins', report_dir)

        if month == 1:
            all_datasets = ts_archive.read_datasets(data_dir)
            m = []
            for ds in all_datasets:
                ds.rebaseline(1981, 2010)
                ds.select_year_range(2014, 2024)
                m.append(ds)
            pt.monthly_plot(figure_dir, m, f'monthly.png', 'Monthly global mean')

            all_datasets = long_ts_archive.read_datasets(data_dir)
            m = []
            for ds in all_datasets:
                ds.rebaseline(1850, 1900)
                ds.select_year_range(2014, 2024)
                m.append(ds)
            pt.monthly_plot(figure_dir, m, f'own_monthly.png', 'Monthly global mean')
