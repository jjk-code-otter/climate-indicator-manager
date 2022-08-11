import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

import climind.plotters.plot_types as pt
import climind.data_types.timeseries as ts
from climind.data_manager.processing import DataArchive
from climind.definitions import ROOT_DIR
from climind.config.config import DATA_DIR

DATA_DIR = DATA_DIR / "ManagedData" / "Data"


class Page:

    def __init__(self, metadata: dict):
        self.metadata = metadata

    def __getitem__(self, key):
        return self.metadata[key]

    def __setitem__(self, key, value):
        self.metadata[key] = value

    def build(self, build_dir: Path, archive: DataArchive):
        figure_dir = build_dir / 'figures'
        figure_dir.mkdir(exist_ok=True)

        formatted_data_dir = build_dir / 'formatted_data'
        formatted_data_dir.mkdir(exist_ok=True)

        print(f"Building {self.metadata['id']} using template {self.metadata['template']}")

        for card in self['cards']:

            indicator = card['indicators']
            link_to = card['link_to']
            plot_type = card['plot']
            processing = card['processing']

            # Select and load data sets in archive
            selection_metadata = {
                'type': 'timeseries',
                'variable': indicator,
                'time_resolution': plot_type
            }
            selected = archive.select(selection_metadata)
            selected_datasets = selected.read_datasets(DATA_DIR)

            # Apply processing steps to each dataset
            processed_datasets = []
            for ds in selected_datasets:
                for step in processing:
                    method = step['method']
                    arguments = step['args']
                    output = getattr(ds, method)(*arguments)
                    if output is not None:
                        ds = output
                processed_datasets.append(ds)

            # Plot the output and add figure name to card
            figure_name = f'{indicator}.png'
            plot_function = card['plotting']['function']
            plot_title = card['plotting']['title']
            getattr(pt, plot_function)(figure_dir, processed_datasets, figure_name, plot_title)
            card['figure_name'] = figure_name

            for ds in processed_datasets:
                csv_filename = f"{indicator}_{ds.metadata['name']}.csv"
                ds.write_csv(formatted_data_dir / csv_filename)

            card['csv_name'] = csv_filename

        # populate template to make webpage
        env = Environment(
            loader=FileSystemLoader(ROOT_DIR / "climind" / "web" / "jinja_templates"),
            autoescape=select_autoescape()
        )
        template = env.get_template(f"{self['template']}.html.jinja")
        with open(build_dir / f"{self['id']}.html", 'w') as out_file:
            out_file.write(template.render(cards=self['cards'], page_meta=self))


class Dashboard:

    def __init__(self, metadata: dict, archive: DataArchive):
        """
        Create a dashboard from a set of dashboard metadata

        Parameters
        ----------
        metadata
        archive
        """
        self.metadata = metadata
        self.archive = archive

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
            page.build(build_dir, self.archive)
