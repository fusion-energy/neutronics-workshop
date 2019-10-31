#!/usr/env/python3

#run with the following command 
# trelis -batch -nographics make_faceted_geometry_with_materials.py 
# trelis make_faceted_geometry_with_materials.py 

import os
import json

os.system('rm *.log')
os.system('rm *.jou')

#cubit.cmd('reset')


def find_number_of_volumes_in_each_CAD_file(input_locations, basefolder=''):
    body_ids = ''
    for entry in input_locations:
      current_vols = cubit.parse_cubit_list("volume", "all")
      print(os.path.join(basefolder, entry['filename']))
      if entry['filename'].lower().endswith('.sat'):
        cubit.cmd('import acis "' + os.path.join(basefolder,entry['filename']) + '" separate_bodies no_surfaces no_curves no_vertices ')
      if entry['filename'].lower().endswith('.stp') or entry['filename'].lower().endswith('.step'):
        cubit.cmd('import step "' + os.path.join(basefolder,entry['filename']) + '" separate_bodies no_surfaces no_curves no_vertices ')
      short_file_name = os.path.split(entry['filename'])[-1]
      all_vols = cubit.parse_cubit_list("volume", "all")
      new_vols = set(current_vols).symmetric_difference(set(all_vols))
      new_vols = map(str, new_vols)
      print('new_vols', new_vols)
      current_bodies = cubit.parse_cubit_list("body", "all")
      if len(new_vols) > 1:
        cubit.cmd('unite vol ' + ' '.join(new_vols) + ' with vol '+' '.join(new_vols))
      all_vols = cubit.parse_cubit_list("volume", "all")
      new_vols_after_unite = set(current_vols).symmetric_difference(set(all_vols))
      new_vols_after_unite = map(str, new_vols_after_unite)
      entry['volumes'] = new_vols_after_unite
      cubit.cmd('group "'+short_file_name + '" add volume ' + ' '.join(entry['volumes']))
    cubit.cmd('separate body all')
    print(input_locations)
    return input_locations

def create_graveyard():
  current_vols = cubit.parse_cubit_list("volume", "all")
  #makes smaller bounding box
  cubit.cmd('create brick bounding box Volume all extended absolute 100')
  vols_after_small_box = cubit.parse_cubit_list("volume", "all")
  small_box_vols = set(current_vols).symmetric_difference(set(vols_after_small_box))
  small_bound_box = map(str, small_box_vols)[0]
  current_vols = cubit.parse_cubit_list("volume", "all")
  cubit.cmd('create brick bounding box Volume all extended absolute 200')
  vols_after_big_box = cubit.parse_cubit_list("volume", "all")
  big_box_vols = set(current_vols).symmetric_difference(set(vols_after_big_box))
  big_bound_box = map(str, big_box_vols)[0]
  current_vols = cubit.parse_cubit_list("volume", "all")
  cubit.cmd('subtract volume '+small_bound_box+' from volume '+big_bound_box)
  vols_after_substraction = cubit.parse_cubit_list("volume", "all")
  print('vols_after_substraction', vols_after_substraction)
  new_vols = set(current_vols).symmetric_difference(set(vols_after_substraction))
  for vol in new_vols:
    if vol not in small_box_vols and vol not in big_box_vols:
        graveyard_vol = str(vol)
  #graveyard = map(str, new_vols)
  print('graveyard vols =', graveyard_vol)
  cubit.cmd('group "mat:Graveyard" add volume '+graveyard_vol)
  cubit.cmd('volume '+graveyard_vol+' visibility off')
  return graveyard_vol

def tag_geometry_with_mats(geometry_details):
    for entry in geometry_details:
       #cubit.cmd('group "'+os.path.split(entry['filename'])[-1]+'" add volume ' +' '.join(entry['volumes'])) # can be performed here or in the file loading
       cubit.cmd('group "mat:'+entry['material'] + '" add volume ' + ' '.join(entry['volumes']))
       print(entry)

def imprint_and_merge_geometry(tolerance='1e-4'):
    cubit.cmd('imprint body all')
    cubit.cmd('merge tolerance '+tolerance)  # optional as there is a default
    cubit.cmd('merge vol all group_results')
    cubit.cmd('graphics tol angle 3')

def save_output_files(graveyard_vol, tolerance='1.0'):
    #this tolerance should be 1e-2 for production simulations
    with open('geometry_details_with_volumes.json', 'w') as outfile:
        json.dump(geometry_details, outfile, indent=4)
    cubit.cmd('set attribute on')
    # cubit.cmd('volume all scale 100')
    cubit.cmd('export dagmc "dagmc_notwatertight.h5m" faceting_tolerance '+tolerance)
    cubit.cmd('save as "dagmc.cub" overwrite')
    #cubit.cmd('delete Group "mat:Graveyard"') #would be tidier if these trelis allowed group commands like these without the sdk
    cubit.cmd('delete volume '+graveyard_vol)
    cubit.cmd('save as "dagmc.trelis" overwrite')
    print('DAGMC model creation complete, use dagmc_notwatertight.h5m in your neutronics simulation' )

def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

# def scale_geometry(geometry_details):
  


with open('geometry_details.json') as f:
    geometry_details = byteify(json.load(f))


geometry_details = find_number_of_volumes_in_each_CAD_file(geometry_details)

# scale_geometry(geometry_details)
graveyard_vol = create_graveyard()

tag_geometry_with_mats(geometry_details)

imprint_and_merge_geometry()

save_output_files(graveyard_vol)
