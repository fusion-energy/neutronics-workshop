#!/usr/bin/env python3

"""
3_simulate_with_halton_sample.py samples 16 points within the parameter space
using the Halton method. The benefit of this method over random is that there
is less clustering of sample points so each sample point adds more information.
The benefit of this over grid sampling is that if the study increases in scope
and more points are added then this can be accommodated in an efficient manner
"""

import json
import uuid
import argparse

import ghalton
from tqdm import tqdm

from openmc_model import simulate_model

parser = argparse.ArgumentParser()
parser.add_argument(
    "-n", "--number", default=16, type=int, help="number of simulations to perform"
)
args = parser.parse_args()


sequencer = ghalton.Halton(2)
coords = sequencer.get(args.number)

print("running simulations with halton sampling")

for i, coord in tqdm(enumerate(coords)):

    enrichment = coord[0] * 100  # scales smapling from 0 to 100
    thickness = coord[1] * 500  # scales smapling from 0 to 500

    result = simulate_model(enrichment=enrichment, thickness=thickness)

    result["sample"] = "halton"

    filename = "outputs/" + str(uuid.uuid4()) + ".json"
    with open(filename, mode="w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)
