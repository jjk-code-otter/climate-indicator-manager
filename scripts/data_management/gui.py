#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2025 John Kennedy
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
from pathlib import Path
import os
from tkinter import *
from tkinter import ttk

import climind.data_manager.processing as dm
from climind.config.config import DATA_DIR

ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
METADATA_DIR = (ROOT_DIR / "..").resolve() / "climind" / "metadata_files"
OUT_DIR = DATA_DIR / "ManagedData" / "Data"


class MetadataBrowser:

    def __init__(self, root):

        root.title("Data Manager")

        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        self.archive = dm.DataArchive.from_directory(METADATA_DIR)
        self.display_archive = self.archive.select({})

        self.choices = [name for name in self.display_archive.collections.keys()]
        self.choicesvar = StringVar(value=self.choices)
        datasest_list = Listbox(mainframe, height=30, width=30, listvariable=self.choicesvar)

        self.selected_dataset = StringVar()

        datasest_list.grid(column=1, row=1, sticky=(W, E))

        datasest_list.bind("<<ListboxSelect>>", lambda e: self.updateDetails(datasest_list.curselection()))

        self.meters = StringVar()

        ttk.Button(mainframe, text="Get data", command=self.get_data).grid(column=3, row=3, sticky=W)

        self.text = Text(mainframe, width=60, height=30)
        self.text.insert('1.0', "")
        self.text.grid(column=3, row=1, sticky=W)

        self.ts = StringVar(value='false')
        ttk.Checkbutton(
            mainframe, text="Time Series", variable=self.ts, command=self.updateDatasetList,
            onvalue='true', offvalue='false'
        ).grid(column=1, row=3, sticky=S)

        self.gd = StringVar(value='false')
        ttk.Checkbutton(
            mainframe, text="Gridded", variable=self.gd, command=self.updateDatasetList,
            onvalue='true', offvalue='false'
        ).grid(column=2, row=3, sticky=S)

        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        datasest_list.focus()
        # root.bind("<Return>", self.get_data)

    def updateDatasetList(self):
        types = []
        if self.ts.get() == 'true':
            types.append('timeseries')
        if self.gd.get() == 'true':
            types.append('gridded')

        selection_dict = {}

        if len(types) > 0:
            selection_dict['type'] = types

        self.display_archive = self.archive.select(selection_dict)
        self.choices = [name for name in self.display_archive.collections.keys()]
        self.choicesvar.set(value=self.choices)


    def updateDetails(self, in_index):
        try:
            self.selected_dataset.set(self.choices[in_index[0]])
            metadata = self.display_archive.collections[self.choices[in_index[0]]]
            self.text.delete("1.0", END)
            self.text.insert('1.0', f'{metadata}')
        except IndexError:
            pass

    def get_data(self, *args):
        try:
            self.display_archive.collections[self.selected_dataset.get()].download(OUT_DIR)
        except Exception as e:
            print(e)


root = Tk()
MetadataBrowser(root)
root.mainloop()
