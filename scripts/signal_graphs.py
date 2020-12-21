# %%
import pandas as pd
import plotly.express as px

# %%
df = pd.read_csv('gateways.tsv', sep='\t', parse_dates=['ts', 'ts_day', 'ts_hour'])
df.head()
# %%
df.info()
# %%
dev = "boat-lt2-a8404137b182428e"
gtw = "eui-a840411eed744150"
dfq = df.query('dev_id == @dev and gateway == @gtw')
dft = dfq.set_index('ts')
dft = dft.resample('1H').mean()
px.scatter(dft, x=dft.index, y='snr')
# %%
df.dev_id.unique()

# %%
