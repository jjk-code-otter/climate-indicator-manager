#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2024 John Kennedy
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
import numpy as np

import climind.stats.utils as utils

def test_get_latitudes():

    lats = utils.get_latitudes(1.0)
    assert len(lats) == 180
    assert lats[0] == -89.5
    assert lats[-1] == 89.5

    lats = utils.get_latitudes(5.0)
    assert len(lats) == 36
    assert lats[0] == -87.5
    assert lats[-1] == 87.5

def test_get_n_years_from_n_months():

    month = 12
    year = -1

    for n_months in range(200):
        month += 1
        if month > 12:
            month = 1
            year += 1

        n_years = utils.get_n_years_from_n_months(n_months)
        assert year == n_years

    assert utils.get_n_years_from_n_months(1) == 0
    assert utils.get_n_years_from_n_months(12) == 1
    assert utils.get_n_years_from_n_months(13) == 1
    assert utils.get_n_years_from_n_months(24) == 2
    assert utils.get_n_years_from_n_months(29) == 2


def test_monthly_to_annual():

    monthly_means = np.zeros((24,3))
    monthly_means[:,0] = np.arange(0.0, 24.0, 1.0)
    monthly_means[:,1] = np.arange(0.0, 24.0, 1.0)
    monthly_means[:,2] = np.arange(0.0, 24.0, 1.0)

    annual_means = utils.monthly_to_annual_array(monthly_means)

    for i in range(3):
        assert annual_means[0,i] == 66.0/12.
        assert annual_means[1,i] == 66.0/12. + 12.


def test_rolling_average():
    input_array = np.arange(0.0, 200.0, 1.0)

    rolled_array = utils.rolling_average(input_array,10)

    for i in range(4):
        assert np.isnan(rolled_array[i])

    for i in range(6):
        assert np.isnan(rolled_array[-1*i])

    assert rolled_array[4] == 45./10.
    assert rolled_array[-6] == 45./10. + 190.