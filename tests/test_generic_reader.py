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
from datetime import datetime
from climind.readers.generic_reader import read_ts, get_reader_script_name, get_module, get_last_modified_time
from climind.data_manager.processing import DataCollection


def test_get_last_modified(tmpdir):
    filename = Path(tmpdir) / 'test_file.txt'

    with open(filename, 'w') as f:
        f.write('test text')

    longtime = filename.stat().st_mtime
    last_updated_from_file = datetime.fromtimestamp(longtime).strftime("%Y-%m-%d %H:%M:%S")

    last_updated = get_last_modified_time(filename)

    assert last_updated == last_updated_from_file


def test_get_reader_script_name():
    metadata = {'type': 'timeseries', 'time_resolution': 'monthly'}
    test_script = get_reader_script_name(metadata)
    assert test_script == 'read_monthly_ts'

    metadata = {'type': 'timeseries', 'time_resolution': 'annual'}
    test_script = get_reader_script_name(metadata)
    assert test_script == 'read_annual_ts'

    metadata = {'type': 'gridded', 'time_resolution': 'monthly'}
    kwargs = {'grid_resolution': 1}
    test_script = get_reader_script_name(metadata, **kwargs)
    assert test_script == 'read_monthly_1x1_grid'

    metadata = {'type': 'gridded', 'time_resolution': 'monthly'}
    kwargs = {'grid_resolution': 5}
    test_script = get_reader_script_name(metadata, **kwargs)
    assert test_script == 'read_monthly_5x5_grid'

    test_script = get_reader_script_name(metadata)
    assert test_script == 'read_monthly_grid'


def test_get_module():
    test_module = get_module('climind.readers', 'generic_reader')
    assert test_module.read_ts == read_ts


@pytest.fixture
def generic_metadata():
    collection = DataCollection.from_file(Path('test_data') / 'hadcrut5.json')
    return collection.datasets[1].metadata


def test_read_ts_monthly_ts(generic_metadata):
    generic_metadata['reader'] = 'reader_test'
    generic_metadata['time_resolution'] = 'monthly'
    result = read_ts(Path(''), generic_metadata)
    assert result == 'monthly_ts'


def test_read_ts_annual_ts(generic_metadata):
    generic_metadata['reader'] = 'reader_test'
    result = read_ts(Path(''), generic_metadata)
    assert result == 'annual_ts'


def test_read_ts_monthly_grid(generic_metadata):
    generic_metadata['reader'] = 'reader_test'
    generic_metadata['type'] = 'gridded'
    generic_metadata['time_resolution'] = 'monthly'
    result = read_ts(Path(''), generic_metadata)
    assert result == 'monthly_grid'


def test_read_ts_monthly_1x1_grid(generic_metadata):
    generic_metadata['reader'] = 'reader_test'
    generic_metadata['type'] = 'gridded'
    kwargs = {'grid_resolution': 1}
    result = read_ts(Path(''), generic_metadata, **kwargs)
    assert result == 'monthly_1x1_grid'


def test_read_ts_monthly_5x5_grid(generic_metadata):
    generic_metadata['reader'] = 'reader_test'
    generic_metadata['type'] = 'gridded'
    kwargs = {'grid_resolution': 5}
    with pytest.raises(NotImplementedError):
        _ = read_ts(Path(''), generic_metadata, **kwargs)


def test_non_existent_combination(generic_metadata):
    generic_metadata['time_resolution'] = 'weekly'
    with pytest.raises(RuntimeError):
        _ = read_ts(Path(''), generic_metadata)
