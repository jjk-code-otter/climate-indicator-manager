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
import climind.stats.paragraphs as pg


def test_rank_ranges():
    test_text = pg.rank_ranges(1, 4)
    assert test_text == 'between the 1st and 4th'

    test_text = pg.rank_ranges(4, 1)
    assert test_text == 'between the 1st and 4th'

    test_text = pg.rank_ranges(3, 3)
    assert test_text == 'the 3rd'


class Tiny:
    def __init__(self, number):
        self.metadata = {'display_name': f'{number}'}


def test_dataset_name_list():
    all_datasets = []
    for i in range(1, 5):
        all_datasets.append(Tiny(i))
    test_text = pg.dataset_name_list(all_datasets)
    assert test_text == '1, 2, 3, and 4'

    all_datasets = []
    for i in range(1, 2):
        all_datasets.append(Tiny(i))
    test_text = pg.dataset_name_list(all_datasets)
    assert test_text == '1'

    all_datasets = []
    for i in range(1, 3):
        all_datasets.append(Tiny(i))
    test_text = pg.dataset_name_list(all_datasets)
    assert test_text == '1 and 2'


def test_fancy_units():
    assert pg.fancy_html_units('degC') == '&deg;C'
    assert pg.fancy_html_units('numpty') == 'numpty'
