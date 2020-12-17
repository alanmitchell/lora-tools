#!/usr/bin/env python3
"""Looks at Analog V1 and Analog V2 readings to analyze the anomalies that
were observed with radical drops in V1 voltage.
"""
import base64
import json
from datetime import datetime
import subprocess

def int16(ix: int) -> int:
    """Returns a 16-bit integer from the 2 bytes starting at index 'ix' in data byte array.
    """
    return (data[ix] << 8) | (data[ix + 1])

subprocess.run("./get_data.sh", shell=True)
ct = 0
for lin in open('lt22222.json'):
    rec = json.loads(lin.strip())
    data = base64.b64decode(rec['payload_raw'])
    v1 = int16(0)
    v2 = int16(2)
    c1 = int16(4)
    c2 = int16(6)
    # digitals are inverted logic.
    di1 = 0 if data[8] & 0x08 else 1
    di2 = 0 if data[8] & 0x10 else 1
    if rec['metadata']['time'] > '2020-12-08T05:40:05':
        ct += 1
        #print(v1, v2, c1, c2, di1, di2)
        if abs(v1 - 11847) > 50:
            print(f"V1: {rec['metadata']['time']} {v1}")
        if abs(v2 - 11886) > 50:
            print(f"  V2: {rec['metadata']['time']} {v2}")
        if abs(c1 - 602) > 10:
            print(f"    C1: {rec['metadata']['time']} {c1}")
        if abs(c2 - 602) > 10:
            print(f"      C2: {rec['metadata']['time']} {c2}")
        if di1 != 1:
            print(f"        DI1: {rec['metadata']['time']} {di1}")
        if di2 != 1:
            print(f"          DI2: {rec['metadata']['time']} {di2}")

print(f'\nNow UTC: {datetime.utcnow()}')
print(f'Total Records: {ct}')
