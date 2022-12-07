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
"""
Set of scripts to download the JRA-55 gridded data. Adapted from the scripts
provided by UCAR. Data are stored by year up till a certain point and by
month for near-real time data thereafter. Credentials are needed (see fetch function)
"""
import itertools
from pathlib import Path
import sys
import os
import requests
from dotenv import load_dotenv
from typing import List

from climind.config.config import DATA_DIR


def check_file_status(file_path, file_size) -> None:
    """
    Writes a status bar on the download. Not used.

    Parameters
    ----------
    file_path: str
        Path of the file
    file_size: float
        Size of the file

    Returns
    -------
    None
    """
    sys.stdout.write('\r')
    sys.stdout.flush()
    size = int(os.stat(file_path).st_size)
    percent_complete = (size / file_size) * 100
    sys.stdout.write('%.3f %s' % (percent_complete, '% Completed'))
    sys.stdout.flush()


def make_realtime_file_list(first_year: int, final_year: int) -> List[str]:
    """
    Make a list of monthly real-time filenames between the two specified years.

    Parameters
    ----------
    first_year: int
        Year to start generation
    final_year: int
        Year to end generation

    Returns
    -------
    List[str]
        List of filenames for real-time data between the specified years
    """
    filelist = []
    for year, month in itertools.product(range(first_year, final_year + 1), range(1, 13)):
        filelist.append(f'anl_surf125/{year}{month:02d}/anl_surf125.{year}{month:02d}')
    return filelist


def make_file_list(first_year, final_year) -> List[str]:
    """
    Make a list of annual archived filenames between the two specified years.

    Parameters
    ----------
    first_year: int
        Year to start generation
    final_year: int
        Year to end generation

    Returns
    -------
    List[str]
        List of filenames for archived data between the specified years
    """
    filelist = []
    for year in range(first_year, final_year + 1):
        filelist.append(f'anl_surf125/{year}/anl_surf125.011_tmp.{year}01_{year}12')
    return filelist


def download_file(filename: str, file_base: str, ret) -> None:
    """
    Download a file.

    Parameters
    ----------
    filename: str
        URL of the file to be downloaded
    file_base: str
        Name of the output file to which the data will be written
    ret:
        Authentication information

    Returns
    -------
    None
    """
    req = requests.get(filename, cookies=ret.cookies, allow_redirects=True, stream=True)

    if req.status_code == 404:
        print("404 returned for ", file_base)
        return

    with open(file_base, 'wb') as outfile:
        chunk_size = 1048576
        for chunk in req.iter_content(chunk_size=chunk_size):
            outfile.write(chunk)


def get_files(filelist: str, web_path: str, ret) -> None:
    """
    For each file in a file list, check if it already exists on the system and if it does
    not, attempt to download it.

    Parameters
    ----------
    filelist: str
        List of files to be downloaded
    web_path: str
        URL of the directory that contains the files.
    ret:
        Authentication information

    Returns
    -------
    None
    """
    for file in filelist:
        filename = web_path + file
        file_base = DATA_DIR / "ManagedData" / "Data" / "JRA-55" / os.path.basename(file)

        if file_base.exists():
            print("File already downloaded", file_base)
        else:
            print('Downloading', file_base)
            download_file(filename, file_base, ret)


def fetch(_, out_dir: Path) -> None:
    """
    Get JRA-55 files from UCAR. Requires the credentials:

    * username, specified by entry in .env UCAR_USER
    * password, specified by entry in .env UCAR_PSWD


    Parameters
    ----------
    _:
        dummy input to match interface.
    out_dir: Path
        Path of the directory to which the output will be written.

    Returns
    -------
    None
    """
    load_dotenv()

    email = os.getenv('UCAR_EMAIL')
    password = os.getenv('UCAR_PSWD')

    url = 'https://rda.ucar.edu/cgi-bin/login'

    values = {'email': email, 'passwd': password, 'action': 'login'}
    # Authenticate
    ret = requests.post(url, data=values)
    if ret.status_code != 200:
        print('Bad Authentication')
        print(ret.text)
        exit(1)

    # Real time
    web_path = 'https://rda.ucar.edu/data/ds628.9/'
    filelist = make_realtime_file_list(2020, 2022)
    get_files(filelist, web_path, ret)

    web_path = 'https://rda.ucar.edu/data/ds628.1/'
    filelist = make_file_list(1958, 2020)
    get_files(filelist, web_path, ret)
