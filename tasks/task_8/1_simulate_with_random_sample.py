#!/usr/bin/env python3

""" simulate_model.py: obtains a few netronics parameters for a basic tokamak geometry ."""
""" run with python3 simulate_tokamak_model.py | tqdm >> /dev/null """
""" outputs results to a files in json format"""

import json
import os
import numpy as np
from tqdm import tqdm
import uuid

from pathlib import Path


from openmc_model import simulate_model


number_of_simulations = 5 # this value can be changed to perform more simulation

for i in tqdm(range(number_of_simulations)):

    for breeder_material_name in ['Li4SiO4', 'F2Li2BeF2', 'Li', 'Pb84.2Li15.8']:

        enrichment = np.random.uniform(0, 100)
        thickness = np.random.uniform(1, 500)

        inputs = {'batches':2,
                  'nps':1000,  
                  'enrichment':enrichment,
                  'inner_radius':500,
                  'thickness':thickness,
                  'breeder_material_name':breeder_material_name,
                  'temperature_in_C':500
                  }

        result = simulate_model(**inputs)

        inputs['sample'] = 'random'

        result.update(inputs)

        filename = 'outputs/'+str(uuid.uuid4())+'.json'
        with open(filename, mode='w', encoding='utf-8') as f:
            json.dump(result, f, indent=4)