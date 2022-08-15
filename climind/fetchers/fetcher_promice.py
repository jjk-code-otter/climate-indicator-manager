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

from pathlib import Path
import requests
import shutil
from bs4 import BeautifulSoup, SoupStrainer


def fetch(url: str, outdir: Path):
    # First open up the landing page
    landing_page_url = "https://dataverse.geus.dk/api/datasets/:persistentId/dirindex?persistentId=doi:10.22008/FK2/OHI23Z"
    landing_page_request = requests.get(landing_page_url, stream=True, headers={'User-agent': 'Mozilla/5.0'})

    # Next scan through the landing page to find the links to the required files. The ULRs for these change, but
    # the contents of the <a> tags remains the same.
    for link in BeautifulSoup(landing_page_request.text, "html.parser", parse_only=SoupStrainer('a')):

        if ('MB_SMB_D_BMB.csv' in link.contents or
                'MB_SMB_D_BMB_ann.csv' in link.contents):

            # File number is the number after the last slash in the API call in the <a> tag
            file_number = link['href'].split('/')[-1]
            filename = link.contents[0]

            file_url = f"{url}/{file_number}"
            out_path = outdir / filename

            # Setp up a request for the latest version of the target file
            file_request = requests.get(file_url, stream=True, headers={'User-agent': 'Mozilla/5.0'})

            if file_request.status_code == 200:
                with open(out_path, 'wb') as f:
                    file_request.raw.decode_content = True
                    shutil.copyfileobj(file_request.raw, f)
