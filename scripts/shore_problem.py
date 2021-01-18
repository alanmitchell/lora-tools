#!/usr/bin/env python3
"""Analyzes erroneous Shore Power readings on AV1.
"""
import base64
import json
from datetime import datetime
import subprocess
import pandas as pd
import questionary

DEVICE = 'boat-lt2-a8404137b182428e'
START_DATE = '2021-01-13 10:24'

def int16(ix: int) -> int:
    """Returns a 16-bit integer from the 2 bytes starting at index 'ix' in data byte array.
    """
    return (data[ix] << 8) | (data[ix + 1])

print()
refresh = questionary.confirm("Download new Data?").ask()
#refresh = False
if refresh:
    subprocess.run("./values_get.sh", shell=True)

df = pd.read_csv('values.tsv', sep='\t')
dfs = df.query('dev_id == @DEVICE and ts > @START_DATE').copy()
bad_ct = 0

fout = open('shore.tsv', 'w')
fout.write('ts\tv1\tv2\n')

for ix, row in dfs.iterrows():
    data = base64.b64decode(row['payload'])
    ts = row['ts']
    v1 = int16(0) / 1000.
    v2 = int16(2) / 1000.
    print(f"{ts} V1: {v1:.3f}, V2: {v2:.3f}")
    fout.write(f'{ts}\t{v1}\t{v2}\n')
