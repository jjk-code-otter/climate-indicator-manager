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
