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

from setuptools import setup

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='Climind',
    url='https://github.com/jjk-code-otter/climate-indicator-manager',
    author='John Kennedy',
    author_email='jjk.code.otter@gmail.com',
    # Needed to actually package something
    packages=['climind', 'climind.config', 'climind.data_manager', 'climind.data_types',
              'climind.fetchers', 'climind.plotters', 'climind.readers', 'climind.stats',
              'climind.web'],
    # Needed for dependencies
    install_requires=['pytest', 'numpy', 'requests', 'beautifulsoup4',
                      'pandas', 'jsonschema', 'matplotlib', 'seaborn', 'xarray',
                      'python-dotenv', 'regionmask', 'geopandas', 'shapely',
                      'cdsapi', 'cartopy', 'cftime', 'jinja2', 'python-docx'],
# =======
#     install_requires=['pytest==7.1.1', 'requests==2.24.0',
#                       'beautifulsoup4==4.10.0',
#                       'pandas==1.3.4', 'jsonschema==4.7.1', 'matplotlib==3.3.1',
#                       'seaborn==0.11.2', 'xarray==0.20.2',
#                       'python-dotenv==0.20.0', 'regionmask==0.9.0', 'geopandas==0.9.0',
#                       'shapely==1.7.1',
#                       'cdsapi==0.5.1', 'cartopy==0.18.0', 'cftime==1.5.1.1',
#                       'jinja2==3.0.3', 'python-docx==0.8.11'],
# >>>>>>> parent of 9ce3864 (add requirements)
    # version number
    version='0.1',
    # The license can be anything you like
    license='GNU General Public License v3.0',
    description='A python package for managing climate indicator information',
    # We will also need a readme eventually (there will be a warning)
    long_description=open('README.md').read(),
    include_package_data=True,
)
