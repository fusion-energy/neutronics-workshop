#!/usr/bin/env python3

"""
2_simulate_with_grid_sample.py simulates and x y grid of sample points.
This has limits as the number of dimentions increase and is inefficient
when the number of samples is increase.
"""

from pathlib import Path
import json
import uuid
import math
import argparse

import numpy as np
from tqdm import tqdm

from openmc_model import find_tbr_hcpb

parser = argparse.ArgumentParser()
parser.add_argument(
    "-n", "--number", default=16, type=int, help="number of simulations to perform"
)
args = parser.parse_args()


number_of_steps = math.floor(math.sqrt(args.number))

print("running simulations with grid sampling")

for breeder_percent_in_breeder_plus_multiplier_ratio in tqdm(np.linspace(0, 100, number_of_steps)):
    for blanket_breeder_li6_enrichment in np.linspace(0, 100, number_of_steps):

        result = find_tbr_hcpb(breeder_percent_in_breeder_plus_multiplier_ratio,
                               blanket_breeder_li6_enrichment)

        result["sample"] = "grid"

        filename = "outputs/" + str(uuid.uuid4()) + ".json"
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with open(filename, mode="w", encoding="utf-8") as f:
            json.dump(result, f, indent=4)
