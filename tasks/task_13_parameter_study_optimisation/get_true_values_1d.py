import json


import numpy as np
from tqdm import tqdm

from openmc_model import objective

# Grid of data values 1D example
tbr_values = []
for breeder_percent_in_breeder_plus_multiplier in tqdm(np.linspace(0, 100, 101)):
    tbr_values.append({'breeder_percent_in_breeder_plus_multiplier':breeder_percent_in_breeder_plus_multiplier,
                       'tbr':-objective([breeder_percent_in_breeder_plus_multiplier])})

with open('1d_tbr_values.json', mode="w", encoding="utf-8") as f:
    json.dump(tbr_values, f, indent=4)
