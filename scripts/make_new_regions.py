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

from shapely.geometry import Polygon

import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gp
from climind.config.config import DATA_DIR


def make_the_thing(main_index):
    project_dir = DATA_DIR / "ManagedData"
    out_shape_dir = project_dir / "Shape_Files"

    # Use natural Earth Shape files.
    shape_dir = DATA_DIR / "Natural_Earth" / "ne_10m_admin_0_countries"

    countries = gp.read_file(shape_dir / "ne_10m_admin_0_countries.shp")
    countries['wmosubregion'] = ''

    region_to_country_lookups = [
        {
            'South America': ['CO', 'VE', 'GY', 'SR', 'FR', 'EC', 'PE',
                              'BR', 'BO', 'PY', 'CL', 'UY', 'AR']
        },
        {
            'Mexico': ['MX', 'HN', 'CR', 'NI', 'GT', 'BZ', 'SV',
                       'PA', 'CU', 'JM', 'CO', 'US']
        },
        {
            'Caribbean': ['CO', 'VE', 'PA', 'CR', 'NI', 'HN', 'US', 'GY', 'SR',
                          'CU', 'JM', 'HT', 'BS', 'DO', 'PR', 'TC',
                          'VG', 'AI', 'MS', 'GP', 'DM', 'MQ', 'LC',
                          'VC', 'BB', 'GD', 'TT', 'AW', 'CW', 'KY']
        }
    ]

    region_to_country_lookup = region_to_country_lookups[main_index]

    for i in range(len(countries)):
        countries.wmosubregion[i] = 'Null'
        for region_key in region_to_country_lookup:
            if countries.ISO_A2_EH[i] in region_to_country_lookup[region_key]:
                countries.wmosubregion[i] = region_key
                print(region_key, countries.NAME[i], countries.ISO_A2_EH[i], countries.SUBREGION[i])
        if countries.wmosubregion[i] == 'Null':
            print("No match", countries.NAME[i], countries.ISO_A2_EH[i])

    wmo_sub_region_shapes = countries.dissolve(by='wmosubregion')

    all_area_names = [
        'South America',
        'Mexico',
        'Caribbean'
    ]

    all_coordinates = [
        "[[[-90, -60], [-90, 15], [-30, 15], [-30, -60], [-90, -60]]]",
        "[[[-120, 5], [-120, 35], [-85, 35], [-85, 23], [-75, 23], [-75, 5], [-120, 5]]]",
        "[[[-85, 5], [-85, 30], [-55, 30], [-55, 5], [-85, 5]]]"
    ]

    area_names = all_area_names[main_index]
    coordinates = all_coordinates[main_index]

    clean_geoms = pd.DataFrame([["Polygon", coordinates]], columns=["field_geom_type", "field_coords"])
    data = Polygon(eval(clean_geoms.field_coords.iloc[0])[0])

    masks = gp.GeoDataFrame({'name': [area_names], 'geometry': [data]})

    wmo_sub_region_shapes = wmo_sub_region_shapes.loc[[area_names]]
    wmo_sub_region_clipped = copy.deepcopy(wmo_sub_region_shapes)
    wmo_sub_region_clipped.geometry[area_names] = wmo_sub_region_shapes.geometry[area_names].intersection(masks.geometry[0])
    wmo_sub_region_clipped['region'] = area_names

    wmo_sub_region_clipped.to_file(out_shape_dir / f'{area_names}')

    wmo_sub_region_clipped.plot(column='ECONOMY')
    plt.show()
    plt.close()

    print()


if __name__ == '__main__':

    for i in range(3):
        make_the_thing(i)
