import copy

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA

from climind.config.config import DATA_DIR

# Load monthly global mean temperature dataset
def load_temperature_data():
    # Load dataset
    df = pd.read_csv(DATA_DIR / 'ManagedData' / 'Data'/ 'HadCRUT5' / 'edit.csv')
    df['Date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))
    df.set_index('Date', inplace=True)
    df = df[df['year'] > 1970]  # Select only years after 1970
    return df['anomaly']

# Fit ARIMA model
def fit_arima_model(series, order=(1, 1, 1)):
    model = ARIMA(series, order=order)
    fitted_model = model.fit()
    return fitted_model

# Generate a synthetic time series using ARIMA model with a specified trend
def generate_synthetic_series(fitted_model, length, slope, intercept):
    simulated_residuals = fitted_model.simulate(length)
    trend = intercept + slope * np.arange(length)
    return trend + simulated_residuals

# Load data
temperature_series = load_temperature_data()

# Compute trend
trend_model = sm.OLS(temperature_series, sm.add_constant(np.arange(len(temperature_series)))).fit()
temperature_trend = trend_model.fittedvalues

#detrended_series = temperature_series - temperature_trend  # Detrend the series

# Fit ARIMA model to detrended series
#arima_model = fit_arima_model(detrended_series)
#residuals = arima_model.resid

# Generate synthetic time series
#synthetic_series = generate_synthetic_series(arima_model, len(temperature_series), slope=0.02, intercept=temperature_series.iloc[0])

# Calculate 12-point running average
running_avg = temperature_series.rolling(window=12).mean()
long_running_avg = temperature_series.rolling(window=120).mean()

long_running_avg = np.roll(long_running_avg, -60)

max_till = copy.deepcopy(running_avg)
for i in range(11, len(running_avg)):
    max_till[i] = np.max(running_avg[11:i])

min_within_12 = copy.deepcopy(running_avg)
for i in range(11, len(running_avg)):
    min_within_12[i] = np.min(running_avg[i-11:i])

max_min = copy.deepcopy(running_avg)
for i in range(11, len(running_avg)):
    max_min[i] = np.max(min_within_12[11:i])


sl1 = (max_till >= temperature_trend) & (~np.isnan(max_till)) & (~np.isnan(temperature_trend))
sl2 = (~np.isnan(max_till)) & (~np.isnan(temperature_trend))

selected1 = 100*np.count_nonzero(sl1)/np.count_nonzero(sl2)


sl1 = (max_till >= long_running_avg) & (~np.isnan(max_till)) & (~np.isnan(long_running_avg))
sl2 = (~np.isnan(max_till)) & (~np.isnan(long_running_avg))

selected2 = 100*np.count_nonzero(sl1)/np.count_nonzero(sl2)


sl1 = (max_min >= long_running_avg) & (~np.isnan(max_min)) & (~np.isnan(long_running_avg))
sl2 = (~np.isnan(max_min)) & (~np.isnan(long_running_avg))

selected3 = 100*np.count_nonzero(sl1)/np.count_nonzero(sl2)

print(selected1)
print(selected2)
print(selected3)

# Plot the results
plt.figure(figsize=(10, 5))
plt.plot(temperature_series.index, temperature_series, label='Observed Temperatures', color='blue', alpha=0.7)
plt.plot(temperature_series.index, temperature_trend, label='Trend', color='red', linewidth=3)
plt.plot(temperature_series.index, running_avg, label='12-Month Running Average', color='green',linewidth=3)
plt.plot(temperature_series.index, long_running_avg, label='120-Month Running Average', color='pink',linewidth=3)
plt.plot(temperature_series.index, max_till, label='Max 12-month average', color='orange',linewidth=3)
plt.plot(temperature_series.index, max_min, label='nonsense',color='black', linewidth=3)
plt.xlabel('Time')
plt.ylabel('Temperature Anomaly (°C)')
plt.title('Global Monthly Mean Temperature Anomalies')
plt.legend()
plt.show()

