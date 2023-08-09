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

from pathlib import Path
from climind.definitions import ROOT_DIR, METADATA_DIR
from climind.config.config import DATA_DIR
from climind.web.dashboard import Dashboard

if __name__ == "__main__":
    # Key indicators 2023
    json_file = ROOT_DIR / 'climind' / 'web' / 'dashboard_metadata' / 'key_indicators_2023.json'
    dash = Dashboard.from_json(json_file, METADATA_DIR)
    dash_dir = DATA_DIR / 'ManagedData' / 'Dashboard2023'
    dash_dir.mkdir(exist_ok=True)
    dash.build(Path(dash_dir), focus_year=2023)

    # Key indicators 2022
    json_file = ROOT_DIR / 'climind' / 'web' / 'dashboard_metadata' / 'key_indicators_2022.json'
    dash = Dashboard.from_json(json_file, METADATA_DIR)
    dash_dir = DATA_DIR / 'ManagedData' / 'Dashboard2022'
    dash_dir.mkdir(exist_ok=True)
    dash.build(Path(dash_dir), focus_year=2022)

    # Decadal
    json_file = ROOT_DIR / 'climind' / 'web' / 'dashboard_metadata' / 'decadal.json'
    dash = Dashboard.from_json(json_file, METADATA_DIR)
    dash_dir = DATA_DIR / 'ManagedData' / 'DecadalDashboard'
    dash_dir.mkdir(exist_ok=True)
    dash.build(Path(dash_dir))

    # Ocean
    json_file = ROOT_DIR / 'climind' / 'web' / 'dashboard_metadata' / 'ocean_indicators.json'
    dash = Dashboard.from_json(json_file, METADATA_DIR)
    dash_dir = DATA_DIR / 'ManagedData' / 'OceanDashboard'
    dash_dir.mkdir(exist_ok=True)
    dash.build(Path(dash_dir))

    # Cryosphere
    json_file = ROOT_DIR / 'climind' / 'web' / 'dashboard_metadata' / 'cryosphere_indicators.json'
    dash = Dashboard.from_json(json_file, METADATA_DIR)
    dash_dir = DATA_DIR / 'ManagedData' / 'CryoDashboard'
    dash_dir.mkdir(exist_ok=True)
    dash.build(Path(dash_dir))

    # regional
    json_file = ROOT_DIR / 'climind' / 'web' / 'dashboard_metadata' / 'regional.json'
    dash = Dashboard.from_json(json_file, DATA_DIR / 'ManagedData' / 'RegionalMetadata')
    dash.data_dir = DATA_DIR / 'ManagedData' / 'RegionalData'
    dash_dir = DATA_DIR / 'ManagedData' / 'RegionalDashboard'
    dash_dir.mkdir(exist_ok=True)
    dash.build(Path(dash_dir), focus_year=2022)

    # regional test
    json_file = ROOT_DIR / 'climind' / 'web' / 'dashboard_metadata' / 'regional_test.json'
    dash = Dashboard.from_json(json_file, DATA_DIR / 'ManagedData' / 'RegionalTestMetadata')
    dash.data_dir = DATA_DIR / 'ManagedData' / 'RegionalTestData'
    dash_dir = DATA_DIR / 'ManagedData' / 'RegionalTestDashboard'
    dash_dir.mkdir(exist_ok=True)
    dash.build(Path(dash_dir), focus_year=2022)


