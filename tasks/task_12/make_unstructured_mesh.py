#!/usr/env/python3
import os
import json

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

def save_tet_details_to_json_file(geometry_details,filename='mesh_details.json'):
    for entry in geometry_details:
        material = entry['material']
    tets_in_volumes = cubit.parse_cubit_list("tet", " in volume "+" ".join(entry['volumes']))
    print('material ',material,' has ',len(tets_in_volumes),' tets')
    entry['tet_ids'] = tets_in_volumes
    with open(filename, 'w') as outfile:
        json.dump(geometry_details, outfile, indent =4)

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
      #cubit.cmd('volume in group '+str(starting_group_id)+' copy rotate 45 about z repeat 7')
    cubit.cmd('separate body all')
    return input_locations

def imprint_and_merge_geometry(tolerance='1e-4'):
    cubit.cmd('imprint body all')
    cubit.cmd('merge tolerance '+tolerance)  # optional as there is a default
    cubit.cmd('merge vol all group_results')
    cubit.cmd('graphics tol angle 3')


cubit.cmd('reset')

cubit.cmd('set attribute on')

with open('manifest.json') as json_file:
    data = byteify(json.load(json_file))

input_locations = []
for entry in data:
    if 'mesh' in entry.keys():
        input_locations.append(entry)
geometry_details = find_number_of_volumes_in_each_step_file(input_locations, str(os.path.abspath('.')))

imprint_and_merge_geometry()

current_vols = cubit.parse_cubit_list("volume", "all")

cubit.cmd('Trimesher volume gradation 1.3')

cubit.cmd('volume all size auto factor 5')
print(geometry_details)
for entry in geometry_details:
    for volume in entry['volumes']:
        cubit.cmd('volume '+str(volume)+' size auto factor 6') # this number is the size of the mesh 1 is small 10 is large
        cubit.cmd('volume all scheme tetmesh proximity layers off geometric sizing on')
        if "size" in entry['mesh']:
            cubit.cmd('volume '+str(volume)+' '+entry['mesh']) #' size 0.5'
        else:
            cubit.cmd('volume '+str(volume))
        cubit.cmd('mesh volume '+str(volume))


cubit.cmd('export mesh "tet_mesh.exo" overwrite')
# cubit.cmd('export abaqus "tet_mesh.inp" overwrite') # asci format, not goood for large meshes
# cubit.cmd('save as "tet_mesh.cub" overwrite') # mbconvert code is older than the exo equivilent

print('unstrutured mesh saved as tet_mesh.exo')

save_tet_details_to_json_file(geometry_details)
