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
from urllib.parse import urlparse


def filename_from_url(url: str) -> str:
    """
    Given an url, return the filename or an empty string if there is no filename

    Parameters
    ----------
    url: str
        URL to be parsed

    Returns
    -------
    str
        Return the filename part of the URL

    """
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)

    return filename


def dir_and_filename_from_url(url: str):
    """
    Get the filename and url up to, but not including the filename

    Parameters
    ----------
    url : str

    Returns
    -------
    str, str
        Return directory name and filename
    """
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    dirname = parsed_url._replace(path=os.path.dirname(parsed_url.path)).geturl()

    return dirname, filename


def url_from_filename(url: str, filename: str):
    """
    Given an url and filename, replace the filename in the URL with the input filename

    Parameters
    ----------
    url : str
    filename : str

    Returns
    -------
    str
    -------

    """
    parsed_url = urlparse(url)
    dirname = os.path.dirname(parsed_url.path)
    path = f'{dirname}/{filename}'
    outurl = parsed_url._replace(path=path).geturl()
    return outurl


def get_ftp_host_and_directory_from_url(url):
    """
    From a url, extract the host name and the directory, the directory being
    broken down into a list of subdirectories

    Parameters
    ----------
    url: str
        URL to extract information from

    Returns
    -------
    str
        The host name
    list
        A list of directories
    """
    parsed_url = urlparse(url)

    working_directory = parsed_url.path

    working_directory = working_directory.split('/')
    working_directory = working_directory[1:-1]

    host = parsed_url.hostname

    return host, working_directory
