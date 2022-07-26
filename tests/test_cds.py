import pytest
from pathlib import Path
from climind.fetchers.fetcher_cds import pick_months, fetch_year, fetch
from datetime import datetime


def test_earlier_year():
    now = datetime(2022, 6, 8)
    months = pick_months(2002, now)
    assert len(months) == 12
    for m in range(12):
        assert months[m] == f'{m + 1:02d}'


def test_future_year():
    now = datetime(2022, 6, 8)
    months = pick_months(2077, now)
    assert len(months) == 0


def test_this_year_after_seventh():
    now = datetime(2022, 6, 8)
    months = pick_months(2022, now)
    assert len(months) == 5
    for m in range(5):
        assert months[m] == f'{m + 1:02d}'


def test_this_year_before_seventh():
    now = datetime(2022, 6, 3)
    months = pick_months(2022, now)
    assert len(months) == 4
    for m in range(4):
        assert months[m] == f'{m + 1:02d}'


def test_january_empty_list():
    now = datetime(2022, 1, 2)
    months = pick_months(2022, now)
    assert len(months) == 0


def test_january_empty_list_after_seventh():
    now = datetime(2022, 1, 8)
    months = pick_months(2022, now)
    assert len(months) == 0


def test_fetch_year(mocker, tmpdir):
    m = mocker.patch("cdsapi.Client")
    fetch_year(Path(tmpdir), 1999)

    assert m.retrieve.called_once()


def test_fetch_existing_year(mocker, tmpdir):
    m = mocker.patch("cdsapi.Client")

    with open(Path(tmpdir) / 'era5_2m_tas_1999.nc', 'w') as f:
        f.write('')

    fetch_year(Path(tmpdir), 1999)

    m.retrieve.assert_not_called()


def test_fetch_future_year(mocker, tmpdir):
    m = mocker.patch("cdsapi.Client")
    fetch_year(Path(tmpdir), 2077)
    m.retrieve.assert_not_called()


def test_fetch_all(mocker):
    m = mocker.patch("climind.fetchers.fetcher_cds.fetch_year")
    fetch('', Path(''))
    assert m.call_count == 2022-1979+1

