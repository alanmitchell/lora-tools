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

ct = 0
for lin in open('shore.json'):
    rec = json.loads(lin.strip())
    data = base64.b64decode(rec['payload_raw'])
    v1 = int16(0) / 1000.
    if rec['metadata']['time'] > '2020-12-29T00:00:00':
        print(f"V1: {rec['metadata']['time']} {v1:.4f}")