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

    folder_id = 390790

    final_year = 2025

    project_dir = DATA_DIR / "ManagedData"
    ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    METADATA_DIR = project_dir / 'RegionalMetadata'
    metadata_dir = METADATA_DIR

    data_dir = project_dir / "RegionalData"

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)

    region_list = [
        ["wmo_ra_1", "WMO RA I Africa annual land temperature"],
        ["wmo_ra_2", "WMO RA II Asia annual land temperature"],
        ["wmo_ra_3", "WMO RA III South America annual land temperature"],
        ["wmo_ra_4", "WMO RA IV North America annual land temperature"],
        ["wmo_ra_5", "WMO RA V Southwest Pacific annual land temperature"],
        ["wmo_ra_land_ocean_5", "WMO RA V Southwest Pacific (land and ocean)"],
        ["wmo_ra_6", "WMO RA VI Europe annual land temperature"],
        ["africa_subregion_1", "North Africa land temperature"],
        ["africa_subregion_2", "West Africa land temperature"],
        ["africa_subregion_3", "Central Africa land temperature"],
        ["africa_subregion_4", "Eastern Africa land temperature"],
        ["africa_subregion_5", "Southern Africa land temperature"],
        ["africa_subregion_6", "Indian Ocean land temperature"],
        ["lac_subregion_3", "Caribbean land temperature"],
        ["lac_subregion_4", "Mexico land temperature"],
        ["lac_subregion_5", "Central America land temperature"],
        ["lac_subregion_6", "Latin America and the Caribbean land temperature"]
    ]

    for region in region_list:
        ts_archive = archive.select(
            {
                'variable': region[0],
                'type': 'timeseries',
                'time_resolution': 'annual',
                'origin': 'obs'
            }
        )

        all_datasets = ts_archive.read_datasets(data_dir)
        df = equalise_datasets(all_datasets)

        columns = {}
        for ds in all_datasets:
            columns[ds.metadata['name']] = ds.metadata['display_name']
        df.rename(columns=columns, inplace=True)

        chart = dw.LineChart(
            title=region[1],
            intro="difference from 1991-2020 average (°C)",
            source_name='WMO',
            data=df,
            custom_range_y=[-2.5, 1.5],
            y_grid_format='0.0',
            tooltip_number_format="0.00",
            tooltip_x_format="YYYY"
        )

        chart.create(folder_id=folder_id)

        client = dw.Datawrapper()
        client.update_metadata(
            chart_id = chart.chart_id,
            metadata = {
                "visualize": {
                    "direct-labeling": False,
                    "legend": {"enabled": True}
                }
            }
        )

        chart.publish()
        iframe_code = chart.get_iframe_code()
        png_url = chart.get_png_url()

        print(chart.chart_id)
        print(iframe_code)
        print(png_url)

        assert False

