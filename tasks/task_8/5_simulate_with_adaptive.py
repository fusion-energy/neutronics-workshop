#!/usr/bin/env python3

""" simulate_model.py: obtains a few netronics parameters for a basic tokamak geometry ."""
""" run with python3 simulate_tokamak_model.py | tqdm >> /dev/null """
""" outputs results to a files in json format"""

import json
import uuid

import numpy as np
from tqdm import tqdm

import adaptive
from openmc_model import simulate_model


def find_tbr(x):

    enrichment, thickness = x

    breeder_material_name = 'Li4SiO4'
    inputs = {'batches': 2,
              'nps': 1000,
              'enrichment': enrichment,
              'inner_radius': 500,
              'thickness': thickness,
              'breeder_material_name': breeder_material_name,
              'temperature_in_C': 500
             }

    result = simulate_model(**inputs)

    inputs['sample'] = 'adaptive'

    result.update(inputs)

    filename = 'outputs/'+str(uuid.uuid4())+'.json'
    with open(filename, mode='w', encoding='utf-8') as f:
        json.dump(result, f, indent=4)

    return result['TBR']



learner = adaptive.Learner2D(find_tbr, bounds=[(0, 100), (1, 500)])

runner = Runner(learner, goal=stop_after(minutes=5))
# runner.start()
# find_tbr((50,50))
