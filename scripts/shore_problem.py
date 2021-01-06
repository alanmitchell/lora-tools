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
for lin in open('shore.json'):
    rec = json.loads(lin.strip())
    data = base64.b64decode(rec['payload_raw'])
    v1 = int16(0) / 1000.
    v2 = int16(2) / 1000.
    if rec['metadata']['time'] > '2021-01-05T00:00:00':
        bad_data = False
        if abs(v1) > 0.02:
            bad_data = True
        if abs(v2 - 11.92) > 0.1:
            bad_data = True
        if bad_data:
            print('***', end='')
            bad_ct += 1
        print(f"{rec['metadata']['time']} V1: {v1:.3f}, V2:{v2:.3f}")
print(f'Number of Bad Readings: {bad_ct}')