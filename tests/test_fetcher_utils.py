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
import itertools

import pytest

import climind.fetchers.fetcher_utils as utils


@pytest.fixture
def test_url():
    return 'https://www.doesntexist.boom/directory/filename.txt'


def test_get_filename_from_url(test_url):
    filename = utils.filename_from_url(test_url)
    assert filename == 'filename.txt'


def test_get_filename_from_url_ftp():
    url = 'ftps://old.school/directory/ftp_filename.txt'
    filename = utils.filename_from_url(url)
    assert filename == 'ftp_filename.txt'


def test_get_filename_from_url_no_filename():
    url = 'https://www.doesntexist.boom/directory/'
    filename = utils.filename_from_url(url)
    assert filename == ''


def test_dir_and_filename(test_url):
    test_dir, filename = utils.dir_and_filename_from_url(test_url)
    assert filename == 'filename.txt'
    assert test_dir == 'https://www.doesntexist.boom/directory'


def test_url_from_filename(test_url):
    fixed_url = utils.url_from_filename(test_url, 'new_filename.txt')
    assert fixed_url == 'https://www.doesntexist.boom/directory/new_filename.txt'


def test_get_ftp_host_and_directory():
    url = 'ftps://the.host.name/directory0/directory1/directory2/filename.txt'
    host, working_directory = utils.get_ftp_host_and_directory_from_url(url)

    assert host == 'the.host.name'
    for i in range(3):
        assert working_directory[i] == f'directory{i}'


def test_get_n_months_back_raises():
    with pytest.raises(ValueError):
        _, _ = utils.get_n_months_back(2022, 12, back=13)
    with pytest.raises(ValueError):
        _, _ = utils.get_n_months_back(2022, 12, back=-1)


def test_get_n_months_back():
    y, m = utils.get_n_months_back(2022, 12)
    assert y == 2022
    assert m == 1

    y, m = utils.get_n_months_back(1985, 3)
    assert y == 1984
    assert m == 4

    for y1, m1 in itertools.product(range(2000, 2005), range(1, 13)):
        y, m = utils.get_n_months_back(y1, m1, back=1)
        assert y == y1
        assert m == m1

    y, m = utils.get_n_months_back(2022, 12, back=3)
    assert y == 2022
    assert m == 10

    y, m = utils.get_n_months_back(2022, 2, back=3)
    assert y == 2021
    assert m == 12

    y, m = utils.get_n_months_back(2022, 12, back=6)
    assert y == 2022
    assert m == 7

    y, m = utils.get_n_months_back(2022, 4, back=6)
    assert y == 2021
    assert m == 11

    y, m = utils.get_n_months_back(2022, 12, back=9)
    assert y == 2022
    assert m == 4

    y, m = utils.get_n_months_back(2022, 6, back=9)
    assert y == 2021
    assert m == 10


def test_fill_year_month():
    test_str = 'YYYYMMMM'
    for year, month in itertools.product(range(1800, 2029), range(1, 13)):
        filled = utils.fill_year_month(test_str, year, month)
        assert filled == f'{year}{month:02d}'

    test_str = 'sfawefaergaergMMMMYYYYertftrhsr'
    for year, month in itertools.product(range(1800, 2029), range(1, 13)):
        filled = utils.fill_year_month(test_str, year, month)
        assert filled == f'sfawefaergaerg{month:02d}{year}ertftrhsr'
