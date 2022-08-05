import os
from pathlib import Path
import requests
from dotenv import load_dotenv
from climind.fetchers.fetcher_utils import filename_from_url
from climind.config.config import DATA_DIR


def fetch(url: str, outdir: Path):
    """
    Fetch files from the PODAAC website. Note that the API URL base is:
    API_url = "https://podaac-tools.jpl.nasa.gov/drive/files"

    Parameters
    ----------
    url: str
        URL for the file
    outdir: Path
        directory to which the file will be written.

    Returns
    -------
    None
    """
    load_dotenv()

    username = os.getenv('PODAAC_USER')
    password = os.getenv('PODAAC_PSWD')

    req = requests.get(url, auth=(username, password))

    filename = filename_from_url(url)
    filename = outdir / filename

    if req.status_code != 404:
        file_size = int(req.headers['Content-length'])
        with open(filename, 'wb') as outfile:
            chunk_size = 1048576
            for chunk in req.iter_content(chunk_size=chunk_size):
                outfile.write(chunk)
    else:
        print("404 returned for ", filename)
