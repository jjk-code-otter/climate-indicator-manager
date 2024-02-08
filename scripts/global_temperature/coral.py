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

import copy
from pathlib import Path
import logging

import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt
import climind.stats.utils as utils

from climind.data_types.timeseries import make_combined_series

from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR

if __name__ == "__main__":
    final_year = 2010

    project_dir = DATA_DIR / "ManagedData"
    metadata_dir = METADATA_DIR

    data_dir = project_dir / "Data"
    fdata_dir = project_dir / "Formatted_Data"
    figure_dir = project_dir / 'Figures'
    log_dir = project_dir / 'Logs'
    report_dir = project_dir / 'Reports'
    report_dir.mkdir(exist_ok=True)

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)

    # some global temperature data sets are annual only, others are monthly so need to read these separately
    sst_archive = archive.select({
        'variable': 'sst',
        'type': 'timeseries',
        'time_resolution': 'annual',
        'name': ['HadSST4', 'ERSST']
    })

    sst = sst_archive.read_datasets(data_dir)

    coral_archive = archive.select({'variable': 'coral',
                                    'type': 'timeseries',
                                    'time_resolution': 'annual'})

    coral = coral_archive.read_datasets(data_dir)

    pt.neat_plot(figure_dir, sst, 'dink.png', 'SST')
    pt.neat_plot(figure_dir, coral, 'dink2.png', 'Coral')

    calibration0 = 1964

    coral[0].select_year_range(calibration0, 2010)

    matching = []
    for ds in sst:
        ds.rebaseline(1961, 1990)
        ds.select_year_range(calibration0, 2012)

        match = []
        for y in coral[0].df.year:
            if ds.get_value_from_year(y) is not None:
                match.append(ds.get_value_from_year(y))

        matching.append(match)

    import matplotlib.pyplot as plt

    short_years = coral[0].df.year

    plt.plot(short_years, matching[0])
    plt.plot(short_years, matching[1])
    plt.plot(short_years, coral[0].df.data)
    plt.show()

    import numpy as np
    from sklearn.linear_model import LinearRegression

    new_sst = sst_archive.read_datasets(data_dir)
    for ds in new_sst:
        ds.rebaseline(1961, 1990)

    for ijk in range(2):
        X = np.array(coral[0].df.year).reshape(-1, 1)
        Y = np.array(matching[ijk])

        model = LinearRegression()
        model.fit(X, Y)

        y_pred = model.predict(X)

        X = np.array(coral[0].df.data).reshape(-1, 1)

        model2 = LinearRegression()
        model2.fit(X, y_pred)

        coral_new = coral_archive.read_datasets(data_dir)
        coral_new[0].df.data = coral_new[0].df.data * model2.coef_[0] + model2.intercept_

        new_sst.append(coral_new[0])

    pt.neat_plot(figure_dir, new_sst, 'dink3.png', 'SST and coral')

    print()
    print()
