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

import qrcode
from climind.config.config import DATA_DIR

def create_code(url, filename):
    project_dir = DATA_DIR / "ManagedData"
    figure_dir = project_dir / 'Figures'

    img = qrcode.make(url)
    img.save(figure_dir / filename)


if __name__ == "__main__":

    create_code('https://wmo.int/publication-series/state-of-global-climate-2023', 'qr_sotc.png')