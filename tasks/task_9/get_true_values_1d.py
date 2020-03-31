import json

import numpy as np
from tqdm import tqdm

from openmc_model import objective

# Grid of data values 1D example
tbr_values = []
for enrichment in tqdm(np.linspace(0, 100, 101)):
    tbr_values.append((enrichment, -objective([enrichment])))

with open('enrichment_vs_tbr.json', mode="w", encoding="utf-8") as f:
    json.dump(tbr_values, f, indent=4)