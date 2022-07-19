import argparse
import itertools
from pathlib import Path
import sys
import os
import requests
from dotenv import load_dotenv
from climind.config.config import DATA_DIR


def check_file_status(filepath, filesize):
    sys.stdout.write('\r')
    sys.stdout.flush()
    size = int(os.stat(filepath).st_size)
    percent_complete = (size / filesize) * 100
    sys.stdout.write('%.3f %s' % (percent_complete, '% Completed'))
    sys.stdout.flush()


def fetch(url: str, outdir: Path):
    load_dotenv()

    email = os.getenv('UCAR_EMAIL')
    pswd = os.getenv('UCAR_PSWD')

    url = 'https://rda.ucar.edu/cgi-bin/login'

    values = {'email': email, 'passwd': pswd, 'action': 'login'}
    # Authenticate
    ret = requests.post(url, data=values)
    if ret.status_code != 200:
        print('Bad Authentication')
        print(ret.text)
        exit(1)

    # Real time
    dspath = 'https://rda.ucar.edu/data/ds628.9/'

    filelist = []
    for year, month in itertools.product(range(2020, 2023), range(1, 13)):
        filelist.append(f'anl_surf125/{year}{month:02d}/anl_surf125.{year}{month:02d}')

    for file in filelist:
        filename = dspath + file
        file_base = os.path.basename(file)
        file_base = DATA_DIR / "ManagedData" / "Data" / "JRA-55" / file_base

        if file_base.exists():
            print("File already downloaded", file_base)
        else:
            print('Downloading', file_base)
            req = requests.get(filename, cookies=ret.cookies, allow_redirects=True, stream=True)

            if req.status_code != 404:
                filesize = int(req.headers['Content-length'])
                with open(file_base, 'wb') as outfile:
                    chunk_size = 1048576
                    for chunk in req.iter_content(chunk_size=chunk_size):
                        outfile.write(chunk)
                        if chunk_size < filesize:
                            check_file_status(file_base, filesize)
                check_file_status(file_base, filesize)
                print()
            else:
                print("404 returned for ", file_base)

    # Non-realtime
    dspath = 'https://rda.ucar.edu/data/ds628.1/'

    filelist = []
    for year in range(1958, 2021):
        filelist.append(f'anl_surf125/{year}/anl_surf125.011_tmp.{year}01_{year}12')

    for file in filelist:
        filename = dspath + file
        file_base = os.path.basename(file)
        file_base = DATA_DIR / "ManagedData" / "Data" / "JRA-55" / file_base

        if file_base.exists():
            print("File already downloaded", file_base)
        else:
            print('Downloading', file_base)
            req = requests.get(filename, cookies=ret.cookies, allow_redirects=True, stream=True)

            if req.status_code != 404:
                filesize = int(req.headers['Content-length'])
                with open(file_base, 'wb') as outfile:
                    chunk_size = 1048576
                    for chunk in req.iter_content(chunk_size=chunk_size):
                        outfile.write(chunk)
                        if chunk_size < filesize:
                            check_file_status(file_base, filesize)
                check_file_status(file_base, filesize)
                print()
            else:
                print("404 returned for ", file_base)
