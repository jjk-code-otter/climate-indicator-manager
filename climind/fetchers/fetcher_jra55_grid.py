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
from pathlib import Path
import sys
import os
import requests
from dotenv import load_dotenv
from climind.config.config import DATA_DIR


def check_file_status(file_path, file_size):
    sys.stdout.write('\r')
    sys.stdout.flush()
    size = int(os.stat(file_path).st_size)
    percent_complete = (size / file_size) * 100
    sys.stdout.write('%.3f %s' % (percent_complete, '% Completed'))
    sys.stdout.flush()


def make_realtime_file_list(y1, y2):
    filelist = []
    for year, month in itertools.product(range(y1, y2 + 1), range(1, 13)):
        filelist.append(f'anl_surf125/{year}{month:02d}/anl_surf125.{year}{month:02d}')
    return filelist


def make_file_list(y1, y2):
    filelist = []
    for year in range(y1, y2 + 1):
        filelist.append(f'anl_surf125/{year}/anl_surf125.011_tmp.{year}01_{year}12')
    return filelist


def download_file(filename, file_base, ret):
    req = requests.get(filename, cookies=ret.cookies, allow_redirects=True, stream=True)

    if req.status_code == 404:
        print("404 returned for ", file_base)
        return

    with open(file_base, 'wb') as outfile:
        chunk_size = 1048576
        for chunk in req.iter_content(chunk_size=chunk_size):
            outfile.write(chunk)


def get_files(filelist, web_path, ret):
    for file in filelist:
        filename = web_path + file
        file_base = DATA_DIR / "ManagedData" / "Data" / "JRA-55" / os.path.basename(file)

        if file_base.exists():
            print("File already downloaded", file_base)
        else:
            print('Downloading', file_base)
            download_file(filename, file_base, ret)


def fetch(_, out_dir: Path):
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
