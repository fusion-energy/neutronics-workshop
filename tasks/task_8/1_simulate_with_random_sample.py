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

from openmc_model import simulate_model

parser = argparse.ArgumentParser()
parser.add_argument(
    "-n", "--number", default=16, type=int, help="number of simulations to perform"
)
args = parser.parse_args()


print("running simulations with random sampling")

for i in tqdm(range(args.number)):

    enrichment = np.random.uniform(0, 100)
    thickness = np.random.uniform(1, 500)

    result = simulate_model(enrichment=enrichment, thickness=thickness)

    result["sample"] = "random"

    filename = "outputs/" + str(uuid.uuid4()) + ".json"
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    with open(filename, mode="w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)
