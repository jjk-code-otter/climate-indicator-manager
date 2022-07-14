import cdsapi
from pathlib import Path
from datetime import datetime


def pick_months(year: int, now: datetime):
    """
    For a given year, return a list of strings containing the months which are available in the
    CDS for ERA5. For years before the current year, return all months. For the current year
    return all months up to last month, but only include last month if the day of the month is
    after the 7th

    Parameters
    ----------
    year
    now

    Returns
    -------

    """
    if year < now.year:
        months_to_download = [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
            '10', '11', '12',
        ]
    else:
        months_to_download = []
        for m in range(1, now.month):
            if (m < now.month - 1) or (m == now.month - 1 and now.day > 6):
                months_to_download.append(f'{m:02d}')

    return months_to_download


def fetch_year(outdir: Path, year: int):
    """
    Fetch a specified year of data and write it to the outdir. If the year is
    incomplete, only recover available months.

    Parameters
    ----------
    outdir directory to which the data will be written
    year the year of data we want

    Returns
    -------

    """
    outputfile = outdir / f'era5_2m_tas_{year}.nc'

    now = datetime.now()

    if outputfile.exists() and year != now.year:
        print(f'File for {year} already exists, not downloading')
        return

    months_to_download = pick_months(year, now)

    if len(months_to_download) == 0:
        print(f'No months available for {year}')
        return

    print(f'Downloading file for {year}')
    print(str(outputfile))
    c = cdsapi.Client()

    c.retrieve(
        'reanalysis-era5-single-levels-monthly-means',
        {
            'product_type': 'monthly_averaged_reanalysis',
            'variable': '2m_temperature',
            'year': [str(year)],
            'month': months_to_download,
            'time': '00:00',
            'format': 'netcdf',
        },
        str(outputfile))


def fetch(url: str, outdir: Path):
    for year in range(1979, 2023):
        fetch_year(outdir, year)
