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

import pytest
from pathlib import Path
from climind.definitions import ROOT_DIR, METADATA_DIR
from climind.web.dashboard import Page, Dashboard


@pytest.fixture
def page_metadata():
    metadata = {
        "id": "dashboard",
        "name": "Key Climate Indicators",
        "template": "front_page",
        "indicators": ["co2", "tas", "ohc",
                       "sea_level", "arctic_ice", "greenland"],
        "links": ["greenhouse_gases", "global_mean_temperature",
                  "ocean_heat_content", "sea_level",
                  "sea_ice_extent", "glaciers_and_ice_sheets"]
    }
    return metadata


def test_page(page_metadata):
    page = Page(page_metadata)
    assert isinstance(page, Page)


def test_page_get_item(page_metadata):
    page = Page(page_metadata)

    assert page['id'] == 'dashboard'

    page['id'] = 'somethingelse'

    assert page['id'] == 'somethingelse'


def test_dashboard_from_json(tmpdir):
    json_file = ROOT_DIR / 'climind' / 'web' / 'dashboard_metadata' / 'key_indicators.json'
    assert json_file.exists()

    dash = Dashboard.from_json(json_file, METADATA_DIR)

    assert isinstance(dash, Dashboard)

    assert len(dash.pages) == 6 + 1
