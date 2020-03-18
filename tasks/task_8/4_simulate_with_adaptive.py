#!/usr/bin/env python3

"""
4_simulate_with_adaptive.py tries to target areas of high gradient when
selecting the sample coordinates so that samples are not wasted on
regions that are relativly flat. Allows for more efficient use of compute
"""

import json
import uuid
import argparse

import adaptive
from openmc_model import simulate_model


def find_tbr(x):

    enrichment, thickness = x

    result = simulate_model(enrichment=enrichment, thickness=thickness)

    result["sample"] = "adaptive"

    filename = "outputs/" + str(uuid.uuid4()) + ".json"
    with open(filename, mode="w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

    return result["TBR"]


parser = argparse.ArgumentParser()
parser.add_argument(
    "-n", "--number", default=16, type=int, help="number of simulations to perform"
)
args = parser.parse_args()

print("running simulations with adaptive sampling")

learner = adaptive.Learner2D(find_tbr, bounds=[(0, 100), (1, 500)])

runner = adaptive.Runner(learner, ntasks=1, goal=lambda l: l.npoints > args.number)

# example goal setting for acceptable coverage error is also possible
# runner = adaptive.Runner(learner, ntasks=1, goal=lambda l: l.loss() < 0.01)

runner.ioloop.run_until_complete(runner.task)
