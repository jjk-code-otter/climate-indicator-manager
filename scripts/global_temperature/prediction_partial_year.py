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
from pathlib import Path
import logging
import numpy as np

import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt
import climind.stats.utils as utils

from climind.data_types.timeseries import make_combined_series

from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR

if __name__ == "__main__":

    final_year = 2024
    holdouts = ['HadCRUT5']  # Datasets which haven't been updated from month 1 to month 2 yet
    month2 = 12
    month1 = 11

    project_dir = DATA_DIR / "ManagedData"
    metadata_dir = METADATA_DIR

    data_dir = project_dir / "Data"
    fdata_dir = project_dir / "Formatted_Data"
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
                                 'name': ['HadCRUT5', 'NOAA v6', 'GISTEMP', 'ERA5', 'JRA-3Q', 'Berkeley Earth'],
                                 'time_resolution': 'monthly'})

    all_datasets = ts_archive.read_datasets(data_dir)
    to_august_datasets = []
    for ds in all_datasets:
        ds.rebaseline(1981, 2010)
        ds = ds.running_mean(month1)
        annual = ds.make_annual_by_selecting_month(month1)
        annual.add_offset(0.69)
        to_august_datasets.append(annual)

    all_datasets = ts_archive.read_datasets(data_dir)
    to_september_datasets = []
    for ds in all_datasets:
        ds.rebaseline(1981, 2010)
        ds = ds.running_mean(month2)
        annual = ds.make_annual_by_selecting_month(month2)
        annual.add_offset(0.69)
        to_september_datasets.append(annual)

    all_datasets = ts_archive.read_datasets(data_dir)
    to_part_datasets = []
    for ds in all_datasets:
        ds.rebaseline(1981, 2010)
        if ds.metadata['name'] in holdouts:
            ds = ds.running_mean(month1)
            annual = ds.make_annual_by_selecting_month(month1)
        else:
            ds = ds.running_mean(month2)
            annual = ds.make_annual_by_selecting_month(month2)
        annual.add_offset(0.69)
        to_part_datasets.append(annual)

    utils.run_the_numbers(to_september_datasets, final_year, 'to_september_stats', report_dir)
    utils.run_the_numbers(to_part_datasets, final_year, 'to_part_stats', report_dir)

    taxis = []
    ts_diff = []
    countall = 0
    countmismatch = 0
    count_pos = 0
    count_neg = 0

    fixed_taxis = []
    fixed_ts_diff = []
    fixed_countall = 0
    fixed_countmismatch = 0
    fixed_count_pos = 0
    fixed_count_neg = 0

    for year in range(1950, final_year):

        collect_aug = {}
        for ds in to_august_datasets:
            if ds.metadata['name'] not in holdouts:
                collect_aug[ds.metadata['name']] = ds.get_value_from_year(year)

        collect_part = []
        for ds in to_part_datasets:
            collect_part.append(ds.get_value_from_year(year))
        collect_part = np.mean(collect_part)

        collect_all = []
        for ds in to_september_datasets:
            if ds.metadata['name'] not in holdouts:
                collect_aug[ds.metadata['name']] = collect_aug[ds.metadata['name']] - ds.get_value_from_year(year)
            collect_all.append(ds.get_value_from_year(year))
        collect_all = np.mean(collect_all)

        offset = 0.0
        offset_count = 0
        for key in collect_aug:
            offset += collect_aug[key]
            offset_count += 1
        offset /= offset_count

        fixed_part = []
        for ds in to_part_datasets:
            if ds.metadata['name'] in holdouts:
                fixed_part.append(ds.get_value_from_year(year) - offset)
            else:
                fixed_part.append(ds.get_value_from_year(year))
        fixed_part = np.mean(fixed_part)

        ts_diff.append(collect_part - collect_all)
        taxis.append(year)

        if collect_all > collect_part:
            count_pos += 1
        elif collect_all < collect_part:
            count_neg += 1

        strdiff = (f"{collect_part:.2f}" != f"{collect_all:.2f}")

        if strdiff:
            countmismatch += 1
            print(f"{year} {collect_part:.2f} {collect_all:.2f}  {collect_part:.4f} {collect_all:.4f} XXXX")
        else:
            print(f"{year} {collect_part:.2f} {collect_all:.2f}  {collect_part:.4f} {collect_all:.4f}")

        countall += 1

        fixed_ts_diff.append(fixed_part - collect_all)
        fixed_taxis.append(year)

        if collect_all > fixed_part:
            fixed_count_pos += 1
        elif collect_all < fixed_part:
            fixed_count_neg += 1

        strdiff = (f"{fixed_part:.2f}" != f"{collect_all:.2f}")

        if strdiff:
            fixed_countmismatch += 1
            print(f"{year} {fixed_part:.2f} {collect_all:.2f}  {fixed_part:.4f} {collect_all:.4f} XXXX")
        else:
            print(f"{year} {fixed_part:.2f} {collect_all:.2f}  {fixed_part:.4f} {collect_all:.4f}")

        fixed_countall += 1

    print(f"{countmismatch} out of {countall} = {100 * countmismatch / countall}%")
    print(f"positive {count_pos} {100 * count_pos / countall}%, negative {count_neg} {100 * count_neg / countall}%")
    print(f"Mean difference = {np.mean(ts_diff)}")
    print(f"Std difference = {np.std(ts_diff)}")

    print(f"{fixed_countmismatch} out of {fixed_countall} = {100 * fixed_countmismatch / fixed_countall}%")
    print(
        f"positive {fixed_count_pos} {100 * fixed_count_pos / fixed_countall}%, negative {fixed_count_neg} {100 * fixed_count_neg / fixed_countall}%")
    print(f"Mean difference = {np.mean(fixed_ts_diff)}")
    print(f"Std difference = {np.std(fixed_ts_diff)}")

    collect_aug = {}
    for ds in to_august_datasets:
        if ds.metadata['name'] not in holdouts:
            collect_aug[ds.metadata['name']] = ds.get_value_from_year(final_year)
    collect_all = []
    for ds in to_september_datasets:
        if ds.metadata['name'] not in holdouts:
            collect_aug[ds.metadata['name']] = collect_aug[ds.metadata['name']] - ds.get_value_from_year(final_year)
    offset = 0.0
    offset_count = 0
    for key in collect_aug:
        offset += collect_aug[key]
        offset_count += 1
    offset /= offset_count

    collect_fcst = []
    for ds in to_august_datasets:
        if ds.metadata['name'] in holdouts:
            collect_fcst.append(ds.get_value_from_year(final_year) - offset)
    for ds in to_september_datasets:
        if ds.metadata['name'] not in holdouts:
            collect_fcst.append(ds.get_value_from_year(final_year))

    print(f"{np.mean(collect_fcst)}")
    print(f"Offset {offset}")

    import matplotlib.pyplot as plt

    plt.plot(taxis, ts_diff)
    plt.plot(fixed_taxis, fixed_ts_diff)
    plt.savefig(figure_dir / 'differences.png')
    plt.close()
