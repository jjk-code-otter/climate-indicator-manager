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

def read_monthly_ts(filename, metadata, **kwargs):
    return 'monthly_ts'


def read_annual_ts(filename, metadata, **kwargs):
    return 'annual_ts'


def read_monthly_grid(filename, metadata, **kwargs):
    return 'monthly_grid'


def read_monthly_1x1_grid(filename, metadata, **kwargs):
    return 'monthly_1x1_grid'
