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
from scripts.global_temperature.compare_preindustrial import all_annual_datasets

if __name__ == "__main__":

    # client = dw.Datawrapper()
    # ws = client.get_workspaces('SoC 2025')
    # fd = client.get_folders()

    folder_id = 389606

    final_year = 2025

    project_dir = DATA_DIR / "ManagedData"
    ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    METADATA_DIR = ROOT_DIR.resolve() / "climind" / "metadata_files"
    metadata_dir = METADATA_DIR

    data_dir = project_dir / "Data"

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)

    iod = True
    enso = True

    mhw = False

    lsat = False
    sst = False

    ch4 = False
    n2o = False
    co2growth = False
    ch4growth = False
    n2ogrowth = False

    gmst = False
    co2 = False
    ohc = False
    sea_level = False
    sea_ice =False
    antarctic_sea_ice = False
    glaciers = False
    oceanph = False
    eei = False

    if iod:
        ts_archive = archive.select(
            {
                'variable': 'lsat',
                'type': 'timeseries',
                'name': ["NOAA LSAT v6", "CRUTEM5", "Berkeley Earth Hires LSAT", "DCENT_LSAT_I", "CMA_GLST", "CLSAT21"],
                'time_resolution': 'annual'
            }
        )
        all_datasets = ts_archive.read_datasets(data_dir)
        all_annual_datasets = []
        for ds in all_datasets:
            ds.rebaseline(1991,2020)
            ds.select_year_range(1850, 2025)
            all_annual_datasets.append(ds)
        df = equalise_datasets(all_annual_datasets)

        chart = dw.LineChart(
            title='Global land surface air temperature 1850-2025',
            source_name='WMO',
            data=df,
            custom_range_y=[-2.3, 1.2],
            y_grid_format='0.0',
            tooltip_number_format="00.00",
            tooltip_x_format="YYYY",
        )

        chart.create(folder_id=folder_id).publish()
        iframe_code = chart.get_iframe_code()
        png_url = chart.get_png_url()

        print(chart.chart_id)
        print(iframe_code)
        print(png_url)


    if enso:
        pass

    if mhw:
        ts_archive = archive.select(
            {
                'variable': ['mhw', 'mcs'],
                'type': 'timeseries',
                'time_resolution': 'annual'
            }
        )
        all_datasets = ts_archive.read_datasets(data_dir)
        df = equalise_datasets(all_datasets)

        chart = dw.LineChart(
            title='Area affected by marine heatwaves and cold spells',
            intro='% of ocean area affected, baseline 1982-2021',
            source_name='WMO',
            data=df,
            custom_range_y=[0, 100],
            y_grid_format='0.0',
            tooltip_number_format="0.[00]%",
            tooltip_x_format="YYYY",
        )

        chart.create(folder_id=folder_id).publish()
        iframe_code = chart.get_iframe_code()
        png_url = chart.get_png_url()

        print(chart.chart_id)
        print(iframe_code)
        print(png_url)

    if lsat:
        ts_archive = archive.select(
            {
                'variable': 'lsat',
                'type': 'timeseries',
                'name': ["NOAA LSAT v6", "CRUTEM5", "Berkeley Earth Hires LSAT", "DCENT_LSAT_I", "CMA_GLST", "CLSAT21"],
                'time_resolution': 'annual'
            }
        )
        all_datasets = ts_archive.read_datasets(data_dir)
        all_annual_datasets = []
        for ds in all_datasets:
            ds.rebaseline(1991,2020)
            ds.select_year_range(1850, 2025)
            all_annual_datasets.append(ds)
        df = equalise_datasets(all_annual_datasets)

        chart = dw.LineChart(
            title='Global land surface air temperature 1850-2025',
            source_name='WMO',
            data=df,
            custom_range_y=[-2.3, 1.2],
            y_grid_format='0.0',
            tooltip_number_format="00.00",
            tooltip_x_format="YYYY",
        )

        chart.create(folder_id=folder_id).publish()
        iframe_code = chart.get_iframe_code()
        png_url = chart.get_png_url()

        print(chart.chart_id)
        print(iframe_code)
        print(png_url)

    if sst:
        ts_archive = archive.select(
            {
                'variable': 'sst',
                'type': 'timeseries',
                'name': ["HadSST4", "ERSST v6", "DCENT_SST_I", "CMA_SST", "CMEMS_SST"],
                'time_resolution': 'annual'
            }
        )
        all_datasets = ts_archive.read_datasets(data_dir)
        all_annual_datasets = []
        for ds in all_datasets:
            ds.rebaseline(1991,2020)
            ds.select_year_range(1850, 2025)
            all_annual_datasets.append(ds)
        df = equalise_datasets(all_annual_datasets)

        chart = dw.LineChart(
            title='Global sea surface air temperature 1850-2025',
            intro='difference from 1991-2020 average, degC',
            source_name='WMO',
            data=df,
            custom_range_y=[-1.5, 0.5],
            y_grid_format='0.0',
            tooltip_number_format="00.00",
            tooltip_x_format="YYYY",
        )

        chart.create(folder_id=folder_id).publish()
        iframe_code = chart.get_iframe_code()
        png_url = chart.get_png_url()

        print(chart.chart_id)
        print(iframe_code)
        print(png_url)

    if gmst:
        # some global temperature data sets are annual only, others are monthly so need to read these separately
        ts_archive = archive.select({'variable': 'tas',
                                     'type': 'timeseries',
                                     'name': ["NOAA v6", "GISTEMP", "ERA5", "JRA-3Q", "Berkeley Earth Hires", "HadCRUT5", "DCENT_I", "CMA_GMST", "CMST v3"],
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

        chart.create(folder_id=folder_id).publish()
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

        chart.create(folder_id=folder_id).publish()
        iframe_code = chart.get_iframe_code()
        png_url = chart.get_png_url()

        print(chart.chart_id)
        print(iframe_code)
        print(png_url)

    if ch4:
        # some global temperature data sets are annual only, others are monthly so need to read these separately
        ts_archive = archive.select({'variable': 'ch4',
                                     'type': 'timeseries',
                                     'name': ['WDCGG CH4'],
                                     'time_resolution': 'annual'})

        all_datasets = ts_archive.read_datasets(data_dir)

        df = equalise_datasets(all_datasets)

        chart = dw.LineChart(
            title='Atmospheric methane concentration 1984-2024',
            source_name='WMO',
            data=df,
            custom_range_y=[1650, 1950],
            y_grid_format='0',
            tooltip_number_format="00.0",
            tooltip_x_format="YYYY",
            plot_height_ratio=0.5,
            plot_height_mode='ratio',

        )

        chart.create(folder_id=folder_id).publish()
        iframe_code = chart.get_iframe_code()
        png_url = chart.get_png_url()

        print(chart.chart_id)
        print(iframe_code)
        print(png_url)

    if n2o:
        # some global temperature data sets are annual only, others are monthly so need to read these separately
        ts_archive = archive.select({'variable': 'n2o',
                                     'type': 'timeseries',
                                     'name': ['WDCGG N2O'],
                                     'time_resolution': 'annual'})

        all_datasets = ts_archive.read_datasets(data_dir)

        df = equalise_datasets(all_datasets)

        chart = dw.LineChart(
            title='Atmospheric nitrous oxide concentration 1984-2024',
            source_name='WMO',
            data=df,
            custom_range_y=[300, 340],
            y_grid_format='0',
            tooltip_number_format="00.0",
            tooltip_x_format="YYYY",
            plot_height_ratio=0.5,
            plot_height_mode='ratio',

        )

        chart.create(folder_id=folder_id).publish()
        iframe_code = chart.get_iframe_code()
        png_url = chart.get_png_url()

        print(chart.chart_id)
        print(iframe_code)
        print(png_url)

    if co2growth:
        # some global temperature data sets are annual only, others are monthly so need to read these separately
        ts_archive = archive.select({'variable': 'co2rate',
                                     'type': 'timeseries',
                                     'name': ['WDCGG CO2 growth'],
                                     'time_resolution': 'annual'})

        all_datasets = ts_archive.read_datasets(data_dir)

        df = equalise_datasets(all_datasets)

        chart = dw.LineChart(
            title='Atmospheric carbon dioxide growth rate 1984-2024',
            source_name='WMO',
            data=df,
            custom_range_y=[0, 3.5],
            y_grid_format='0',
            tooltip_number_format="0.0",
            tooltip_x_format="YYYY",
            plot_height_ratio=0.5,
            plot_height_mode='ratio',

        )

        chart.create(folder_id=folder_id).publish()
        iframe_code = chart.get_iframe_code()
        png_url = chart.get_png_url()

        print(chart.chart_id)
        print(iframe_code)
        print(png_url)

    if ch4growth:
        # some global temperature data sets are annual only, others are monthly so need to read these separately
        ts_archive = archive.select({'variable': 'ch4rate',
                                     'type': 'timeseries',
                                     'name': ['WDCGG CH4 growth'],
                                     'time_resolution': 'annual'})

        all_datasets = ts_archive.read_datasets(data_dir)

        df = equalise_datasets(all_datasets)

        chart = dw.LineChart(
            title='Atmospheric methane growth rate 1984-2024',
            source_name='WMO',
            data=df,
            custom_range_y=[-3, 18],
            y_grid_format='0',
            tooltip_number_format="0.0",
            tooltip_x_format="YYYY",
            plot_height_ratio=0.5,
            plot_height_mode='ratio',

        )

        chart.create(folder_id=folder_id).publish()
        iframe_code = chart.get_iframe_code()
        png_url = chart.get_png_url()

        print(chart.chart_id)
        print(iframe_code)
        print(png_url)

    if n2ogrowth:
        # some global temperature data sets are annual only, others are monthly so need to read these separately
        ts_archive = archive.select({'variable': 'n2orate',
                                     'type': 'timeseries',
                                     'name': ['WDCGG N2O growth'],
                                     'time_resolution': 'annual'})

        all_datasets = ts_archive.read_datasets(data_dir)

        df = equalise_datasets(all_datasets)

        chart = dw.LineChart(
            title='Atmospheric nitrous oxide growth rate 1984-2024',
            source_name='WMO',
            data=df,
            custom_range_y=[0, 1.4],
            y_grid_format='0',
            tooltip_number_format="0.0",
            tooltip_x_format="YYYY",
            plot_height_ratio=0.5,
            plot_height_mode='ratio',

        )

        chart.create(folder_id=folder_id).publish()
        iframe_code = chart.get_iframe_code()
        png_url = chart.get_png_url()

        print(chart.chart_id)
        print(iframe_code)
        print(png_url)

    if ohc:
        # some global temperature data sets are annual only, others are monthly so need to read these separately
        ts_archive = archive.select({'variable': 'ohc2k',
                                     'type': 'timeseries',
                                     'name': ["Cheng et al 2k", "Miniere", "Copernicus_OHC", "GCOS2k TEMP"],
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

        chart.create(folder_id=folder_id).publish()
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

        chart.create(folder_id=folder_id).publish()
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

        chart.create(folder_id=folder_id).publish()
        iframe_code = chart.get_iframe_code()
        png_url = chart.get_png_url()

        print(chart.chart_id)
        print(iframe_code)
        print(png_url)

    if antarctic_sea_ice:
        # some global temperature data sets are annual only, others are monthly so need to read these separately
        ts_archive = archive.select({'variable': 'antarctic_ice',
                                     'type': 'timeseries',
                                     'name': ["JAXA SH", "NSIDC v4 SH", "OSI SAF SH v2p3"],
                                     'time_resolution': 'monthly'})

        all_datasets = ts_archive.read_datasets(data_dir)

        for ds in all_datasets:
            ds.rebaseline(1991, 2020)
            ds.make_annual()

        df = equalise_datasets(all_datasets)

        df['year'] = df['time']
        df = df.drop(columns=['time', 'month'])

        chart = dw.LineChart(
            title='Antarctic sea-ice extent 1978-2025',
            source_name='WMO',
            data=df,
            custom_range_y=[-2.5, 2.5],
            y_grid_format='0',
            tooltip_number_format=".00",
            tooltip_x_format="YYYY",
            plot_height_ratio=0.5,
            plot_height_mode='ratio',
        )

        chart.create(folder_id=folder_id).publish()
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

        chart.create(folder_id=folder_id).publish()
        iframe_code = chart.get_iframe_code()
        png_url = chart.get_png_url()

        print(chart.chart_id)
        print(iframe_code)
        print(png_url)

    if oceanph:
        # some global temperature data sets are annual only, others are monthly so need to read these separately
        ts_archive = archive.select({'variable': 'ph',
                                     'type': 'timeseries',
                                     'name': ["CMEMS 2025"],
                                     'time_resolution': 'annual'})

        all_datasets = ts_archive.read_datasets(data_dir)

        df = equalise_datasets(all_datasets)

        chart = dw.LineChart(
            title='Ocean pH',
            source_name='WMO',
            data=df,
            custom_range_y=[8.02, 8.14],
            y_grid_format='0.00',
            tooltip_number_format="000.00",
            tooltip_x_format="YYYY",
            plot_height_ratio=0.5,
            plot_height_mode='ratio',
        )

        chart.create(folder_id=folder_id).publish()
        iframe_code = chart.get_iframe_code()
        png_url = chart.get_png_url()

        print(chart.chart_id)
        print(iframe_code)
        print(png_url)

        chb = dw.get_chart(chart.chart_id)

        print()

    if eei:
        # some global temperature data sets are annual only, others are monthly so need to read these separately
        ts_archive = archive.select({'variable': 'eei',
                                     'type': 'timeseries',
                                     'name': ["Miniere EEI", "IAP EEI", "Copernicus EEI", "CERES EEI"],
                                     'time_resolution': 'annual'})

        all_datasets = ts_archive.read_datasets(data_dir)

        df = equalise_datasets(all_datasets)

        chart = dw.LineChart(
            title='Earths Energy Imbalance',
            source_name='WMO',
            data=df,
            custom_range_y=[-1.1, 1.6],
            y_grid_format='0.00',
            tooltip_number_format=".00",
            tooltip_x_format="YYYY",
            plot_height_ratio=0.5,
            plot_height_mode='ratio',
        )

        chart.create(folder_id=folder_id).publish()
        iframe_code = chart.get_iframe_code()
        png_url = chart.get_png_url()

        print(chart.chart_id)
        print(iframe_code)
        print(png_url)

        chb = dw.get_chart(chart.chart_id)

        print()