#!/usr/bin/env python3

"""Creates a color bar chart showing reading counts per hour for selected sensors.
"""

# %%
DAYS_TO_SHOW = 4
DEVICES = (
    'Phil ELT-2 3692',
    #'Phil LT22222 428E',
    'Phil LT22222 436E',
    'Phil CO2 26D8',
)

import json
from datetime import datetime, timedelta
import pytz
import pandas as pd
import plotly.graph_objects as go
from dateutil.parser import parse
from dateutil import tz
from rich import print
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
df_cts.tail(30)

# %%
# Color Scale built from https://hihayk.github.io/
color_scale = {
    12: '#41930E',
    11: '#6FB50B',
    10: '#AED906',
    9: '#FFFF00',
    8: '#FFC614',
    7: '#FF8429',
    6: '#FF403D',
}

print('\nNumber of Missed Readings in the Hour:\n')
for c in df_cts.columns:
    print(f'{c:20}', end='')
    vals = df_cts[c].values
    for val in vals:
        val_key = min(12, max(6, val))
        color = color_scale[val_key]
        val_print = ' ' if val_key==12 else int(12 - val) if val >= 3 else '+'
        #val_print = ' '
        print(f"[#000000 on {color}]{val_print}[/]", end='')
    print()
print()
# %%
