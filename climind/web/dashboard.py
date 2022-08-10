import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

from climind.definitions import ROOT_DIR


#class Card:
#
#    def __init__(self):
#        self.variable = None


class Page:

    def __init__(self, metadata: dict):
        self.metadata = metadata

    def __getitem__(self, key):
        return self.metadata[key]

    def __setitem__(self, key, value):
        self.metadata[key] = value

    def build(self, build_dir: Path):
        print(f"Building {self.metadata['id']} using template {self.metadata['template']}")

        indicators = []

        for i, indicator in enumerate(self.metadata['indicators']):

            link_to = self.metadata['links'][i]

            print(f"with indicator {indicator} linked to {link_to}")
            indicators.append({'indicator': indicator, 'link_to': link_to})

        # populate template
        env = Environment(
            loader=FileSystemLoader(ROOT_DIR / "climind" / "web" / "jinja_templates"),
            autoescape=select_autoescape()
        )

        template = env.get_template(f"{self['template']}.html.jinja")
        print(template.render(indicators=indicators, a_variable='dingo'))

        # generate images

        # generate formatted data

        #
        pass


class Dashboard:

    def __init__(self, metadata: dict):
        self.metadata = metadata
        self.pages = []

        for page_metadata in self.metadata['pages']:
            self.pages.append(Page(page_metadata))

    @staticmethod
    def from_json(json_file):
        with open(json_file) as f:
            metadata = json.load(f)

        return Dashboard(metadata)

    def build(self, build_dir):
        """
        Build all the pages

        Parameters
        ----------
        build_dir

        Returns
        -------

        """
        for page in self.pages:
            page.build(build_dir)
