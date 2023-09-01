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

import copy
import json

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
        with open(json_filename, 'r') as in_file:
            region_definitions = json.load(in_file)
        return RegionData(region_definitions)

    def get_area_name(self, main_index) -> list:
        temp_list = [x['name'] for x in self.metadata]
        return temp_list[main_index]

    def get_coordinates(self, main_index) -> list:
        temp_list = [x['coordinates'] for x in self.metadata]
        return temp_list[main_index]

    def get_region_name_and_country_list(self, main_index):
        region_name = self.metadata[main_index]['name']
        country_list = self.metadata[main_index]['countries']

        return region_name, country_list


def label_regions(countries, region_name, country_list):
    country_count = len(countries)
    for i in range(country_count):
        countries.at[i, 'wmosubregion'] = 'Null'
        if countries.ISO_A2_EH[i] in country_list:
            countries.at[i, 'wmosubregion'] = region_name

    return countries


def create_shape_file(main_index):
    project_dir = DATA_DIR / "ManagedData"
    out_shape_dir = project_dir / "Shape_Files"

    # Use natural Earth Shape files.
    shape_dir = DATA_DIR / "Natural_Earth" / "ne_10m_admin_0_countries"
    countries = gp.read_file(shape_dir / "ne_10m_admin_0_countries.shp")

    # Add columns
    countries['wmosubregion'] = ''
    countries['dummy'] = ''

    # Read in the region data and get the area that corresponds to the index
    region_data = RegionData.from_json('sub_regions.json')
    region_name, country_list = region_data.get_region_name_and_country_list(main_index)
    area_name = region_data.get_area_name(main_index)
    coordinates = region_data.get_coordinates(main_index)

    # label regions and combine countries into one region
    countries = label_regions(countries, region_name, country_list)
    region_shapes = countries.dissolve(by='wmosubregion')
    # Do same for whole world for the background map
    whole_world = countries.dissolve(by='dummy')

    # Make the coordinates into a GeoDataFrame
    clean_geoms = pd.DataFrame([["Polygon", coordinates]], columns=["field_geom_type", "field_coords"])
    data = Polygon(eval(clean_geoms.field_coords.iloc[0])[0])
    masks = gp.GeoDataFrame({'name': [area_name], 'geometry': [data]})

    # Select the region of interest, copy it and mask off using coordinates
    region_shapes = region_shapes.loc[[area_name]]
    region_clipped = copy.deepcopy(region_shapes)
    region_clipped.geometry[area_name] = region_shapes.geometry[area_name].intersection(masks.geometry[0])
    region_clipped['region'] = area_name

    # Save the shape file
    region_clipped.to_file(out_shape_dir / f'{area_name}')

    return area_name, region_clipped, whole_world


def increment_indices(i1, i2, n1, n2):
    i1 += 1
    if i1 >= n1:
        i1 = 0
        i2 += 1
    return i1, i2


if __name__ == '__main__':
    fig, axs = plt.subplots(2, 2)
    i1, i2 = 0, 0

    for main_index in range(6):
        area_name, region_clipped, whole_world = create_shape_file(main_index)

        if main_index in [0, 2, 3, 4]:
            minx, miny, maxx, maxy = region_clipped.geometry.total_bounds

            whole_world.plot(ax=axs[i1][i2], color='lightgrey')
            region_clipped.plot(ax=axs[i1][i2], color='lightcoral')

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
    plt.savefig(project_dir / 'Figures' / f'LAC_regions.png')
    plt.savefig(project_dir / 'Figures' / f'LAC_regions.svg')
    plt.savefig(project_dir / 'Figures' / f'LAC_regions.pdf')
    plt.close()
