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

import unicodedata
from pathlib import Path
from docx import Document
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn

import re

Paragraph.text = property(lambda self: GetParagraphText(self))


def GetParagraphText(paragraph):
    def GetTag(element):
        return "%s:%s" % (element.prefix, re.match("{.*}(.*)", element.tag).group(1))

    text = ''
    runCount = 0
    linkCount = 0
    for child in paragraph._p:
        tag = GetTag(child)
        if tag == "w:r":
            text += paragraph.runs[runCount].text
            runCount += 1
        if tag == "w:hyperlink":
            for subChild in child:
                if GetTag(subChild) == "w:r":
                    text += f"|{linkCount}|"

    return text


def split_document(document_name):
    document = Document(document_name)

    headings = []
    text_blocks = []
    new_block = []

    for paragraph in document.paragraphs:

        paragraph_links = []
        for link in paragraph._element.xpath(".//w:hyperlink"):
            inner_run = link.xpath("w:r")[0]#, namespaces=link.nsmap)[0]
            link_text = inner_run.text
            rId = link.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
            link_url = document._part.rels[rId]._target
            paragraph_links.append(f'<a href="{link_url}" target="_blank"  rel="noopener">{link_text}</a>')

        if paragraph.style.name == "Heading 1":
            headings.append(paragraph.text)

            if len(new_block) > 0:
                consolidated = ''.join(new_block)
                text_blocks.append(consolidated)

            new_block = []

        elif paragraph.style.name == "Normal":
            text_to_append = paragraph.text
            for index, link in enumerate(paragraph_links):
                text_to_append = text_to_append.replace(f'|{index}|', link)
            text_to_append = f"<p>\n{text_to_append}\n</p>\n"

            text_to_append = clean_awkward_characters(text_to_append)

            new_block.append(text_to_append)

        elif paragraph.style.name == "Heading 2":
            text_to_append = f'<h2>\n{paragraph.text}\n</h2>\n'

            new_block.append(text_to_append)

    for heading, text in zip(headings, text_blocks):
        file_name = Path("jinja_templates") / f"{heading.lower().replace(' ', '_')}.html"
        with open(file_name, 'w') as out_file:
            out_file.write(text)


def clean_awkward_characters(in_text: str) -> str:
    """
    Clean a string of odd characters or otherwise inelegant combinations that cause problems for jinja and/or
    html.

    Parameters
    ----------
    in_text: str
        String to be cleaned

    Returns
    -------
    str
        Cleaned string
    """
    switcheroo = {
        "°": "&deg;",
        "–": "-",
        "CO2": "CO<sub>2</sub>",
        "CH4": "CH<sub>4</sub>",
        "N2O": "N<sub>2</sub>O",
        "km2": "km<sup>2</sup>",
        "mm/yr": "mm.yr<sup>-1</sup>",
        "’": "'",
        '“': '"',
        '”': '"'
    }

    out_text = in_text
    for char in switcheroo:
        out_text = out_text.replace(char, switcheroo[char])

    return out_text


if __name__ == '__main__':
    split_document('word_documents/key_indicators_texts.docx')
