#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2024 John Kennedy
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
import matplotlib.pyplot as plt
import numpy as np

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

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)

    ts_archive = archive.select({'variable': 'tas',
                                 'type': 'timeseries',
                                 'time_resolution': 'monthly',
                                 'name': ['HadCRUT5', 'GISTEMP', 'NOAA v6', 'JRA-55', 'ERA5', 'Berkeley Earth',
                                          'Kadow', 'JRA-3Q', 'NOAA v6', 'Calvert 2024', 'NOAA Interim']})

    oni_archive = archive.select({'variable': 'oni', 'type': 'timeseries', 'time_resolution': 'monthly'})

    list_of_nino_years = [1953, 1957, 1963, 1969, 1972, 1976, 1982, 1987, 1991, 1994, 1997, 2002, 2004, 2009, 2015,
                          2023]
    list_of_nino_years = [1963, 1969, 1972, 1976, 1982, 1987, 1991, 1994, 1997, 2002, 2004, 2009, 2015, 2023]
    list_of_nino_years = [1968, 1972, 1976, 1987, 1994, 1997, 2002, 2004, 2009, 2015, 2023]
    # list_of_nino_years = [1982, 1987, 1997, 2015, 2023]

    switcheroo = False

    saveit = np.zeros((36))
    ninosaveit = np.zeros((36))
    count = 0
    ninocount = 0

    fig, axs = plt.subplots(2, sharex=True)
    fig.set_size_inches(8, 8)

    for year in list_of_nino_years:
        print(year)
        all_datasets = ts_archive.read_datasets(data_dir)
        oni_datasets = oni_archive.read_datasets(data_dir)

        for ds in all_datasets:
            print(ds)
            ds.rebaseline(1981, 2010)
            ma = ds.lowess(120)
            ds = ds.select_year_range(year - 1, year + 1)
            ma = ma.select_year_range(year - 1, year + 1)

            color = 'dimgrey'
            linewidth = 1
            if year == 2023:
                color = 'darkred'
                linewidth = 3


            if switcheroo:
                axs[0].plot(ds.df.data - np.mean(ds.df.data[0:6]), color=color, linewidth=linewidth)
            else:
                axs[0].plot(ds.df.data - ma.df.data, color=color, linewidth=linewidth)

            if year != 2023:
                if switcheroo:
                    saveit = saveit + ds.df.data - np.mean(ds.df.data[0:6])
                else:
                    saveit = saveit + ds.df.data - ma.df.data
                count += 1

        for ds in oni_datasets:
            ds.rebaseline(1981, 2010)
            ma = ds.lowess(120)
            ds = ds.select_year_range(year - 1, year + 1)
            ma = ma.select_year_range(year - 1, year + 1)

            color = 'dimgrey'
            linewidth = 1
            if year == 2023:
                color = 'darkred'
                linewidth = 3

            if switcheroo:
                axs[1].plot(ds.df.data - np.mean(ds.df.data[0:6]), color=color, linewidth=linewidth)
            else:
                axs[1].plot(ds.df.data - ma.df.data, color=color, linewidth=linewidth)

            if year != 2023:
                if switcheroo:
                    ninosaveit = ninosaveit + ds.df.data - np.mean(ds.df.data[0:6])
                else:
                    ninosaveit = ninosaveit + ds.df.data - ma.df.data
                ninocount += 1


    axs[0].plot(saveit / count, color='darkgreen', linewidth=3)
    axs[1].plot(ninosaveit / ninocount, color='darkgreen', linewidth=3)

    plt.show()
