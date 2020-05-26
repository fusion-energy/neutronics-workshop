#!/usr/env/python3
import os
import json

def find_number_of_volumes_in_each_step_file(input_locations, basefolder):
    body_ids = ''
    volumes_in_each_step_file = []
    #all_groups=cubit.parse_cubit_list("group","all")
    #starting_group_id = len(all_groups)
    for entry in input_locations:
      #starting_group_id = starting_group_id +1
      current_vols = cubit.parse_cubit_list("volume", "all")
      print(os.path.join(basefolder, entry['filename']))
      if entry['filename'].endswith('.sat'):
        import_type = 'acis'
      if entry['filename'].endswith('.stp') or entry['filename'].endswith('.step'):
        import_type = 'step'
      short_file_name = os.path.split(entry['filename'])[-1]
      #print('short_file_name',short_file_name)
      #cubit.cmd('import '+import_type+' "' + entry['filename'] + '" separate_bodies no_surfaces no_curves no_vertices group "'+str(short_file_name)+'"')
      cubit.cmd('import '+import_type+' "' + os.path.join(basefolder,entry['filename']) + '" separate_bodies no_surfaces no_curves no_vertices ')
      all_vols = cubit.parse_cubit_list("volume", "all")
      new_vols = set(current_vols).symmetric_difference(set(all_vols))
      new_vols = map(str, new_vols)
      print('new_vols', new_vols, type(new_vols))
      current_bodies = cubit.parse_cubit_list("body", "all")
      print('current_bodies', current_bodies)
      #volumes_in_group = cubit.cmd('volume in group '+str(starting_group_id))
      #print('volumes_in_group',volumes_in_group,type(volumes_in_group))
      if len(new_vols) > 1:
        cubit.cmd('unite vol ' + ' '.join(new_vols) + ' with vol '+' '.join(new_vols))
      all_vols = cubit.parse_cubit_list("volume", "all")
      new_vols_after_unite = set(current_vols).symmetric_difference(set(all_vols))
      new_vols_after_unite = map(str, new_vols_after_unite)
      #cubit.cmd('group '+str(starting_group_id)+' copy rotate 45 about z repeat 7')
      entry['volumes'] = new_vols_after_unite
      cubit.cmd('group "'+short_file_name + '" add volume ' + ' '.join(entry['volumes']))
      if 'surface_reflectivity' in entry.keys():
        entry['surface_reflectivity'] = find_all_surfaces_of_reflecting_wedge(new_vols_after_unite)
        print("entry['surface_reflectivity']", entry['surface_reflectivity'])
      #cubit.cmd('volume in group '+str(starting_group_id)+' copy rotate 45 about z repeat 7')
    cubit.cmd('separate body all')
    return input_locations

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

def tag_geometry_with_mats(geometry_details):
    for entry in geometry_details:
       cubit.cmd('group "mat:'+entry['material'] + '" add volume ' + ' '.join(entry['volumes']))


def imprint_and_merge_geometry(tolerance='1e-4'):
    cubit.cmd('imprint body all')
    cubit.cmd('merge tolerance '+tolerance)  # optional as there is a default
    cubit.cmd('merge vol all group_results')
    cubit.cmd('graphics tol angle 3')


def save_output_files():
    cubit.cmd('set attribute on')
    # use a faceting_tolerance 1.0e-4 or smaller for accurate simulations
    cubit.cmd('export dagmc "dagmc_notwatertight.h5m" faceting_tolerance 1.0e-2')
    #os.system('mbconvert -1 dagmc_notwatertight.h5m dagmc_notwatertight_edges.h5m')
    with open('geometry_details.json', 'w') as outfile:
        json.dump(geometry_details, outfile, indent=4)

with open('manifest.json') as f:
    geometry_details = byteify(json.load(f))

geometry_details = find_number_of_volumes_in_each_step_file(geometry_details, '/home/shimwell/openmc_workshop/tasks/task_12/')

tag_geometry_with_mats(geometry_details)

imprint_and_merge_geometry()

save_output_files()
