import os
from dotenv import load_dotenv
from pathlib import Path
from ftplib import FTP

from climind.fetchers.fetcher_utils import get_ftp_host_and_directory_from_url


def fetch(url: str, out_dir: Path):
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
