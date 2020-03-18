#!/usr/bin/env python3

"""
2_simulate_with_grid_sample.py simulates and x y grid of sample points.
This has limits as the number of dimentions increase and is inefficient
when the number of samples is increase.
"""

import json
import uuid
import math
import argparse

import numpy as np
from tqdm import tqdm

from openmc_model import simulate_model

parser = argparse.ArgumentParser()
parser.add_argument(
    "-n", "--number", default=16, type=int, help="number of simulations to perform"
)
args = parser.parse_args()


number_of_steps = math.floor(math.sqrt(args.number))

print("running simulations with grid sampling")

for enrichment in tqdm(np.linspace(0, 100, number_of_steps)):
    for thickness in np.linspace(0, 500, number_of_steps):

        result = simulate_model(enrichment=enrichment, thickness=thickness)

        result["sample"] = "grid"

        filename = "outputs/" + str(uuid.uuid4()) + ".json"
        with open(filename, mode="w", encoding="utf-8") as f:
            json.dump(result, f, indent=4)
