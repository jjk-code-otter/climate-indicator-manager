import pytest
from pathlib import Path
from climind.definitions import ROOT_DIR
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

    dash = Dashboard.from_json(json_file)

    assert isinstance(dash, Dashboard)

    assert len(dash.pages) == 6 + 1

    dash.build(tmpdir)
