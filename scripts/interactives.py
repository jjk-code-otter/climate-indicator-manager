#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2025 John Kennedy
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
import os

import pandas as pd
import datawrapper as dw

import climind.data_manager.processing as dm
from climind.data_types.timeseries import make_combined_series, equalise_datasets
from climind.config.config import DATA_DIR

if __name__ == "__main__":

    final_year = 2025

    project_dir = DATA_DIR / "ManagedData"
    ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    METADATA_DIR = ROOT_DIR.resolve() / "climind" / "metadata_files"
    metadata_dir = METADATA_DIR

    data_dir = project_dir / "Data"

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)

    gmst = False
    co2 = False
    ohc = False
    sea_level = False
    sea_ice = False
    glaciers = True

    if gmst:
        # some global temperature data sets are annual only, others are monthly so need to read these separately
        ts_archive = archive.select({'variable': 'tas',
                                     'type': 'timeseries',
                                     'name': ['NOAA v6', 'GISTEMP', 'ERA5', 'JRA-3Q', 'Berkeley Earth Hires', 'HadCRUT5'],
                                     'time_resolution': 'monthly'})

        all_datasets = ts_archive.read_datasets(data_dir)

        all_annual_datasets = []
        for ds in all_datasets:
            ds.rebaseline(1981, 2010)
            annual = ds.make_annual()
            annual.add_offset(0.69)
            annual.manually_set_baseline(1850, 1900)
            annual.select_year_range(1850, final_year)
            all_annual_datasets.append(annual)

        df = equalise_datasets(all_annual_datasets)

        chart = dw.LineChart(
            title='Global mean temperature 1850-2025',
            source_name='WMO',
            data=df,
            custom_range_y=[-0.3, 1.63],
            y_grid_format='0.0',
            tooltip_number_format="00.00",
            tooltip_x_format="YYYY",
        )

        chart.create().publish()
        iframe_code = chart.get_iframe_code()
        png_url = chart.get_png_url()

        print(chart.chart_id)
        print(iframe_code)
        print(png_url)

    if co2:
        # some global temperature data sets are annual only, others are monthly so need to read these separately
        ts_archive = archive.select({'variable': 'co2',
                                     'type': 'timeseries',
                                     'name': ['WDCGG'],
                                     'time_resolution': 'annual'})

        all_datasets = ts_archive.read_datasets(data_dir)

        df = equalise_datasets(all_datasets)

        chart = dw.LineChart(
            title='Atmospheric carbon dioxide concentration 1984-2024',
            source_name='WMO',
            data=df,
            custom_range_y=[340, 430],
            y_grid_format='0',
            tooltip_number_format="000.00",
            tooltip_x_format="YYYY",
            plot_height_ratio=0.5,
            plot_height_mode='ratio',
        )

        chart.create().publish()
        iframe_code = chart.get_iframe_code()
        png_url = chart.get_png_url()

        print(chart.chart_id)
        print(iframe_code)
        print(png_url)

    if ohc:
        # some global temperature data sets are annual only, others are monthly so need to read these separately
        ts_archive = archive.select({'variable': 'ohc2k',
                                     'type': 'timeseries',
                                     'name': ["Copernicus_OHC", "Miniere", "Cheng TEMP"],
                                     'time_resolution': 'annual'})

        all_datasets = ts_archive.read_datasets(data_dir)

        df = equalise_datasets(all_datasets)

        chart = dw.LineChart(
            title='Ocean heat content 0-2000m',
            source_name='WMO',
            data=df,
            custom_range_y=[-325, 200],
            y_grid_format='0',
            tooltip_number_format="000.00",
            tooltip_x_format="YYYY",
            plot_height_ratio=0.5,
            plot_height_mode='ratio',
        )

        chart.create().publish()
        iframe_code = chart.get_iframe_code()
        png_url = chart.get_png_url()

        print(chart.chart_id)
        print(iframe_code)
        print(png_url)

    if sea_level:
        # some global temperature data sets are annual only, others are monthly so need to read these separately
        ts_archive = archive.select({'variable': 'sealevel',
                                     'type': 'timeseries',
                                     'name': ["AVISO ftp"],
                                     'time_resolution': 'monthly'})

        all_datasets = ts_archive.read_datasets(data_dir)

        df = all_datasets[0].df

        df['year'] = df['date']
        df = df.drop(columns=['date', 'month', 'day', 'uncertainty'])
        df = df.rename(columns={'data': 'AVISO'})

        chart = dw.LineChart(
            title='Global mean sea level change 1993-2025',
            source_name='WMO',
            data=df,
            custom_range_y=[-10, 120],
            y_grid_format='0',
            tooltip_number_format="000.00",
            tooltip_x_format="YYYY",
            plot_height_ratio=0.5,
            plot_height_mode='ratio',
        )

        chart.create().publish()
        iframe_code = chart.get_iframe_code()
        png_url = chart.get_png_url()

        print(chart.chart_id)
        print(iframe_code)
        print(png_url)

    if sea_ice:
        # some global temperature data sets are annual only, others are monthly so need to read these separately
        ts_archive = archive.select({'variable': 'arctic_ice',
                                     'type': 'timeseries',
                                     'name': ["JAXA NH", "NSIDC v4", "OSI SAF v2p3"],
                                     'time_resolution': 'monthly'})

        all_datasets = ts_archive.read_datasets(data_dir)

        for ds in all_datasets:
            ds.rebaseline(1991, 2020)

        df = equalise_datasets(all_datasets)

        df['year'] = df['time']
        df = df.drop(columns=['time', 'month'])

        chart = dw.LineChart(
            title='Arctic sea-ice extent 1978-2025',
            source_name='WMO',
            data=df,
            custom_range_y=[-2.5, 2.5],
            y_grid_format='0',
            tooltip_number_format="000.00",
            tooltip_x_format="YYYY",
            plot_height_ratio=0.5,
            plot_height_mode='ratio',
        )

        chart.create().publish()
        iframe_code = chart.get_iframe_code()
        png_url = chart.get_png_url()

        print(chart.chart_id)
        print(iframe_code)
        print(png_url)

    if glaciers:
        # some global temperature data sets are annual only, others are monthly so need to read these separately
        ts_archive = archive.select({'variable': 'glacier',
                                     'type': 'timeseries',
                                     'time_resolution': 'annual'})

        all_datasets = ts_archive.read_datasets(data_dir)

        df = all_datasets[0].df
        df = df.rename(columns={'data': 'WGMS'})

        chart = dw.LineChart(
            title='Glacier cumulative mass balance 1950-2024',
            source_name='WMO',
            data=df,
            custom_range_y=[-30, 5],
            y_grid_format='0',
            tooltip_number_format="000.00",
            tooltip_x_format="YYYY",
            plot_height_ratio=0.5,
            plot_height_mode='ratio',
        )

        chart.create().publish()
        iframe_code = chart.get_iframe_code()
        png_url = chart.get_png_url()

        print(chart.chart_id)
        print(iframe_code)
        print(png_url)