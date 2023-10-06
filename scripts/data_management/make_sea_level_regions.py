#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2022-2023 John Kennedy
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

import json
from typing import Tuple, List

from shapely.geometry import Polygon

import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gp
from climind.config.config import DATA_DIR


class RegionData:

    def __init__(self, region_definitions: dict):
        self.metadata = region_definitions

    @staticmethod
    def from_json(json_filename):
        """Create a RegionData object from a json file"""
        with open(json_filename, 'r') as in_file:
            region_definitions = json.load(in_file)
        return RegionData(region_definitions)

    def get_area_name(self, main_index: int) -> str:
        """
        Get the area names corresponding to the index

        Parameters
        ----------
        main_index: int
            The index of required area

        Returns
        -------
        list
            List of area names
        """
        temp_list = [x['name'] for x in self.metadata]
        return temp_list[main_index]

    def get_coordinates(self, main_index: int) -> list:
        """
        Get the coordinates corresponding to the index

        Parameters
        ----------
        main_index: int

        Returns
        -------
        list
            List of coordinates
        """
        temp_list = [x['coordinates'] for x in self.metadata]
        return temp_list[main_index]


def create_shape_file(main_index, region_json_file) -> Tuple[str, gp.GeoDataFrame]:
    """
    Given an index and a json file specifying the regions, make a shape file

    Parameters
    ----------
    main_index: int
        Index of the region to extract from the file
    region_json_file: str
        Name of the json file to create the shape file from

    Returns
    -------
    Tuple[str, gp.GeoDataFrame, gp.GeoDataFrame]
        the region name, the region as a shape file , the region as a shape file
    """
    project_dir = DATA_DIR / "ManagedData"
    out_shape_dir = project_dir / "Shape_Files"

    # Read in the region data and get the area that corresponds to the index
    region_data = RegionData.from_json(region_json_file)
    area_name = region_data.get_area_name(main_index)
    coordinates = region_data.get_coordinates(main_index)

    # Make the coordinates into a GeoDataFrame
    clean_geoms = pd.DataFrame([["Polygon", coordinates]], columns=["field_geom_type", "field_coords"])
    data = Polygon(eval(clean_geoms.field_coords.iloc[0])[0])
    masks = gp.GeoDataFrame({'wmosubregion': [area_name], 'geometry': [data]})

    # Save the shape file
    masks.to_file(out_shape_dir / f'{area_name}')

    return (area_name, masks)


def increment_indices(i1, i2, n1, n2):
    i1 += 1
    if i1 >= n1:
        i1 = 0
        i2 += 1
    return i1, i2


if __name__ == '__main__':
    fig, axs = plt.subplots(2, 2)
    i1, i2 = 0, 0

    subregions = gp.read_file(r"C:\Users\johnk\Downloads\Africa.shp")

    region_json_file = 'coastal_regions.json'
    output_image = 'Coastal_regions'
    n_regions = 4

    # Use natural Earth Shape files.
    shape_dir = DATA_DIR / "Natural_Earth" / "ne_10m_admin_0_countries"
    countries = gp.read_file(shape_dir / "ne_10m_admin_0_countries.shp")
    countries['dummy'] = ''
    whole_world = countries.dissolve(by='dummy')

    for main_index in range(n_regions):
        area_name, region_clipped = create_shape_file(main_index, region_json_file)

        minx, miny, maxx, maxy = region_clipped.geometry.total_bounds

        whole_world.plot(ax=axs[i1][i2], color='lightgrey')
        region_clipped.plot(ax=axs[i1][i2], color='lightcoral', alpha=0.5)

        axs[i1, i2].set_title(area_name, fontsize=10)
        axs[i1, i2].set_xlim(minx - 2, maxx + 2)
        axs[i1, i2].set_ylim(miny - 2, maxy + 2)

        axs[i1][i2].set_xticklabels([])
        axs[i1][i2].set_yticklabels([])
        axs[i1][i2].set_xticks([])
        axs[i1][i2].set_yticks([])

        i1, i2 = increment_indices(i1, i2, 2, 2)

    plt.subplots_adjust(hspace=0.15)
    project_dir = DATA_DIR / "ManagedData"
    plt.savefig(project_dir / 'Figures' / f'{output_image}.png')
    plt.savefig(project_dir / 'Figures' / f'{output_image}.svg')
    plt.savefig(project_dir / 'Figures' / f'{output_image}.pdf')
    plt.close()
