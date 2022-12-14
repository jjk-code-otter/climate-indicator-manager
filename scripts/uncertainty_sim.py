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
import numpy as np
import random

trials = []

# calculate estimated uncertainty for average of 100 values
var = (2.0 * 0.5) ** 2 / 12.
estimated_uncertainty = np.sqrt(var / 100.)

# do ten thousand trials
for j in range(0, 100000):

    # generate random numbers and then round them
    samples = []
    intsamples = []
    for i in range(0, 100):
        rn = random.gauss(0, 1)
        samples.append(rn)
        intsamples.append(float(round(rn)))

    full_precision_average = np.mean(samples)
    rounded_average = np.mean(intsamples)

    trials.append(full_precision_average - rounded_average)

print(np.std(trials), estimated_uncertainty)
