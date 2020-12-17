#!/usr/bin/env python3

# %%
import bmondata
import matplotlib.pyplot as plt
 

# %%
sensor_id = 'A8404137B182428E_batteryV'

srvr = bmondata.Server('https://sewardwatch.org')

df = srvr.sensor_readings(sensor_id, start_ts='Dec 8, 2020')
df.head()

# %%
dfp = df.resample('1H').count()
plt.scatter(x=dfp.index, y=dfp.A8404137B182428E_batteryV)

# %%
df.reset_index().diff()['index'].max()  #quantile(.999)

# %%
df.reset_index().diff()['index'].quantile(.99)
