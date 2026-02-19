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

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR

project_dir = DATA_DIR / "ManagedData"



df = pd.read_excel(
    project_dir / "Data" / "gcb_fossil" / "Global_Carbon_Budget_2025_v0.6.xlsx",
    sheet_name="Global Carbon Budget",
    header=21
)

plt.plot(df.Year, df["fossil emissions excluding carbonation"])
plt.plot(df.Year, df["land-use change emissions"])
plt.plot(df.Year, df["atmospheric growth"])
plt.plot(df.Year, df["ocean sink"])
plt.plot(df.Year, df["land sink"])
plt.plot(df.Year, df["cement carbonation sink"])
plt.plot(df.Year, df["budget imbalance"])
plt.show()


print(df)