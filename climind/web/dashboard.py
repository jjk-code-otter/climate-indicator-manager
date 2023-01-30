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
import hashlib
import pkg_resources
from datetime import datetime
from typing import Union, List
from pathlib import Path
from zipfile import ZipFile
from jinja2 import Environment, FileSystemLoader, select_autoescape

from climind.data_types.timeseries import TimeSeriesMonthly, TimeSeriesAnnual, TimeSeriesIrregular
import climind.plotters.plot_types as pt
import climind.stats.paragraphs as pa
from climind.data_manager.processing import DataArchive
from climind.definitions import ROOT_DIR
from climind.config.config import DATA_DIR

DATA_DIR = DATA_DIR / "ManagedData" / "Data"


def process_single_dataset(ds: Union[TimeSeriesAnnual, TimeSeriesMonthly],
                           processing_steps: list) -> Union[TimeSeriesAnnual, TimeSeriesMonthly]:
    """
    Process the input data set using the methods and arguments provided in a list of processing steps.
    Each processing step is a dictionary containing a 'method' and an 'arguments' entry.

    Parameters
    ----------
    ds: TimeSeriesAnnual or TimeSeriesMonthly
        Data set to be processed
    processing_steps: list
        list of steps. Each step must be a dictionary containing a 'method' entry that corresponds to
        the name of a method in the timeseries class and a 'arguments' entry which contains a list
        of arguments for that method

    Returns
    -------
    Union[TimeSeriesAnnual, TimeSeriesMonthly]
    """
    for step in processing_steps:
        method = step['method']
        arguments = step['args']
        output = getattr(ds, method)(*arguments)
        if output is not None:
            ds = output
    return ds


class WebComponent:

    def __init__(self, component_metadata: dict):
        self.metadata = component_metadata
        self.datasets = []

    def __getitem__(self, key):
        return self.metadata[key]

    def __setitem__(self, key, value):
        self.metadata[key] = value

    def select_and_read_data(self, data_dir: Path, archive: DataArchive):
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
        selection_metadata = self['selecting']
        selected = archive.select(selection_metadata)
        self.datasets = selected.read_datasets(data_dir)

    def process_datasets(self):
        """
        Apply the processing steps specified in the 'processing' section of the metadata file to
        all the data sets.

        Returns
        -------
        None
        """
        processed_datasets = []
        for ds in self.datasets:
            ds = process_single_dataset(ds, self['processing'])
            processed_datasets.append(ds)

        self.datasets = processed_datasets


class Paragraph(WebComponent):

    def __init__(self, paragraph_metadata: dict):
        super().__init__(paragraph_metadata)

    def process_paragraph(self, data_dir: Path, archive: DataArchive, focus_year: int = 2021):
        """
        Process and ultimately render the Paragraph object

        Parameters
        ----------
        data_dir: Path
            Path of the directory containing the data
        archive: DataArchive
            DataArchive object with the metadata describing all the datasets
        focus_year: int
            Year which the paragraph will focus on, usually the most recent year, though it needn't be.

        Returns
        -------

        """
        self.select_and_read_data(data_dir, archive)
        self.process_datasets()
        self.render(focus_year)

    def process_datasets(self):
        """
        Run the processing specified in the paragraph metadata on each of the data sets.

        Returns
        -------
        None
        """
        super().process_datasets()
        self['dataset_metadata'] = self.datasets[0].metadata

    def render(self, year: int = 2021):
        """
        Render out the text of the paragraph specified in the paragraph metadata.

        Parameters
        ----------
        year: int
            Year which is the focus of the paragraph.

        Returns
        -------
        None
        """
        # Plot the output and add figure name to card
        paragraph_function = self['writing']['function']

        if 'kwargs' in self['writing']:
            kwargs = self['writing']['kwargs']
            paragraph_text = getattr(pa, paragraph_function)(self.datasets, year, **kwargs)
        else:
            paragraph_text = getattr(pa, paragraph_function)(self.datasets, year)

        self['text'] = paragraph_text


class Card(WebComponent):

    def __init__(self, card_metadata: dict):
        """
        A card is a single panel in a dashboard web page. The Card class manages the metadata
        associated with the card, and generates the files that are associated with it. These
        include the figure (in multiple formats) and the data files (in a zip archive)

        Parameters
        ----------
        card_metadata: dict
            dictionary containing the metadata for the card
        """
        super().__init__(card_metadata)

    def process_card(self, data_dir: Path, figure_dir: Path, formatted_data_dir: Path, archive: DataArchive):
        """
        Process the datasets, plot them and write out the data based on the metadata in the Card

        Parameters
        ----------
        data_dir: Path
            Path of the directory in which the data are found.
        figure_dir: Path
            Path of the directory to which the figures will be written.
        formatted_data_dir: Path
            Path of the directory to which the formatted data will be written.
        archive: DataArchive
            DataArchive object containing the descriptive metadata.

        Returns
        -------
        None
        """
        self.select_and_read_data(data_dir, archive)
        self.process_datasets()
        self.plot(figure_dir)
        self.make_zip_file(formatted_data_dir)

    def process_datasets(self):
        """
        Run the processing specified in the card metadata on each of the data sets.

        Returns
        -------
        None
        """
        super().process_datasets()
        pro_metadata = []
        for ds in self.datasets:
            pro_metadata.append(
                {
                    'name': ds.metadata['name'],
                    'display_name': ds.metadata['display_name'],
                    'url': ds.metadata['url'],
                    'citation': ds.metadata['citation'],
                    'citation_url': ds.metadata['citation_url'],
                    'data_citation': ds.metadata['data_citation'],
                    'acknowledgement': ds.metadata['acknowledgement'],
                    'history': ds.metadata['history']
                }
            )

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

    def make_csv_files(self, formatted_data_dir: Path) -> List[Path]:
        """
        Make a csv file in the standard format for each data set in the Card and return a list of all then names
        of the csv files.

        Parameters
        ----------
        formatted_data_dir: Path
            Path of the directory to which the csv files will be written

        Returns
        -------
        List[Path]
            List containing a Path for each csv file written
        """
        csv_paths = []
        for ds in self.datasets:
            if (
                    isinstance(ds, TimeSeriesMonthly) or
                    isinstance(ds, TimeSeriesAnnual) or
                    isinstance(ds, TimeSeriesIrregular)
            ):
                csv_filename = f"{ds.metadata['variable']}_{ds.metadata['name']}.csv".replace(" ", "_")
                csv_path = formatted_data_dir / csv_filename
                ds.write_csv(csv_path)
                csv_paths.append(csv_path)

        return csv_paths

    def make_zip_file(self, formatted_data_dir: Path):
        """
        Create a formatted data file for each data set and zip these into a zip file. Adds a metadata element
        'csv_name' with the names of the zip file once it is created.

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

        with open(formatted_data_dir / zipfile_name, "rb") as f:
            gobbled_bytes = f.read()  # read file as bytes
            checksum = hashlib.md5(gobbled_bytes).hexdigest()

        self['csv_checksum'] = checksum
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

    def _process_cards(self, data_dir: Path, figure_dir: Path,
                       formatted_data_dir: Path, archive: DataArchive) -> List[Card]:
        """
        Process each of the cards on the page

        Parameters
        ----------
        data_dir: Path
            Path of the directory containing the data
        figure_dir: Path
            Path of directory to which figures will be written
        formatted_data_dir: Path
            Path of directory to which formatted data will be written
        archive: DataArchive
            Archive which contains all the metadata for this selection

        Returns
        -------
        List[Card]
            List of the processed Cards
        """
        processed_cards = []
        for card_metadata in self['cards']:
            this_card = Card(card_metadata)
            this_card.process_card(data_dir, figure_dir, formatted_data_dir, archive)
            processed_cards.append(this_card)
        return processed_cards

    def _process_paragraphs(self, data_dir: Path, archive: DataArchive, focus_year: int = 2021) -> List[Paragraph]:
        """
        Process each of the paragraphs on the page

        Parameters
        ----------
        data_dir: Path
            Path of the directory containing the data
        archive: DataArchive
            Archive which contains all the metadata for this selection
        focus_year: int
            Year to focus on

        Returns
        -------
        List[Paragraph]
            List of the processed Cards
        """
        processed_paragraphs = []
        for paragraph_metadata in self['paragraphs']:
            this_paragraph = Paragraph(paragraph_metadata)
            this_paragraph.process_paragraph(data_dir, archive, focus_year=focus_year)
            processed_paragraphs.append(this_paragraph)
        return processed_paragraphs

    def build(self, build_dir: Path, data_dir: Path, archive: DataArchive,
              focus_year: int = 2021, menu_items: List[List[str]] = []):
        """
        Build the Page, processing all the Card and Paragraph objects, then populating the template
        to generate a webpage, figures and formatted data.

        Parameters
        ----------
        build_dir: Path
            Path of the directory to which the html, figures and data will be written
        data_dir: Path
            Path of the directory where the data are to be found.
        archive: DataArchive
            DataArchive containing the metadata for the datasets
        focus_year: int
            Year to focus on. Usually, this will be the latest year
        menu_items: List[List[str]]
            List of items to display in the menu. Each item is a two element list, with the name of the webpage as
            the first element (which gets a .html extension) and the title of the page as the second elements. The
            title is used to generate the menu items so should be human readable.

        Returns
        -------
        None
        """
        figure_dir = build_dir / 'figures'
        figure_dir.mkdir(exist_ok=True)

        formatted_data_dir = build_dir / 'formatted_data'
        formatted_data_dir.mkdir(exist_ok=True)

        print(f"Building {self.metadata['id']} using template {self.metadata['template']}")

        processed_cards = self._process_cards(data_dir, figure_dir, formatted_data_dir, archive)
        processed_paragraphs = self._process_paragraphs(data_dir, archive, focus_year=focus_year)

        now = datetime.today()
        climind_version = pkg_resources.get_distribution("climind").version

        self['created'] = f'{now.year}-{now.month:02d}-{now.day:02d}'
        self['code_version'] = f'climind v{climind_version}'

        # populate template to make webpage
        env = Environment(
            loader=FileSystemLoader(ROOT_DIR / "climind" / "web" / "jinja_templates"),
            autoescape=select_autoescape()
        )
        template = env.get_template(f"{self['template']}.html.jinja")
        with open(build_dir / f"{self['id']}.html", 'w') as out_file:
            out_file.write(template.render(cards=processed_cards,
                                           paragraphs=processed_paragraphs,
                                           page_meta=self,
                                           menu_items=menu_items))


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
        """
        Create a Dashboard from a json file and directory containing dataset metadata

        Parameters
        ----------
        json_file: Path
            Path to the json file
        archive_dir: Path
            Path of the directory which contains the dataset metadata

        Returns
        -------
        Dashboard
        """
        with open(json_file) as f:
            metadata = json.load(f)
        archive = DataArchive.from_directory(archive_dir)
        return Dashboard(metadata, archive)

    def build(self, build_dir: Path, focus_year: int = 2021):
        """
        Build all the pages in the dashboard. This will create the html, the images,
        the formatted data in a chosen directory

        Parameters
        ----------
        build_dir: Path
            Path of the directory to build the web pages in
        focus_year: int
            Year to focus on. Usually, this will be the latest year
        Returns
        -------
        None
        """
        page_ids = []
        for page in self.pages:
            page_ids.append([page['id'], page['name']])

        for page in self.pages:
            page.build(build_dir, self.data_dir, self.archive,
                       focus_year=focus_year,
                       menu_items = page_ids)
