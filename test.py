#!/usr/bin/env python3
import json
from pprint import pprint
from base64 import b64decode
from decoder.decoder import decode


for lin in open('../lora-debug.txt'):
    try:
        d = json.loads(lin.strip())
        pprint(decode(d))
    except:
        print('Error')
