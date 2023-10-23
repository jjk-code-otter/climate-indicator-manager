#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2023 John Kennedy
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

from pathlib import Path
from typing import Tuple


def find_latest(out_dir: Path, filename_with_wildcards: str) -> Path:
    """
    Find the most recent file that matches

    Parameters
    ----------
    filename_with_wildcards : str
        Filename including wildcards
    out_dir : Path
        Path of data directory

    Returns
    -------
    Path
        Path of latest file that matches the filename with wildcards in the directory
    """
    # look in directory to find all matching
    list_of_files = list(out_dir.glob(filename_with_wildcards))
    list_of_files.sort()
    out_filename = list_of_files[-1]
    return out_filename


def get_latest_filename_and_url(filename: Path, url: str) -> Tuple[str, str]:
    """
    Get the filename and url from a filled filename Path and URL with placeholders

    Parameters
    ----------
    filename: Path
        Path of filename
    url: str
        URL to be replaced

    Returns
    -------
    Tuple[str, str]
        The filename and the url with placeholders replaced
    """
    selected_file = filename.name
    selected_url = url.split('/')
    selected_url = selected_url[0:-1]
    selected_url.append(selected_file)
    selected_url = '/'.join(selected_url)

    return selected_file, selected_url
