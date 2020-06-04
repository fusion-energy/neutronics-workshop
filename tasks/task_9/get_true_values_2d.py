import json
import csv

import numpy as np
from tqdm import tqdm

from openmc_model import objective

# Grid of data values for 2D example
tbr_values = []
for breeder_percent_in_breeder_plus_multiplier in tqdm(np.linspace(0, 100, 10)):
    for thickness in np.linspace(10, 200, 10):
        tbr_values.append({'breeder_percent_in_breeder_plus_multiplier': breeder_percent_in_breeder_plus_multiplier,
                           'blanket_breeder_li6_enrichment': blanket_breeder_li6_enrichment,
                           'tbr': -objective([breeder_percent_in_breeder_plus_multiplier,
                                              blanket_breeder_li6_enrichment])
                          })

with open('2d_tbr_values.json', mode="w", encoding="utf-8") as f:
    json.dump(tbr_values, f, indent=4)