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

from pathlib import Path
import os
from climind.definitions import ROOT_DIR, METADATA_DIR
from climind.config.config import DATA_DIR
from climind.web.dashboard import Dashboard

if __name__ == "__main__":

    ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ROOT_DIR = (ROOT_DIR / "..").resolve()
    METADATA_DIR = ROOT_DIR / "climind" / "metadata_files"

    hub = False
    interactive = False

    minimal = False
    dash2025 = True
    dash2024 = False
    dash2023 = False
    dash2022 = False

    decadal = False
    monthly = False
    ocean = False
    cryosphere = False

    justmaps = False

    halloween = False

    comprehensive = False

    regional = False
    regional_multiyear = False
    regional_test = False

    run_all = False

    if hub:
        json_file = ROOT_DIR / "climind" / "web" / "dashboard_metadata" / "hub_dashboard.json"
        dash = Dashboard.from_json(json_file, METADATA_DIR)
        dash_dir = DATA_DIR / "ManagedData" / "Hub"
        dash_dir.mkdir(exist_ok=True)
        dash.build(Path(dash_dir), focus_year=2025)

    if justmaps:
        json_file = ROOT_DIR / "climind" / "web" / "dashboard_metadata" / "maps.json"
        dash = Dashboard.from_json(json_file, METADATA_DIR)
        dash_dir = DATA_DIR / "ManagedData" / "Maps"
        dash_dir.mkdir(exist_ok=True)
        dash.build(Path(dash_dir), focus_year=2025)

    if interactive:
        json_file = ROOT_DIR / "climind" / "web" / "dashboard_metadata" / "interactive_dashboard.json"
        dash = Dashboard.from_json(json_file, METADATA_DIR)
        dash_dir = DATA_DIR / "ManagedData" / "Interactive"
        dash_dir.mkdir(exist_ok=True)
        dash.build(Path(dash_dir), focus_year=2025)

    if minimal:
        json_file = ROOT_DIR / 'climind' / 'web' / 'dashboard_metadata' / 'Minimal_2024.json'
        dash = Dashboard.from_json(json_file, METADATA_DIR)
        dash_dir = DATA_DIR / 'ManagedData' / 'Minimal'
        dash_dir.mkdir(exist_ok=True)
        dash.build(Path(dash_dir), focus_year=2024)

    if halloween:
        json_file = ROOT_DIR / 'climind' / 'web' / 'dashboard_metadata' / 'Halloween.json'
        dash = Dashboard.from_json(json_file, METADATA_DIR)
        dash_dir = DATA_DIR / 'ManagedData' / 'Halloween'
        dash_dir.mkdir(exist_ok=True)
        dash.build(Path(dash_dir), focus_year=2024)

    if comprehensive or run_all:
        json_file = ROOT_DIR / 'climind' / 'web' / 'dashboard_metadata' / 'key_indicators_2023_comprehensive.json'
        dash = Dashboard.from_json(json_file, METADATA_DIR)
        dash_dir = DATA_DIR / 'ManagedData' / 'ComprehensiveDashboard'
        dash_dir.mkdir(exist_ok=True)
        dash.build(Path(dash_dir), focus_year=2023)

    if monthly or run_all:
        json_file = ROOT_DIR / 'climind' / 'web' / 'dashboard_metadata' / 'monthly.json'
        dash = Dashboard.from_json(json_file, METADATA_DIR)
        dash_dir = DATA_DIR / 'ManagedData' / 'MonthlyDashboard'
        dash_dir.mkdir(exist_ok=True)
        dash.build(Path(dash_dir), focus_year=2025)

    if dash2025 or run_all:
        json_file = ROOT_DIR / 'climind' / 'web' / 'dashboard_metadata' / 'key_indicators_2025.json'
        dash = Dashboard.from_json(json_file, METADATA_DIR)
        dash_dir = DATA_DIR / 'ManagedData' / 'Dashboard2025'
        dash_dir.mkdir(exist_ok=True)
        dash.build(Path(dash_dir), focus_year=2025)

    if dash2024 or run_all:
        json_file = ROOT_DIR / 'climind' / 'web' / 'dashboard_metadata' / 'key_indicators_2024.json'
        dash = Dashboard.from_json(json_file, METADATA_DIR)
        dash_dir = DATA_DIR / 'ManagedData' / 'Dashboard2024'
        dash_dir.mkdir(exist_ok=True)
        dash.build(Path(dash_dir), focus_year=2024)

    if dash2023 or run_all:
        json_file = ROOT_DIR / 'climind' / 'web' / 'dashboard_metadata' / 'key_indicators_2023.json'
        dash = Dashboard.from_json(json_file, METADATA_DIR)
        dash_dir = DATA_DIR / 'ManagedData' / 'Dashboard2023'
        dash_dir.mkdir(exist_ok=True)
        dash.build(Path(dash_dir), focus_year=2023)

    if dash2022 or run_all:
        json_file = ROOT_DIR / 'climind' / 'web' / 'dashboard_metadata' / 'key_indicators_2022.json'
        dash = Dashboard.from_json(json_file, METADATA_DIR)
        dash_dir = DATA_DIR / 'ManagedData' / 'Dashboard2022'
        dash_dir.mkdir(exist_ok=True)
        dash.build(Path(dash_dir), focus_year=2022)

    if decadal or run_all:
        json_file = ROOT_DIR / 'climind' / 'web' / 'dashboard_metadata' / 'decadal.json'
        dash = Dashboard.from_json(json_file, METADATA_DIR)
        dash_dir = DATA_DIR / 'ManagedData' / 'DecadalDashboard'
        dash_dir.mkdir(exist_ok=True)
        dash.build(Path(dash_dir))

    if ocean or run_all:
        json_file = ROOT_DIR / 'climind' / 'web' / 'dashboard_metadata' / 'ocean_indicators.json'
        dash = Dashboard.from_json(json_file, METADATA_DIR)
        dash_dir = DATA_DIR / 'ManagedData' / 'OceanDashboard'
        dash_dir.mkdir(exist_ok=True)
        dash.build(Path(dash_dir))

    if cryosphere or run_all:
        json_file = ROOT_DIR / 'climind' / 'web' / 'dashboard_metadata' / 'cryosphere_indicators.json'
        dash = Dashboard.from_json(json_file, METADATA_DIR)
        dash_dir = DATA_DIR / 'ManagedData' / 'CryoDashboard'
        dash_dir.mkdir(exist_ok=True)
        dash.build(Path(dash_dir))

    if regional or run_all:
        json_file = ROOT_DIR / 'climind' / 'web' / 'dashboard_metadata' / 'regional.json'

        dash = Dashboard.from_json(json_file, [DATA_DIR / 'ManagedData' / 'RegionalMetadata', METADATA_DIR])
        dash.data_dir = [DATA_DIR / 'ManagedData' / 'RegionalData', DATA_DIR / "ManagedData" / "Data"]

        dash_dir = DATA_DIR / 'ManagedData' / 'RegionalDashboard'
        dash_dir.mkdir(exist_ok=True)
        dash.build(Path(dash_dir), focus_year=2025)

    if regional_multiyear or run_all:
        json_file = ROOT_DIR / 'climind' / 'web' / 'dashboard_metadata' / 'regional_multiyear.json'
        dash = Dashboard.from_json(json_file, DATA_DIR / 'ManagedData' / 'RegionalMetadata')
        dash.data_dir = DATA_DIR / 'ManagedData' / 'RegionalData'
        dash_dir = DATA_DIR / 'ManagedData' / 'RegionalMultiyearDashboard'
        dash_dir.mkdir(exist_ok=True)
        dash.build(Path(dash_dir), focus_year=2022)

    if regional_test or run_all:
        json_file = ROOT_DIR / 'climind' / 'web' / 'dashboard_metadata' / 'regional_test.json'
        dash = Dashboard.from_json(json_file, DATA_DIR / 'ManagedData' / 'RegionalTestMetadata')
        dash.data_dir = DATA_DIR / 'ManagedData' / 'RegionalTestData'
        dash_dir = DATA_DIR / 'ManagedData' / 'RegionalTestDashboard'
        dash_dir.mkdir(exist_ok=True)
        dash.build(Path(dash_dir), focus_year=2022)
