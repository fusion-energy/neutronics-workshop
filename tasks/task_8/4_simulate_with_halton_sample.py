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
import ghalton
import pandas as pd

from openmc_model import simulate_model

# reads all json files into pandas dataframe to check if the simulations have been previously performed
path_to_json = "outputs"
Path('outputs/').mkdir(parents=True, exist_ok=True)
list_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
resultdict = []
for filename in list_files:
    try:
        with open(os.path.join(path_to_json, filename), "r") as inputjson:
            resultdict.append(json.load(inputjson))
    except:
        print('no files created yet')
results_df = pd.DataFrame(resultdict)



number_of_new_simulations = 7  # this value will need to be changed to cover the space better

for breeder_material_name in ['Li4SiO4', 'F2Li2BeF2', 'Li', 'Pb84.2Li15.8']:

    sequencer = ghalton.Halton(2)

    if len(results_df) > 0:
        existing_simulations_for_this_material = results_df[results_df['breeder_material_name'] == breeder_material_name]

        coords = sequencer.get(number_of_new_simulations + len(existing_simulations_for_this_material))

    else:
        coords = sequencer.get(number_of_new_simulations)

    # x = [item for sublist in x for item in sublist]
    for i, coord in enumerate(coords):
        enrichment = coord[0]
        thickness = coord[1]*500

        inputs = {'batches': 2,
                  'nps': 1000,  
                  'enrichment': enrichment,
                  'inner_radius': 500,
                  'thickness': thickness,
                  'breeder_material_name': breeder_material_name,
                  'temperature_in_C': 500
                 }

        result = simulate_model(**inputs)

        inputs['sample'] = 'halton'

        result.update(inputs)

        filename = 'outputs/'+str(uuid.uuid4())+'.json'
        with open(filename, mode='w', encoding='utf-8') as f:
            json.dump(result, f, indent=4)
