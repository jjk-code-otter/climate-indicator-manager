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
"""
Sets up the DATA_DIR variable used throughout the package
"""
import os
from pathlib import Path


def check_setup(data_dir: Path) -> None:
    """
    Ensure that all the relevant directories exist

    Parameters
    ----------
    data_dir: Path
      Path to the directory which will contain all of the

    Returns
    -------
    None
    """
    project_dir = data_dir / "ManagedData"
    data_dir = project_dir / "Data"
    log_dir = project_dir / "Logs"
    figures_dir = project_dir / "Figures"
    formatted_data_dir = project_dir / "Formatted_Data"
    project_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    formatted_data_dir.mkdir(parents=True, exist_ok=True)


data_dir_env = os.getenv('DATADIR')

DATA_DIR = Path(data_dir_env)
CLIMATOLOGY = [1991, 2020]

check_setup(DATA_DIR)
