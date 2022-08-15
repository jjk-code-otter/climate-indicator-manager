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

import climind.fetchers.fetcher_utils as utils


def test_get_filename_from_url():
    url = 'http://www.doesntexist.boom/directory/filename.txt'
    filename = utils.filename_from_url(url)
    assert filename == 'filename.txt'


def test_get_filename_from_url_ftp():
    url = 'ftp://old.school/directory/ftp_filename.txt'
    filename = utils.filename_from_url(url)
    assert filename == 'ftp_filename.txt'


def test_get_filename_from_url_no_filename():
    url = 'http://www.doesntexist.boom/directory/'
    filename = utils.filename_from_url(url)
    assert filename == ''


def test_dir_and_filename():
    url = 'http://www.doesntexist.boom/directory/filename.txt'
    test_dir, filename = utils.dir_and_filename_from_url(url)
    assert filename == 'filename.txt'
    assert test_dir == 'http://www.doesntexist.boom/directory'


def test_url_from_filename():
    url = 'http://www.doesntexist.boom/directory/filename.txt'
    fixed_url = utils.url_from_filename(url, 'new_filename.txt')
    assert fixed_url == 'http://www.doesntexist.boom/directory/new_filename.txt'


def test_get_ftp_host_and_directory():
    url = 'fpt://the.host.name/directory0/directory1/directory2/filename.txt'
    host, working_directory = utils.get_ftp_host_and_directory_from_url(url)

    assert host == 'the.host.name'
    for i in range(3):
        assert working_directory[i] == f'directory{i}'
