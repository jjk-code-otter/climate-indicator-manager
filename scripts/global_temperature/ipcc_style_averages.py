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

"""
Code to calculate the IPCC-style global mean temperature relative to an 1850-1900 baseline

Port from fortran to python from https://github.com/ClimateIndicator/GMST/blob/main/globaltemphadcrupub.f
Originally written by Blair Trewin. Ported by John Kennedy.
Note only routines needed to calculate global annual means were ported. The original code did more things.
"""

import xarray as xa
import numpy as np
import pandas as pd
from pathlib import Path
import os
from climind.config.config import DATA_DIR
from climind.stats.utils import (get_latitudes, get_n_years_from_n_months,
                                 monthly_to_annual_array, rolling_average)

import matplotlib.pyplot as plt


def obsingest(filename):
    """
    Ingest the gridded temperature data and return an array (nyears, 12, nlon, nlat). This is coded using the
    original fortran code ported directly.

    Only complete years are output

    Parameters
    ----------
    filename: Path

    Returns
    -------

    """
    df = xa.open_dataset(filename)

    # Each dataset has a different main variable.
    if 'tas_mean' in df.variables:
        data = df.tas_mean.data
    elif 'tas' in df.variables:
        data = df.tas.data
    elif 'anom' in df.variables:
        data = df.anom.data
        data = data[:, 0, :, :]
    elif 'temperature' in df.variables:
        data = df.temperature.data

    # Determine how many months there are and select only whole years starting from start of array
    n_months = data.shape[0]
    n_years = int(np.floor(n_months / 12.))
    data = data[0:n_years * 12, :, :]

    # Determine size of array
    nlat = data.shape[1]
    nlon = data.shape[2]

    # Reshape to standard array format
    output_array = np.zeros((n_years, 12, nlon, nlat))

    # Copy data across
    count = 0
    for yr in range(n_years):
        for m in range(12):
            for x in range(nlon):
                for y in range(nlat):
                    output_array[yr, m, x, y] = data[count, y, x]
            count += 1

    # replace with standard null value
    output_array[np.isnan(output_array)] = -999.0

    return output_array


def spatmeancalc(obs):
    """
    calculation of spatial means from grids using the original method directly ported from Fortran

    Parameters
    ----------
    obs
    length

    Returns
    -------

    """
    nlat = obs.shape[3]
    nlon = obs.shape[2]
    length = obs.shape[0]

    res = 180. / nlat

    spatmean = np.zeros((length, 12, 3, 3))
    gridcount = np.zeros((length, 12, 3, 3))

    pi = 3.14159

    for i in range(length):
        for j in range(12):
            # in these arrays, m is hemisphere (1 southern, 2 northern) and n
            # is a land/ocean flag (1 all, 2 land, 3 ocean)
            spatsum = np.zeros((2, 3))
            count = np.zeros((2, 3))
            wsum = np.zeros((2, 3))
            lat = np.zeros((2))

            for l in range(nlat):
                lat[0] = ((res * (l + 1)) - (90.0 + res)) * pi / 180.0
                lat[1] = ((res * (l + 1)) - 90.0) * pi / 180.0
                # gridboxes weighted by area. Note this is equivalent to the standard weight of
                # cosine of the latitude of the grid cell midpoint but multiplied by a constant
                weight = abs((np.sin(lat[0]) - np.sin(lat[1])))

                for k in range(nlon):
                    if obs[i, j, k, l] != -999.0:
                        if lat[0] < 0.0:
                            # spatsum is sum of weighted spatial means, wsum is sum of weights
                            spatsum[0, 0] += weight * obs[i, j, k, l]
                            count[0, 0] += 1
                            wsum[0, 0] += weight
                        else:
                            spatsum[1, 0] += weight * obs[i, j, k, l]
                            count[1, 0] += 1
                            wsum[1, 0] += weight

            # calculation of spatial means from the weighted gridbox values
            for n in range(3):
                for m in range(2):
                    if wsum[m, n] > 0:
                        spatmean[i, j, m, n] = spatsum[m, n] / wsum[m, n]
                    else:
                        spatmean[i, j, m, n] = -999.0
                    gridcount[i, j, m, n] = count[m, n]

                # global mean calculated as mean of NH and SH values
                gridcount[i, j, 2, n] = gridcount[i, j, 0, n] + gridcount[i, j, 1, n]
                if (wsum[0, n] > 0) and (wsum[1, n] > 0):
                    spatmean[i, j, 2, n] = (spatmean[i, j, 0, n] + spatmean[i, j, 1, n]) / 2.0
                else:
                    spatmean[i, j, 2, n] = -999.0

    return spatmean


def annspatcalc(spatmean):
    length = spatmean.shape[0]
    annspatmean = np.zeros((length, 3, 3))

    for i in range(length):
        for k in range(3):
            for n in range(3):
                sum = 0.0
                count = 0
                for j in range(12):
                    if spatmean[i, j, k, n] != -999.0:
                        sum += spatmean[i, j, k, n]
                        count += 1
                if count == 12:
                    annspatmean[i, k, n] = sum / 12.0
                else:
                    annspatmean[i, k, n] = -999.0

    return annspatmean


def simple_obs_ingest(filename):
    """
    Read in the gridded data from netcdf and output a standard ndarray. Note only reads in whole years. Assumes
    that the first month in a file is January 1850 and that there are no missing months.

    Parameters
    ----------
    filename: Path
        Path of the netcdf file

    Returns
    -------

    """
    df = xa.open_dataset(filename)

    # Each of the groups has a different name for the temperature variable, and slightly different ways of
    # organising the data in the NetCDF file, so we need to coerce these into a common array format
    if 'tas_mean' in df.variables:
        data = df.tas_mean.data
    elif 'tas' in df.variables:
        data = df.tas.data
    elif 'anom' in df.variables:
        data = df.anom.data
        data = data[:, 0, :, :]
    elif 'temperature' in df.variables:
        data = df.temperature.data

    # Determine how many months there are and select only whole years starting from start of array
    n_months = data.shape[0]
    n_years = get_n_years_from_n_months(n_months)
    n_months = n_years * 12

    data = data[0:n_months, :, :]

    return data


def calculate_spatial_mean(observation_array):
    """
    Calculate the spatial mean of the gridded data. Assuming that the data are on a regular lat-lon grid, which runs
    from -90 to 90 degrees and that the areas of the grid correspond to the grid-cell centres. Areas are calculated
    using the standard cos(latitude) weighting. Three averages are output for each month: northern hemisphere,
    southern hemisphere and the global average (which is just the simple mean of the two).

    Parameters
    ----------
    observation_array: ndarray(time, nlat, nlon)
        Numpy 3-d array containing the observations.

    Returns
    -------
    ndarray(time, 3)
        Return array which contains the northern hemisphere, southern hemisphere and global averages for each time step
    """
    n_latitude = observation_array.shape[1]
    n_longitude = observation_array.shape[2]
    length = observation_array.shape[0]
    resolution = 180. / n_latitude

    latitudes = np.zeros((n_latitude, n_longitude))
    for x in range(n_longitude):
        latitudes[:, x] = get_latitudes(resolution)
    weights = np.cos(np.deg2rad(latitudes))

    spatial_means = np.zeros((length, 3))

    for time_index in range(length):
        selected_obs = observation_array[time_index, :, :]

        nh_mask = (latitudes > 0) & (~np.isnan(selected_obs))
        sh_mask = (latitudes < 0) & (~np.isnan(selected_obs))

        # index 0 is Northern Hemisphere average masked to observed locations
        # index 1 is Southern Hemisphere average masked to observed locations
        # index 2 is Global average calculated as simple arithmetic mean of the two hemispheric averages
        spatial_means[time_index, 0] = np.average(selected_obs[nh_mask], weights=weights[nh_mask])
        spatial_means[time_index, 1] = np.average(selected_obs[sh_mask], weights=weights[sh_mask])
        spatial_means[time_index, 2] = (spatial_means[time_index, 0] + spatial_means[time_index, 1]) / 2.0

    return spatial_means


def calculate_annual_mean(monthly_means):
    """
    Given the monthly spatial means, calculate the annual averages

    Parameters
    ----------
    monthly_means: ndarray(time, 3)
        Monthly means for the northern hemisphere, southern hemisphere and globe

    Returns
    -------
    ndarray(nyears)
    """
    return monthly_to_annual_array(monthly_means)


startyr = 1850
endyr = 2023
length = endyr - startyr + 1

climatology_start = 1850
climatology_end = 1900

# Set to True to use the functions based on a word-for-word translation of the original fortran
# Setting it to False uses the more pythonic versions
original_processing = False

data_dir = DATA_DIR / "ManagedData" / "Data"

berkeley_file = data_dir / "Berkeley Earth" / "Land_and_Ocean_LatLong1.nc"
noaa_v51_file = data_dir / "NOAA Interim" / "NOAAGlobalTemp_v5.1.0_gridded_s185001_e202312_c20240108T150239.nc"
noaa_v6_file = data_dir / "NOAA v6" / "NOAAGlobalTemp_v6.0.0_gridded_s185001_e202402_c20240308T152813.nc"
hadcrut5_file = data_dir / "HadCRUT5" / "HadCRUT.5.0.2.0.analysis.anomalies.ensemble_mean.nc"
kadow_file = data_dir / "Kadow" / "HadCRUT5.anomalies.Kadow_et_al_2020_20crAI-infilled.ensemble_mean_185001-202312.nc"

obs_filenames = [berkeley_file, noaa_v6_file, hadcrut5_file, kadow_file]

# Set up the basic arrays
all_data = np.zeros((length, len(obs_filenames)))
yearvals = np.arange(startyr, endyr + 1, 1)
climatology_period = (yearvals >= climatology_start) & (yearvals <= climatology_end)

for i, obs_filename in enumerate(obs_filenames):

    if original_processing:
        observed_grid = obsingest(obs_filename)
        spatial_mean = spatmeancalc(observed_grid)
        annual_spatial_mean = annspatcalc(spatial_mean)
    else:
        observed_grid = simple_obs_ingest(obs_filename)
        spatial_mean = calculate_spatial_mean(observed_grid)
        annual_spatial_mean = calculate_annual_mean(spatial_mean)


    all_data[:, i] = annual_spatial_mean[:, 2] - np.mean(annual_spatial_mean[climatology_period, 2])

#Average together all the datasets and take 10 and 20 year rolling means
summary = np.mean(all_data, axis=1)

decadal = rolling_average(summary, 10)
tecadal = rolling_average(summary, 20)

# Read in the series as calculated using the original code
orig = pd.read_csv('Global indicators paper - decadal means.csv', names=['year', 'miss', 'dec', 'ann'])
update = pd.read_csv('Global indicators paper - decadal means - April 2024.csv', names=['year', 'miss', 'dec', 'ann'])

# Plot the individual series and the summary
for i in range(len(obs_filenames)):
    plt.plot(yearvals, all_data[:, i])

plt.plot(yearvals, summary, color='black')
plt.plot(yearvals, decadal, color='red')
plt.plot(yearvals, tecadal, color='green')

plt.show()
plt.close()

# Plot the annual values: freshly calculated and from the IGCC paper
plt.plot(yearvals, summary, label='This analysis')
plt.plot(orig.year, orig.ann, label='IPCC')
plt.plot(update.year, update.ann, label='IGCC update')
plt.legend()
plt.show()
plt.close()

# Plot the decadal values: freshly calculated and from the IGCC paper
plt.plot(yearvals, decadal, label='This analysis')
plt.plot(orig.year, orig.dec, label='IPCC')
plt.plot(update.year, update.dec, label='IGCC update')
plt.legend()
plt.show()
plt.close()

decadal[np.isnan(decadal)] = -9.9999
orig.dec[np.isnan(orig.dec)] = -9.9999
orig.ann[np.isnan(orig.ann)] = -9.9999
update.dec[np.isnan(update.dec)] = -9.9999
update.ann[np.isnan(update.ann)] = -9.9999

# Print out the freshly calculated series and the "original" series from the IGCC 2023 paper
print("Original")
for i in range(2018 - startyr):
    print(
        f"{yearvals[i]} {decadal[i]:.2f}, {orig.dec[i]:.2f}, {decadal[i] - orig.dec[i]:.2f} === "
        f"{summary[i]:.2f}, {orig.ann[i]:.2f} {summary[i] - orig.ann[i]:.2f} ")
i += 1
print(f"{yearvals[i]} {decadal[i]:.2f}, {-9:.2f}, {-9:.2f} === {summary[i]:.2f}, {-9:.2f} {-9:.2f} ")

# Print out the freshly calculated series and the "original" series from the IGCC 2023 paper
print("Update")
for i in range(2018 - startyr):
    print(
        f"{yearvals[i]} {decadal[i]:.2f}, {update.dec[i]:.2f}, {decadal[i] - update.dec[i]:.4f} === "
        f"{summary[i]:.2f}, {update.ann[i]:.2f} {summary[i] - update.ann[i]:.4f} ")
i += 1
print(f"{yearvals[i]} {decadal[i]:.2f}, {-9:.2f}, {-9:.2f} === {summary[i]:.2f}, {-9:.2f} {-9:.2f} ")
