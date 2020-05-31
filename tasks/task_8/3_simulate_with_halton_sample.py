#!/usr/bin/env python3

"""
3_simulate_with_halton_sample.py samples 16 points within the parameter space
using the Halton method. The benefit of this method over random is that there
is less clustering of sample points so each sample point adds more information.
The benefit of this over grid sampling is that if the study increases in scope
and more points are added then this can be accommodated in an efficient manner
"""

from pathlib import Path
import json
import uuid
import argparse

import ghalton
from tqdm import tqdm

from openmc_model import find_tbr_hcpb

parser = argparse.ArgumentParser()
parser.add_argument(
    "-n", "--number", default=16, type=int, help="number of simulations to perform"
)
args = parser.parse_args()


sequencer = ghalton.Halton(2)
coords = sequencer.get(args.number)

print("running simulations with halton sampling")

for coord in tqdm(coords):

    breeder_percent_in_breeder_plus_multiplier_ratio = coord[0] * 100  # scales sampling from 0 to 100
    blanket_breeder_li6_enrichment = coord[1] * 100  # scales sampling from 0 to 100

    result = find_tbr_hcpb(breeder_percent_in_breeder_plus_multiplier_ratio,
                           blanket_breeder_li6_enrichment)

    result["sample"] = "halton"

    filename = "outputs/" + str(uuid.uuid4()) + ".json"
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    with open(filename, mode="w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)
