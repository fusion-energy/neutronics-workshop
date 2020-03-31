import json

import numpy as np
from tqdm import tqdm

from openmc_model import objective

# Grid of data values for 2D example
tbr_values = []
for enrichment in tqdm(np.linspace(0, 100, 20)):
    for thickness in np.linspace(10, 200, 20):
        tbr_values.append((enrichment, thickness, -objective([enrichment])))

with open('enrichment_thickness_vs_tbr.json', mode="w", encoding="utf-8") as f:
    json.dump(tbr_values, f, indent=4)
