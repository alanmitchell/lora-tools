#!/usr/bin/env python3

"""Creates a color bar chart showing reading counts per hour for selected sensors.
"""

# %%
# Groups of sensors:  GroupName: (max_reading_count, list of device IDs)
DEVICE_GROUPS = {
    'Seward': (12, (
        'Phil ELT-2 3692',
        'Phil LT22222 436E',
        'Phil CO2 26D8',
    )),
    'Public Housing': (6, (
        '3148 E 19th, Anc',
        '3414 E 16th, Anc',
        '3424 E 18th, Anc',
        '122 N Bliss',
    )),
}

# Color Scale built from https://hihayk.github.io/
# key is number of readings in the hour.
color_scale = {
    0: '#FF3131',
    1: '#FF7F20',
    2: '#FFC610',
    3: '#FFFF00',
}

color_scale = {
    0: '#FF3131',
    1: '#FFD822',
    2: '#FFFF00',
}


from datetime import datetime, timedelta
import subprocess
import pandas as pd
from dateutil.parser import parse
from dateutil import tz
from rich import print
from rich.markdown import Markdown
import questionary
from label_map import dev_id_lbls, gtw_lbls

print()
refresh = questionary.confirm("Download new Data?").ask()
#refresh = False
if refresh:
    subprocess.run("./gateways_get.sh", shell=True)

device_group = questionary.select('Select Group of Sensors:', DEVICE_GROUPS.keys()).ask()
max_reading_count, devices = DEVICE_GROUPS[device_group]

days_to_show = int(questionary.select(
    "How many days to Show?", 
    choices=['1', '2', '3', '4'],
    default='4').ask())

tz_ak = tz.gettz('US/Alaska')
start_ts = (datetime.now(tz_ak) - timedelta(days=days_to_show)).replace(
    tzinfo=None, minute=0, second=0, microsecond=0)
end_ts = datetime.now(tz_ak).replace(
    tzinfo=None, minute=0, second=0, microsecond=0)

df = pd.read_csv('gateways.tsv', 
    sep='\t', 
    parse_dates=['ts', 'ts_hour'],
    index_col='ts',
    low_memory=False)
df = df.loc[str(start_ts):]
df['dev_id'] = df.dev_id.map(dev_id_lbls)
df.query('dev_id in @devices', inplace=True)

def gtw_map(gtw_eui):
    return gtw_lbls.get(gtw_eui, gtw_eui)

df['gateway'] = df.gateway.map(gtw_map)

gtws = df.gateway.unique()
gtw_choices = ['Any'] + list(gtws)
# filter gateway here, if requested
#gtw_incl = questionary.select("Gateways to Include:", choices=gtw_choices).ask()
print('\nNumber of Readings in the Hour:\n')
for gtw_incl in gtw_choices:
    if gtw_incl != 'Any':
        dfg = df.query('gateway == @gtw_incl').copy()
    else:
        dfg = df.copy()
    
    print(f'Gateway: {gtw_incl}')
    print()

    dfg = dfg[['ts_hour', 'dev_id', 'counter']].reset_index()
    dfg.drop_duplicates(inplace=True)
    dfg.drop(columns='ts', inplace=True)
    df2 = dfg.groupby(['ts_hour', 'dev_id']).count().reset_index()
    df_cts = df2.pivot(index='ts_hour', columns='dev_id', values='counter')

    # Make a new index that fills in any missing hours
    #new_ix = pd.date_range(df_cts.index[0], df_cts.index[-1], freq='1H')
    new_ix = pd.date_range(start_ts, end_ts, freq='1H')
    df_cts = df_cts.reindex(new_ix)

    # Fill NaNs with 0
    df_cts.fillna(0, inplace=True)

    # drop last hour because likely a partial hour
    df_cts = df_cts[:-1]

    for c in df_cts.columns:
        print(f'{c:20}', end='')
        for ts, val in df_cts[c].iteritems():
            if ts.hour == 0:
                print(' ', end='')
            if val > max(color_scale.keys()):
                prn_char = int(val) if val < 10 else '+'
                print(f"[#BBBBBB on #FFFFFF]{prn_char}[/]", end='')
            else:
                color = color_scale[val]
                print(f"[#000000 on {color}]{int(val)}[/]", end='')
        print()

    print(Markdown('---\n\n'))

print()
