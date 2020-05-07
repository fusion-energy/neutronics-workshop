import json
import csv

import numpy as np
from tqdm import tqdm

from openmc_model import objective

# Grid of data values for 2D example
tbr_values = []
for enrichment in tqdm(np.linspace(0, 100, 10)):
    for thickness in np.linspace(10, 200, 10):
        tbr_values.append({'enrichment': enrichment,
                           'thickness': thickness,
                           'tbr': -objective([enrichment, thickness])
                          })

with open('2d_tbr_values.json', mode="w", encoding="utf-8") as f:
    json.dump(tbr_values, f, indent=4)