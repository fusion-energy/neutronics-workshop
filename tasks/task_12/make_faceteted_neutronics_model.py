#!/usr/env/python3
import os
import json

# os.system('rm *.log')
# os.system('rm *.jou')

#cubit.cmd('reset')


def delete_old_files(output_filename_stub):
    filenames_to_del = ['geometry_details.json',
                        output_filename_stub + '.h5m',
                        output_filename_stub + '.trelis',
                        output_filename_stub + '.stl',
                        output_filename_stub + '_edges.h5m'
                        ]
    for filename in filenames_to_del:
        os.system('rm '+filename)


def check_files_creation(output_filename_stub):
    All_files_produced = True
    filenames_to_check = ['geometry_details.json',
                          output_filename_stub + '.h5m',
                          output_filename_stub + '.trelis',
                          output_filename_stub + '.stl',
                          output_filename_stub + '_edges.h5m'
                          ]
    for filename in filenames_to_check:
        file_exists = os.path.isfile(filename)
        if not file_exists:
            raise ValueError('Exspected output file not found', filename)
            All_files_produced = False
    print('All_files_produced:', All_files_produced)


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


def find_all_surfaces_of_reflecting_wedge(new_vols):
  surfaces_in_volume = cubit.parse_cubit_list("surface", " in volume "+' '.join(new_vols))
  print(surfaces_in_volume)
  surface_info_dict = {}
  for surface_id in surfaces_in_volume:
    surface = cubit.surface(surface_id)
    #area = surface.area()
    vertex_in_surface = cubit.parse_cubit_list("vertex", " in surface " + str(surface_id))
    if surface.is_planar() == True and len(vertex_in_surface) == 4:
      surface_info_dict[surface_id] = {'reflector': True}
    else:
      surface_info_dict[surface_id] = {'reflector': False}
  print('surface_info_dict', surface_info_dict)
  return surface_info_dict


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


def find_reflecting_surfaces_of_reflecting_wedge(geometry_details):
    wedge_volume = None
    for entry in geometry_details:
        if 'surface_reflectivity' in entry.keys():
          if entry['surface_reflectivity'] == True:
            surface_info_dict = entry['surface_reflectivity']
            wedge_volume = ' '.join(entry['volumes'])
            surfaces_in_wedge_volume = cubit.parse_cubit_list("surface", " in volume "+str(wedge_volume))
            for surface_id in surface_info_dict.keys():
                if surface_info_dict[surface_id]['reflector'] == True:
                    print(surface_id, 'surface originally reflecting but does it still exist')
                    if surface_id not in surfaces_in_wedge_volume:
                        del surface_info_dict[surface_id]
            for surface_id in surfaces_in_wedge_volume:
                if surface_id not in surface_info_dict.keys():
                    surface_info_dict[surface_id] = {'reflector': True}
                    cubit.cmd('group "boundary:Reflecting" add surf ' + str(surface_id))
                    cubit.cmd('surface ' + str(surface_id)+' visibility on')
            entry['surface_reflectivity'] = surface_info_dict
            return geometry_details, wedge_volume
    return geometry_details, wedge_volume


def scale_geometry(geometry_details):
  for entry in geometry_details:
    if 'scale' in entry.keys():
      cubit.cmd('volume ' + ' '.join(entry['volumes'] + ' scale ' + str(entry['scale'])))


def color_geometry(geometry_details):
    assigned_colors = []
    for entry in geometry_details:
       print(entry)
       if "color" in entry.keys():
        if entry['color'].strip().lower().startswith('rgb'):
          color_name = 'new_color_' + '-'.join(entry['color'].split())
          if len(assigned_colors) >= 15:
            print('WARNING color set to grey as the number of custom colors in Trelis is limited to 15')
            cubit.cmd('Color volume '+' '.join(entry['volumes']) + ' grey')
          else:
            if color_name not in assigned_colors:
                cubit.cmd('Color Define "'+color_name+'" '+join(entry['color']))
                assigned_colors.append(color_name)
            cubit.cmd('Color volume ' + ' '.join(entry['volumes']) + ' ' + color_name)
        else:    
          print('setting ' + geometry_details['filename'] + ' to ' + entry['color'])
          # Available Colors https://www.csimsoft.com/help/appendix/available_colors.htm
          cubit.cmd('Color volume ' + ' '.join(entry['volumes']) + ' ' + entry['color'])
       else:
        cubit.cmd('Color volume '+' '.join(entry['volumes']) + ' grey')


def tag_geometry_with_mats_and_tallies(geometry_details):
    for entry in geometry_details:
       #cubit.cmd('group "'+os.path.split(entry['filename'])[-1]+'" add volume ' +' '.join(entry['volumes'])) # can be performed here or in the file loading
       cubit.cmd('group "mat:'+entry['material'] + '" add volume ' + ' '.join(entry['volumes']))
       print(entry)
       if "tallies" in entry.keys():
        for tally in entry['tallies']:
          print('adding tally group', tally)
          cubit.cmd('group "tally:'+tally+'" add volume ' + ' '.join(entry['volumes']))


def imprint_and_merge_geometry(tolerance='1e-4'):
    cubit.cmd('imprint body all')
    cubit.cmd('merge tolerance '+tolerance)  # optional as there is a default
    cubit.cmd('merge vol all group_results')
    cubit.cmd('graphics tol angle 3')


def save_output_files(output_filename_stub, graveyard_vol, wedge_volume):
    cubit.cmd('set attribute on')
    # use a faceting_tolerance 1.0e-4 for accurate simulations
    cubit.cmd('export dagmc "'+output_filename_stub + '.h5m" faceting_tolerance 1.0e-2')
    #os.system('mbconvert -1 '+output_filename_stub + '.h5m '+output_filename_stub+'_edges.h5m')
    with open('geometry_details.json', 'w') as outfile:
        json.dump(geometry_details, outfile, indent=4)


with open('filename_details.json') as f:
    filename_details = byteify(json.load(f))

output_filename_stub = 'dagmc_notwatertight'

delete_old_files(output_filename_stub)

model_description = filename_details['model_description']

with open(model_description) as f:
    geometry_details = byteify(json.load(f))

geometry_details = find_number_of_volumes_in_each_step_file(geometry_details, os.path.dirname(model_description))

scale_geometry(geometry_details)

graveyard_vol = create_graveyard()

color_geometry(geometry_details)

tag_geometry_with_mats_and_tallies(geometry_details)

imprint_and_merge_geometry()

updated_wedge_surface_info_dict, wedge_volume = find_reflecting_surfaces_of_reflecting_wedge(geometry_details)

save_output_files(output_filename_stub, graveyard_vol, wedge_volume)

check_files_creation(output_filename_stub)
