#  Climate indicator manager - a package for managing and building climate indicator dashboards.
#  Copyright (c) 2024 John Kennedy
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

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Frame, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import Color
from reportlab.pdfbase.pdfmetrics import stringWidth

from PIL import Image
from svglib.svglib import svg2rlg

from climind.config.config import DATA_DIR

fwidth = 595 - 2 * 45


def indented_para_with_left_heading(c, x, ystart, title, para_text, color):

    if type(title) is list:
        total_block_height = plot_text_block(
            c, x, ystart, 130, title,
            255 * color[0], 255 * color[1], 255 * color[2]
        )
        head_width = 130
    else:
        c.setFont('arial_bold', 40, leading=None)
        c.setFillColorRGB(color[0], color[1], color[2])
        c.setStrokeColorRGB(color[0], color[1], color[2])
        head_width = stringWidth(title, 'arial_bold', 40)
        c.drawString(x, ystart - 40, title)
        total_block_height = 40

    s = Paragraph(para_text, style=styleN)

    fwidth = 595 - 2 * 45

    aw, ah = s.wrap(fwidth - head_width - 10, total_block_height)
    g = s.split(fwidth - head_width - 10, total_block_height)

    gw, gh = g[0].wrap(fwidth - head_width - 10, total_block_height)
    f = Frame(
        x + head_width + 10, ystart - total_block_height - 5, gw, gh,
        showBoundary=bounds_on,
        leftPadding=0, bottomPadding=0,
        rightPadding=0, topPadding=0
    )
    f.addFromList([g[0]], c)

    gw, gh = g[1].wrap(fwidth, total_block_height)
    f = Frame(x, ystart - total_block_height - gh - 5, gw, gh,
              showBoundary=bounds_on,
              leftPadding=0, bottomPadding=0,
              rightPadding=0, topPadding=0
              )
    f.addFromList([g[1]], c)

    return ystart - total_block_height - gh - 5


def indented_para_with_right_heading(c, x, ystart, title, para_text, color):
    fwidth = 595 - 2 * 45

    if type(title) is list:
        head_width = 130
        total_block_height = plot_text_block(
            c, x + fwidth - head_width, ystart, 130, title,
            255 * color[0], 255 * color[1], 255 * color[2]
        )

    else:
        c.setFont('arial_bold', 40, leading=None)
        c.setFillColorRGB(color[0], color[1], color[2])
        c.setStrokeColorRGB(color[0], color[1], color[2])
        head_width = stringWidth(title, 'arial_bold', 40)
        c.drawString(x + fwidth - head_width, ystart - 40, title)
        total_block_height = 40

    s = Paragraph(para_text, style=styleN)

    aw, ah = s.wrap(fwidth - head_width, total_block_height)
    g = s.split(fwidth - head_width, total_block_height)

    gw, gh = g[0].wrap(fwidth - head_width, total_block_height)
    f = Frame(x, ystart - total_block_height - 5, gw, gh, showBoundary=bounds_on, leftPadding=0, bottomPadding=0, rightPadding=0,
              topPadding=0)
    f.addFromList([g[0]], c)

    gw, gh = g[1].wrap(fwidth, total_block_height)
    f = Frame(x, ystart - total_block_height - gh - 5, gw, gh, showBoundary=bounds_on, leftPadding=0, bottomPadding=0, rightPadding=0,
              topPadding=0)
    f.addFromList([g[1]], c)

    return ystart - total_block_height - gh - 5


def plot_fixed_width_text(c, x, y, text, box_width, font):
    """
    Given a canvas, x,y coordinates, and some text write the text in a font size that makes the text width equal to
    the box width

    Parameters
    ----------
    c: canvas
        The canvas on which the text will be written
    x: float
        x location of the text
    y: float
        y location of the text
    text: str
        The string you want to write
    box_width: float
        The width of the box you want to fill
    font: str
        Name of the font to be used

    Returns
    -------
    float
        The height of the fitted text
    """

    # Get the text width at 20pt and then scale that to fill the full box width
    text_width = stringWidth(text, 'arial_bold', 20)
    scaled_font_size = 20 * box_width / text_width
    c.setFont('arial_bold', scaled_font_size, leading=None)
    c.drawString(x, y - scaled_font_size, text)

    return scaled_font_size


def plot_text_block(c, x, y, box_width, phrases, r, g, b):
    """
    For a given canvas, x, y, coordinates and box width write a list of phrases such that the width of each line in
    the list is equal to the box_width. Use r, g, and b (0-255) to specify the colour of the text.


    Parameters
    ----------
    c: canvas
        The canvas on which the text will be written
    x: float
        x location of the text
    y: float
        y location of the text
    box_width: float
        The width of the box you want to fill
    phrases: List[str]
        List of strings to be written
    r: float
        red channel 0-255
    g: float
        green channel 0-255
    b: float
        blue channel 0-255

    Returns
    -------
    float
        Total height of all the text blocks
    """
    c.setFillColorRGB(r / 255, g / 255, b / 255)

    total_block_height = 0
    for phrase in phrases:
        scaled_font_size = plot_fixed_width_text(c, x, y, phrase, box_width, 'arial_bold')
        y = y - scaled_font_size
        total_block_height += scaled_font_size

    return total_block_height


def annual_mean(c, x, y, year, value, uncertainty):
    box_width = 145
    phrases = [
        f"{year}",
        "Observed warming",
        f"{value:.2f}±{uncertainty:.2f}°C",
        "above the 1850-1900 average",
        "Warmest year on record"
    ]
    total_block_height = plot_text_block(c, x, y, box_width, phrases, 245, 96, 66)
    return total_block_height

def land_annual_mean(c, x, y, year, value, uncertainty):
    box_width = 145
    phrases = [
        f"{year}",
        "Land temperature",
        f"{value:.2f}±{uncertainty:.2f}°C",
        "above the 1850-1900 average",
        "Warmest year on record"
    ]
    total_block_height = plot_text_block(c, x, y, box_width, phrases, 161, 74, 27)
    return total_block_height

def ocean_annual_mean(c, x, y, year, value, uncertainty):
    box_width = 145
    phrases = [
        f"Ocean",
        "temperature",
        f"{value:.2f}±{uncertainty:.2f}°C",
        "above the 1850-1900 average",
        "Warmest year on record"
    ]
    total_block_height = plot_text_block(c, x, y, box_width, phrases, 85, 207, 200)
    return total_block_height


def long_term_mean(c, x, y, year1, year2, value, uncertainty):
    box_width = 145
    phrases = [
        f"{year1}-{year2}",
        "long-term warming",
        f"{value:.2f}±{uncertainty:.2f}°C",
        "Warmest decade on record"
    ]
    total_block_height = plot_text_block(c, x, y, box_width, phrases, 105, 194, 245)
    return total_block_height


def human_induced(c, x, y, year, value, uncertainty):
    box_width = 145
    phrases = [
        "Human-induced warming",
        # "warming",
        f"{value:.2f}±{uncertainty:.2f}°C",
        # "above the 1850-1900 average",
        "Highest on record"
    ]
    total_block_height = plot_text_block(c, x, y, box_width, phrases, 245, 194, 105)
    return total_block_height


doc_dir = DATA_DIR / 'ManagedData' / 'Documents'
figure_dir = DATA_DIR / 'ManagedData' / 'Figures'
doc_dir.mkdir(exist_ok=True)

pdfmetrics.registerFont(TTFont('arial', 'arial.ttf'))
pdfmetrics.registerFont(TTFont('arial_bold', 'ariblk.ttf'))

bounds_on = 0

c = canvas.Canvas(str(doc_dir / "hello.pdf"), pagesize=A4)

# Title and underline
c.setFont('arial_bold', 21, leading=None)
c.setFillColorRGB(95 / 255, 95 / 255, 95 / 255)
c.setStrokeColorRGB(95 / 255, 95 / 255, 95 / 255)
c.drawString(45, 800, "Key Climate Indicators: Global Temperature")
c.line(45, 797, 550, 797)

# Add plot of global mean temperatures
drawing = svg2rlg(figure_dir / 'observed_and_anthro.svg')
picture_scale = 0.29
drawing.width, drawing.height = drawing.minWidth() * picture_scale, drawing.height * picture_scale
drawing.scale(picture_scale, picture_scale)
drawing.drawOn(c, 200, 560)

# Plot number blocks
ystart = 800
tbh1 = annual_mean(c, 45, ystart, 2022, 1.15, 0.13)
tbh2 = human_induced(c, 45, ystart - tbh1, 2022, 1.26, 0.3)
tbh3 = long_term_mean(c, 45, ystart - tbh1 - tbh2, 2013, 2022, 1.15, 0.12)

# Set up paragraphs
styles = getSampleStyleSheet()
styleN = styles['Normal']
styleN.textColor = Color(245 / 255, 96 / 255, 66 / 255, 1)
styleN.backColor = Color(255 / 255, 255 / 255, 255 / 255, 0)
styleH = styles['Heading1']

ystart = ystart - tbh1 - tbh2 - tbh3

ystart = indented_para_with_left_heading(
    c, 45, ystart, "Basics",
    f"Global mean temperature measures the change in temperature near the surface of the Earth averaged "
    f"across its surface. Increased concentrations of greenhouse gases in the atmosphere are the primary driver of "
    f"the long-term increase in global mean temperature. Temperatures are measured by weather stations over land "
    f"and by ships and buoys at sea. Temperatures are typically shown as difference from a long-term average. "
    f"Several groups produce their own estimates of global mean temperature. Differences "
    f"between the groups' estimates are small in recent years and indicate how well we know global temperature. "
    f"Warming of the Earth is not the same everywhere. The land has warmed more rapidly than the ocean and the "
    f"rate of warming has been highest in the Arctic, which has warmed around two to four times faster than the "
    f"global mean depending on the time period chosen.",
    color=(245 / 255, 96 / 255, 66 / 255)
)

# Add plot of land and ocean temperatures
drawing = svg2rlg(figure_dir / 'land_ocean.svg')
picture_scale = 0.29
drawing.width, drawing.height = drawing.minWidth() * picture_scale, drawing.height * picture_scale
drawing.scale(picture_scale, picture_scale)
drawing.drawOn(c, 45, ystart-drawing.height-10)

tbh1 = land_annual_mean(c, fwidth-2*45, ystart, 2022, 2.11, 0.13)
tbh2 = ocean_annual_mean(c, fwidth-2*45, ystart-tbh1, 2022, 1.01, 0.13)

ystart = ystart - drawing.height -10

styleN.textColor = Color(105 / 255, 194 / 255, 245 / 255, 1)
ystart = indented_para_with_left_heading(
    c, 45, ystart, ["What did","IPCC say?"],
    f"Working Group 1 of the IPCC Sixth Assessment report made the following statements regarding "
    f"global temperatures in the Summary for Policy Makers.<br/><b>A.1.2</b> Each of the last four decades has been successively warmer than any decade that preceded "
    f"it since 1850. Global surface temperature in the first two decades of the 21st century (2001-2020) was 0.99 "
    f"[0.84 to 1.10] °C higher than 1850-1900. Global surface temperature was 1.09 [0.95 to 1.20] °C higher in 2011-2020 "
    f"than 1850-1900, with larger increases over land (1.59 [1.34 to 1.83] °C) than over the ocean "
    f"(0.88 [0.68 to 1.01] °C). The estimated increase in global surface temperature "
    f"since AR5 is principally due to further warming since 2003-2012 (+0.19 [0.16 to 0.22] °C). Additionally, "
    f"methodological advances and new datasets contributed approximately 0.1°C to the updated estimate of warming "
    f"in AR6.<br/><b>A.1.3</b> The likely range of total human-caused global surface "
    f"temperature increase from 1850-1900 to 2010-2019 is 0.8°C to 1.3°C, with a best estimate of 1.07°C. It is "
    f"likely that well-mixed GHGs contributed a warming of 1.0°C to 2.0°C, other human drivers (principally aerosols) "
    f"contributed a cooling of 0.0°C to 0.8°C, "
    f"natural drivers changed global surface temperature by -0.1°C to +0.1°C, and internal variability changed it by "
    f"-0.2°C to +0.2°C. It is very likely that well-mixed GHGs were the main driver of tropospheric warming since 1979 "
    f"and extremely likely that human-caused "
    f"stratospheric ozone depletion was the main driver of cooling of the lower stratosphere between 1979 and the "
    f"mid-1990s.",
    color=(105 / 255, 194 / 255, 245 / 255)
)


c.showPage()


# Title and underline
c.setFont('arial_bold', 21, leading=None)
c.setFillColorRGB(95 / 255, 95 / 255, 95 / 255)
c.setStrokeColorRGB(95 / 255, 95 / 255, 95 / 255)
c.drawString(45, 800, "Key Climate Indicators: Global Temperature")
c.line(45, 797, 550, 797)

ystart = 790

styleN.textColor = Color(245 / 255, 96 / 255, 66 / 255, 1)
ystart = indented_para_with_left_heading(
    c, 45, ystart, ["LONG-TERM","TEMPERATURE","CHANGE"],
    f"Although global temperature records from thermometers only extend back around 170 years, "
    f"longer temperature series can be compiled using proxies. Proxies are things that are sensitive "
    f"to changes in temperature and in which temperature variations leave permanent changes. For example, "
    f"tree rings are wider in years with warmer summers and narrower in colder years. Other proxies include "
    f"things like isotope ratios in ice cores, stalactites and corals, among many others. "
    f"Temperatures inferred from proxies aren't as accurate as those from thermometers and they can be "
    f"sensitive to things other than temperature. Further back in time, it becomes difficult to assign a "
    f"precise date to a proxy, and this tends to blur out when exactly changes happened. As with instrumental "
    f"temperatuers, different groups have approached the problem of estimating a global temperature from "
    f"proxies in very different ways. While these differ, broad scale changes over the past 2000 years can "
    f"be reconstructed with some degree of verisimilitude.",
    color=(245 / 255, 96 / 255, 66 / 255)
)

# Add plot of global mean temperatures
drawing = svg2rlg(figure_dir / 'pages2k.svg')
picture_scale = fwidth / drawing.minWidth()
drawing.width, drawing.height = drawing.minWidth() * picture_scale, drawing.height * picture_scale
drawing.scale(picture_scale, picture_scale)
drawing.drawOn(c, 45, ystart-drawing.height-10)

ystart = ystart-drawing.height-10

styleN.textColor = Color(154/255, 131/255, 230/255, 1)
ystart = indented_para_with_right_heading(
    c, 45, ystart, ["PARIS","AGREEMENT"],
    f"The <b>Paris Agreement</b> aims to hold the increase in the global average temperature "
    f"to well below 2°C above pre-industrial levels and pursue efforts to "
    f"limit the temperature increase to 1.5°C above pre-industrial levels, "
    f"recognizing that this would significantly reduce the risks and impacts "
    f"of climate change. The Paris Agreement is generally understood to refer "
    f"to human-induced or long-term changes in temperature, so a single year that exceeds 1.5°C "
    f"would not signal a breach of the threshold. A 10-year average, on the other hand, may well "
    f"indicate that the threshold had been crossed.",
    color=(154/255, 131/255, 230/255)
)


ystart = ystart - 10

styleN.textColor = Color(55 / 255, 55 / 255, 55 / 255, 1)
story = []
story.append(Paragraph("Data sources", styleH))
story.append(Paragraph(
    "<link href='https://www.metoffice.gov.uk/hadobs/hadcrut5/data/HadCRUT.5.0.2.0/analysis/diagnostics/HadCRUT.5.0.2.0.analysis.summary_series.global.monthly.csv'>HadCRUT5</link>",
    style=styleN))
story.append(Paragraph(
    "<link href='https://www.ncei.noaa.gov/data/noaa-global-surface-temperature/v5.1/access/timeseries/aravg.mon.land_ocean.90S.90N.v5.1.0.202312.asc'>NOAAGlobalTemp</link>",
    style=styleN))
story.append(Paragraph("<link href='https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv'>GISTEMP</link>",
                       style=styleN))
story.append(Paragraph(
    "<link href='https://berkeley-earth-temperature.s3.us-west-1.amazonaws.com/Global/Land_and_Ocean_complete.txt'>Berkeley Earth</link>",
    style=styleN))
story.append(Paragraph(
    "<link href='https://climate.copernicus.eu/sites/default/files/ftp-data/temperature/2023/12/ERA5_1991-2020/ts_1month_anomaly_Global_ERA5_2t_202312_1991-2020_v01.1.csv'>ERA5</link>",
    style=styleN))
story.append(Paragraph("<link href=''>JRA55</link>", style=styleN))

f = Frame(45, ystart - 110, fwidth / 2, 110, showBoundary=bounds_on, leftPadding=0, bottomPadding=0, rightPadding=0,
          topPadding=0)
f.addFromList(story, c)

story = []
story.append(Paragraph("References", style=styleH))
story.append(Paragraph(f"Someone et al. (2024)", style=styleN))
story.append(Paragraph(f"AN Other et al. (2024)", style=styleN))

f = Frame(45 + fwidth / 2, ystart - 110, fwidth / 2, 110, showBoundary=bounds_on, leftPadding=0, bottomPadding=0,
          rightPadding=0,
          topPadding=0)
f.addFromList(story, c)


c.showPage()

c.save()
