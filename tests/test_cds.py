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


def test_fetch_year_bad_variable(tmpdir):
    with pytest.raises(ValueError):
        fetch_year(Path(tmpdir), 1999, variable='badvariable')


def test_fetch_existing_year(mocker, tmpdir):
    m = mocker.patch("cdsapi.Client")

    with open(Path(tmpdir) / 'era5_2m_tas_1999.nc', 'w') as f:
        f.write('')
    fetch_year(Path(tmpdir), 1999)
    m.retrieve.assert_not_called()

    with open(Path(tmpdir) / 'cds_sealevel_1999.zip', 'w') as f:
        f.write('')
    fetch_year(Path(tmpdir), 1999, variable='sealevel')
    m.retrieve.assert_not_called()


def test_fetch_future_year(mocker, tmpdir):
    m = mocker.patch("cdsapi.Client")
    fetch_year(Path(tmpdir), 2077)
    m.retrieve.assert_not_called()

    fetch_year(Path(tmpdir), 2077, variable='sealevel')
    m.retrieve.assert_not_called()


def test_fetch_all(mocker):
    m = mocker.patch("climind.fetchers.fetcher_cds.fetch_year")
    fetch('', Path(''), 'era5_2m_tas')
    assert m.call_count == 2023 - 1979 + 1

    m = mocker.patch("climind.fetchers.fetcher_cds.fetch_year")
    fetch('', Path(''), 'sealevel')
    assert m.call_count == 2023 - 1993 + 1


def test_fetch_all_extension(mocker):
    m = mocker.patch("climind.fetchers.fetcher_cds.fetch_year")
    fetch('extension', Path(''), 'era5_2m_tas')
    assert m.call_count == 2023 - 1959 + 1
