#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2026 John Kennedy
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


import xarray as xa
import itertools
import numpy as np
import pandas as pd
from climind.config.config import DATA_DIR

import cartopy.crs as ccrs
import matplotlib.pyplot as plt

data_dir = DATA_DIR / 'ManagedData' / 'Data' / 'CMA_GMST'

ts = []
years = []
months = []

plotit = False

for year, month in itertools.product(range(1850, 2026), range(1, 13)):
    if (data_dir / f'SURF_CLI_GLB_MST_MON_GRID_2DEG_{year:04d}{month:02d}.nc').exists():
        df = xa.open_dataset(data_dir / f'SURF_CLI_GLB_MST_MON_GRID_2DEG_{year:04d}{month:02d}.nc', engine='netcdf4')
        df = df["anomaly"]
        weights = np.cos(np.deg2rad(df.lat))
        area_average = df.weighted(weights).mean(dim=('lat', 'lon'))
        ts.append(float(area_average.values))
        years.append(year)
        months.append(month)

        if plotit:
            plt.figure()
            proj = ccrs.PlateCarree()
            p = df.plot(transform=proj, subplot_kws={'projection': proj},
                                          levels=[-3, -2, -1, 0, 1, 2, 3])
            p.axes.coastlines()
            plt.title(f"{year}-{month:02d}")
            plt.show()
            plt.close('all')
    else:
        print(f"Missing {year} {month:02d}")
        years.append(year)
        months.append(month)
        ts.append(np.nan)

df = pd.DataFrame({'year': years, 'month': months, 'data': ts})

df.to_csv(data_dir / 'Global_Mean.csv', index=False)
print(df)

plt.plot(ts)
plt.show()


