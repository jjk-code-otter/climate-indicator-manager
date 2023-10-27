#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 11:43:05 2023
@author: Lancelot Leclercq
edited by: John Kennedy
"""

import sys
import os
import itertools
import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
from shapely.geometry import Point, Polygon
from climind.config.config import DATA_DIR

project_dir = DATA_DIR / "ManagedData"
shape_dir = project_dir / "Shape_Files" / "Sealevel_Regions_Africa"
in_data_dir = project_dir / "Data" / "CMEMS trend"
out_data_dir = DATA_DIR

trd = xr.open_dataset(in_data_dir / "global_omi_sl_regional_trends_19930101_P20230403.nc")

shp_name = ["Africa", "WMO_AFRICA"]
mean_dict = {"Name": [], "trd_mean": []}

for name in shp_name:

    shp = gpd.read_file(shape_dir / f"{name}.shp")
    zone_trd = {}

    for lat, lon in itertools.product(trd.latitude.data, trd.longitude.data):

        for ishp in range(len(shp) - 1):

            if name == "Africa":
                zone = shp.geometry[ishp]
            elif name == "WMO_AFRICA":
                zone = Polygon(shp.geometry[ishp].coords)
            else:
                raise ValueError(f"Unknown name {name}")

            if zone.contains(Point(lon, lat)):

                # Initialise the list
                zone_trd[shp.Name[ishp]] = zone_trd.setdefault(shp.Name[ishp])
                if zone_trd[shp.Name[ishp]] is None:
                    zone_trd[shp.Name[ishp]] = []

                # Add the value to the appropriate list

                zone_trd[shp.Name[ishp]].append(float(trd.msl_trend.sel(longitude=lon, latitude=lat).data))

    trd_mean = []
    for zone in zone_trd:
        trd_mean.append(np.nanmean(zone_trd[zone]))

    df = pd.DataFrame({"Region": zone_trd.keys(), "trd_mean": trd_mean})
    df.to_csv(out_data_dir / f"CMEMS_trd_mean_{name}.csv", index=False)
