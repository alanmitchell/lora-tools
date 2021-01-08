#!/usr/bin/env python3
"""Analyzes erroneous Shore Power readings on AV1.
"""
import base64
import json
from datetime import datetime
import subprocess

def int16(ix: int) -> int:
    """Returns a 16-bit integer from the 2 bytes starting at index 'ix' in data byte array.
    """
    return (data[ix] << 8) | (data[ix + 1])

bad_ct = 0
fout = open('shore.tsv', 'w')
fout.write('ts\tv1\tv2\n')
for lin in open('shore.json'):
    rec = json.loads(lin.strip())
    data = base64.b64decode(rec['payload_raw'])
    v1 = int16(0) / 1000.
    v2 = int16(2) / 1000.
    ts = rec['metadata']['time']
    #if ts > '2021-01-01T16:33:00':
    if ts > '2021-01-08T23:25:00':
        bad_data = False
        if abs(v1-5.1) > 0.05:
            bad_data = True
        if abs(v2 - 11.92) > 0.1:
            bad_data = True
        if bad_data:
            print('***', end='')
            bad_ct += 1
        print(f"{ts} V1: {v1:.3f}, V2:{v2:.3f}")
        fout.write(f'{ts}\t{v1}\t{v2}\n')
fout.close()
print(f'Number of Bad Readings: {bad_ct}')