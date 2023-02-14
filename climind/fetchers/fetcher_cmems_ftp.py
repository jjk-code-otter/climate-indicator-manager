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

import os
from dotenv import load_dotenv
from pathlib import Path
from ftplib import FTP

from climind.fetchers.fetcher_utils import get_ftp_host_and_directory_from_url


def fetch(url: str, out_dir: Path, _) -> None:
    """
    Fetch data from the CMEMS ftp system. Credentials required are

    * username, specified by entry in .env CMEMS_USER
    * password, specified by entry in .env CMEMS_PSWD

    Parameters
    ----------
    url: str
        The URL of the file to be downloaded
    out_dir: Path
        Path of the directory to which the files will be saved

    Returns
    -------
    None
    """
    load_dotenv()
    username = os.getenv('CMEMS_USER')
    password = os.getenv('CMEMS_PSWD')

    host, working_directory = get_ftp_host_and_directory_from_url(url)

    ftp = FTP(host)
    ftp.login(user=username, passwd=password)
    for sub_directory in working_directory:
        ftp.cwd(sub_directory)

    filelist = ftp.nlst()

    for file in filelist:
        out_path = out_dir / file
        with open(out_path, 'wb') as local_file:
            ftp.retrbinary(f'RETR {file}', local_file.write)

    ftp.quit()
