"""
This script calculates various statistics of global mean temperatures using monthly averages.
Each month (jan, feb .. .dec) is treated separately to show how trend vs variability changes
through the year. It also makes plots of these data in a variety of styles.
"""
import logging
from pathlib import Path

import climind.data_manager.processing as dm
import climind.plotters.plot_types as pt

from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR

if __name__ == "__main__":

    final_year = 2022

    project_dir = DATA_DIR / "ManagedData"
    metadata_dir = METADATA_DIR

    data_dir = project_dir / "Data"
    figure_dir = project_dir / 'Figures'
    log_dir = project_dir / 'Logs'
    report_dir = project_dir / 'Reports'
    report_dir.mkdir(exist_ok=True)

    script = Path(__file__).stem
    logging.basicConfig(filename=log_dir / f'{script}.log',
                        filemode='w', level=logging.INFO)

    # Read in the whole archive then select the various subsets needed here
    archive = dm.DataArchive.from_directory(metadata_dir)

    holdall = {
        'ohc': [
            {'variable': 'ohc',
             'type': 'timeseries',
             'time_resolution': 'annual'},
            'Ocean heat content'
        ],
        'mhw': [
            {'variable': 'mhw',
             'type': 'timeseries',
             'time_resolution': 'annual'},
            'Marine heat wave (% global ocean area)'
        ],
        'mcs': [
            {'variable': 'mcs',
             'type': 'timeseries',
             'time_resolution': 'annual'},
            'Marine cold spell (% global ocean area)'
        ],
        'sealevel': [
            {'variable': 'sealevel',
             'type': 'timeseries',
             'time_resolution': 'monthly'},
            'Sea level (mm)'
        ],
        'co2': [
            {'variable': 'co2',
             'type': 'timeseries',
             'time_resolution': 'monthly'},
            'Atmospheric concentration of Carbon Dioxide'
        ],
        'ch4': [
            {'variable': 'ch4',
             'type': 'timeseries',
             'time_resolution': 'monthly'},
            'Atmospheric concentration of Methane'
        ],
        'n2o': [
            {'variable': 'n2o',
             'type': 'timeseries',
             'time_resolution': 'monthly'},
            'Atmospheric concentration of Nitrous Oxide'
        ],
        'arctic_ice': [
            {'variable': 'arctic_ice',
             'type': 'timeseries',
             'time_resolution': 'monthly'},
            'Arctic sea-ice extent'

        ],
        'antarctic_ice': [
            {'variable': 'antarctic_ice',
             'type': 'timeseries',
             'time_resolution': 'monthly'},
            'Antarctic sea-ice extent'

        ],
        'greenland': [
            {'variable': 'greenland',
             'type': 'timeseries',
             'time_resolution': 'monthly'},
            'Greenland mass balance'
        ],
        'antarctica': [
            {'variable': 'antarctica',
             'type': 'timeseries',
             'time_resolution': 'monthly'},
            'Antarctic mass balance'
        ],
        'ph': [
            {'variable': 'ph',
             'type': 'timeseries',
             'time_resolution': 'annual'},
            'Ocean pH'
        ]
    }

    for combo in holdall:

        selection_metadata = holdall[combo][0]
        variable = selection_metadata['variable']
        plot_title = holdall[combo][1]
        time_resolution = selection_metadata['time_resolution']

        ts_archive = archive.select(selection_metadata)
        all_datasets = ts_archive.read_datasets(data_dir)

        m = []
        for ds in all_datasets:
            # ds.select_year_range(1980, 2022)
            if variable in ['arctic_ice', 'antarctic_ice', 'ohc']:
                ds.rebaseline(1981, 2010)
            if variable in ['antarctica']:
                ds.zero_on_month(2005, 6)
            if variable in ['greenland']:
                ds.zero_on_month(2005, 7)
            m.append(ds)
        if time_resolution == 'monthly':
            pt.monthly_plot(figure_dir, m, f'{variable}_monthly.png', plot_title)
        else:
            pt.neat_plot(figure_dir, m, f'{variable}_annual.png', plot_title)