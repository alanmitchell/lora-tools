"""Creates a heat map showing reading counts per hour for selected sensors.
Depends on a 
"""

# %%
DAYS_TO_SHOW = 1
DEVICES = (
    'Phil ELT-2 3692',
    'Phil LT22222 428E',
    'Phil CO2 26D8',
)

import json
from datetime import datetime, timedelta
import pytz
import pandas as pd
import plotly.graph_objects as go
from dateutil.parser import parse
from dateutil import tz
from label_map import dev_lbls

start_ts = datetime.now(pytz.utc) - timedelta(days=DAYS_TO_SHOW)
recs = []
tz_ak = tz.gettz('US/Alaska')
for lin in open('lora.json'):
    rec = json.loads(lin)
    ts = parse(rec['metadata']['time'])
    device = dev_lbls.get(rec['hardware_serial'], rec['hardware_serial'])
    if ts > start_ts and device in DEVICES:
        ts_ak = ts.astimezone(tz_ak)
        recs.append(dict(ts = ts_ak, device=device))

df = pd.DataFrame(recs)
df.set_index('ts', inplace=True)

df['readings'] = 1
df_cts = df.pivot(columns='device', values='readings')

df_cts = df_cts.resample('1H').sum()
df_cts.where(df_cts <= 12, 12, inplace=True)
df_cts = df_cts[1:-1]                  # take out first and last hour
# %%
fig = go.Figure(data=go.Heatmap(
        z=df_cts.values.transpose(),
        x=df_cts.index,
        y=df_cts.columns,
        colorscale='RdYlGn')
        )

fig.update_layout(
    title='Readings per Hour',
    xaxis_nticks=48,
    width=1000,
    height=400,
)

fig.show()
