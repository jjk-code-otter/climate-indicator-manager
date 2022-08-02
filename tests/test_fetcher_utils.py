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
