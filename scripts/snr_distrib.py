#!/usr/bin/env python3
# %%
import json
import pandas as pd

snrs = []
for lin in open('lora.txt'):
    rec = json.loads(lin.strip())
    for gtw in rec['metadata']['gateways']:
        snrs.append(gtw['snr'])

df = pd.DataFrame({'snr': snrs})
df.describe()

# %%
df.hist(bins=30)
# %%
