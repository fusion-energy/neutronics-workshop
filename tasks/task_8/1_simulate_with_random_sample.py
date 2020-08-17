#!/usr/bin/env python3

"""
1_simulate_with_random_sample.py generates randomly selected coordinates
within the parameter space samples are often clustered which is inefficient
and this does not scale well as dimentions are increased
"""

from pathlib import Path
import json
import uuid
import argparse

import numpy as np
from tqdm import tqdm

from openmc_model import find_tbr_hcpb

parser = argparse.ArgumentParser()
parser.add_argument(
    "-n", "--number", default=16, type=int, help="number of simulations to perform"
)
args = parser.parse_args()


def run_simulation(breeder_percent_in_breeder_plus_multiplier_ratio, blanket_breeder_li6_enrichment):

    result = find_tbr_hcpb(breeder_percent_in_breeder_plus_multiplier_ratio,
                           blanket_breeder_li6_enrichment)

    result["sample"] = "random"

    filename = "outputs/" + str(uuid.uuid4()) + ".json"
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    with open(filename, mode="w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)



print("running corner simulations")

for i, j in tqdm(zip([0, 0, 100, 100], [0, 100, 0, 100]), total=4):

    run_simulation(i, j)

    
print("running simulations with random sampling")

for i in tqdm(range(args.number)):

    breeder_percent_in_breeder_plus_multiplier_ratio = np.random.uniform(0, 100)
    blanket_breeder_li6_enrichment = np.random.uniform(1, 100)

    run_simulation(breeder_percent_in_breeder_plus_multiplier_ratio, blanket_breeder_li6_enrichment)
