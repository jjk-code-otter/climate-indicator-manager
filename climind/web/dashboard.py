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

import json
from typing import Union
from pathlib import Path
from zipfile import ZipFile
from jinja2 import Environment, FileSystemLoader, select_autoescape

import climind.data_types.timeseries as ts
import climind.plotters.plot_types as pt
from climind.data_manager.processing import DataArchive
from climind.definitions import ROOT_DIR
from climind.config.config import DATA_DIR

DATA_DIR = DATA_DIR / "ManagedData" / "Data"


def process_single_dataset(ds: Union[ts.TimeSeriesAnnual, ts.TimeSeriesMonthly],
                           processing_steps: list):
    """
    Process the input data set using the methods and arguments provided in a list of processing steps.
    Each processing step is a dictionary containing a 'method' and an 'arguments' entry.

    Parameters
    ----------
    ds: ts.TimeSeriesAnnual or ts.TimeSeriesMonthly
        Data set to be processed
    processing_steps: list
        list of steps. Each step must be a dictionary containing a 'method' entry that corresponds to
        the name of a method in the timeseries class and a 'arguments' entry which contains a list
        of arguments for that method

    Returns
    -------
    ts.TimeSeriesAnnual or ts.TimeSeriesMonthly
    """
    for step in processing_steps:
        method = step['method']
        arguments = step['args']
        output = getattr(ds, method)(*arguments)
        if output is not None:
            ds = output
    return ds


class Card:

    def __init__(self, card_metadata):
        """
        A card is a single panel in a dashboard web page. The Card class manages the metadata
        associated with the card, and generates the files that are associated with it. These
        include the figure (in multiple formats) and the data files (in a zip archive)

        Parameters
        ----------
        card_metadata: dict
            dictionary containing the metadata for the card
        """
        self.metadata = card_metadata
        self.datasets = []

    def __getitem__(self, key):
        return self.metadata[key]

    def __setitem__(self, key, value):
        self.metadata[key] = value

    def process_card(self, data_dir, figure_dir, formatted_data_dir, archive):
        self.select_and_read_data(data_dir, archive)
        self.process_datasets()
        self.plot(figure_dir)
        self.make_zip_file(formatted_data_dir)

    def select_and_read_data(self, data_dir, archive):
        """
        Using the specified data archive, select the appropriate subset of data as specified in the card
        metadata and read in the data sets from the data_dir directory

        Parameters
        ----------
        data_dir: Path
            Path of the directory in which the data are to be found
        archive: DataArchive
            Archive of data used to select and populate the data sets

        Returns
        -------
        None
        """
        selection_metadata = {
            'type': 'timeseries',
            'variable': self['indicators'],
            'time_resolution': self['plot']
        }
        selected = archive.select(selection_metadata)
        self.datasets = selected.read_datasets(data_dir)

    def process_datasets(self):
        """
        Run the processing specified in the card metadata on each of the data sets.

        Returns
        -------
        None
        """
        processed_datasets = []
        pro_metadata = []
        for ds in self.datasets:
            ds = process_single_dataset(ds, self['processing'])
            processed_datasets.append(ds)
            pro_metadata.append({'name': ds.metadata['name'],
                                 'url': ds.metadata['url'],
                                 'citation': ds.metadata['citation'],
                                 'data_citation': ds.metadata['data_citation'],
                                 'acknowledgement': ds.metadata['acknowledgement']})

        self.datasets = processed_datasets
        self['dataset_metadata'] = pro_metadata

    def plot(self, figure_dir):
        """
        Plot the figure specified in the card metadata, output to the figure_dir directory

        Parameters
        ----------
        figure_dir: Path
            Path of the directory to which the figure should be written

        Returns
        -------
        None
        """
        # Plot the output and add figure name to card
        figure_name = f"{self['title']}.png".replace(" ", "_")
        plot_function = self['plotting']['function']
        plot_title = self['plotting']['title']

        if 'kwargs' in self['plotting']:
            kwargs = self['plotting']['kwargs']
            caption = getattr(pt, plot_function)(figure_dir, self.datasets, figure_name, plot_title, **kwargs)
        else:
            caption = getattr(pt, plot_function)(figure_dir, self.datasets, figure_name, plot_title)

        self['figure_name'] = figure_name
        self['caption'] = caption

    def make_csv_files(self, formatted_data_dir):
        csv_paths = []
        for ds in self.datasets:
            csv_filename = f"{ds.metadata['variable']}_{ds.metadata['name']}.csv".replace(" ", "_")
            csv_path = formatted_data_dir / csv_filename
            ds.write_csv(csv_path)
            csv_paths.append(csv_path)

        return csv_paths

    def make_zip_file(self, formatted_data_dir):
        """
        Create a formatted data file for each data set and zip these into a zip file

        Parameters
        ----------
        formatted_data_dir: Path
            Path of the directory to which the zip file and data files should be written

        Returns
        -------
        None
        """
        csv_paths = self.make_csv_files(formatted_data_dir)

        zipfile_name = f"{self['title']}_data_files.zip".replace(" ", "_")
        with ZipFile(formatted_data_dir / zipfile_name, 'w') as zip_archive:
            for csv_path in csv_paths:
                csv_filename = csv_path.name
                zip_archive.write(csv_path, arcname=csv_filename)
                csv_path.unlink()

        self['csv_name'] = zipfile_name


class Page:
    def __init__(self, metadata: dict):
        """
        A Page from a dashboard. A page contains multiple Cards, which are used to render a
        jinja2 template.

        Parameters
        ----------
        metadata: dict
            Dictionary containing the page metadata
        """
        self.metadata = metadata

    def __getitem__(self, key):
        return self.metadata[key]

    def __setitem__(self, key, value):
        self.metadata[key] = value

    def build(self, build_dir: Path, data_dir: Path, archive: DataArchive):
        figure_dir = build_dir / 'figures'
        figure_dir.mkdir(exist_ok=True)

        formatted_data_dir = build_dir / 'formatted_data'
        formatted_data_dir.mkdir(exist_ok=True)

        print(f"Building {self.metadata['id']} using template {self.metadata['template']}")

        processed_cards = []

        for card_metadata in self['cards']:
            this_card = Card(card_metadata)
            this_card.process_card(data_dir, figure_dir, formatted_data_dir, archive)
            processed_cards.append(this_card)

        # populate template to make webpage
        env = Environment(
            loader=FileSystemLoader(ROOT_DIR / "climind" / "web" / "jinja_templates"),
            autoescape=select_autoescape()
        )
        template = env.get_template(f"{self['template']}.html.jinja")
        with open(build_dir / f"{self['id']}.html", 'w') as out_file:
            out_file.write(template.render(cards=processed_cards, page_meta=self))


class Dashboard:

    def __init__(self, metadata: dict, archive: DataArchive):
        """
        Create a dashboard from a set of dashboard metadata

        Parameters
        ----------
        metadata: dict
            Dictionary containing the dashboard metadata
        archive: DataArchive
            Data archive that will be used to populate the dashboard
        """
        self.metadata = metadata
        self.archive = archive
        self.data_dir = DATA_DIR

        self.pages = []

        for page_metadata in self.metadata['pages']:
            self.pages.append(Page(page_metadata))

    @staticmethod
    def from_json(json_file: Path, archive_dir: Path):
        with open(json_file) as f:
            metadata = json.load(f)
        archive = DataArchive.from_directory(archive_dir)
        return Dashboard(metadata, archive)

    def build(self, build_dir: Path):
        """
        Build all the pages in the dashboard. This will create the html, the images,
        the formatted data in a chosen directory

        Parameters
        ----------
        build_dir: Path
            Path of the directory to build the web pages in
        Returns
        -------
        None
        """
        for page in self.pages:
            page.build(build_dir, self.data_dir, self.archive)