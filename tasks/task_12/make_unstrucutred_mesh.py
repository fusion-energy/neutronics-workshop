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
    return geometry_details

cubit.cmd('reset')

cubit.cmd('set attribute on')

with open('manifest.json') as json_file:
    data = byteify(json.load(json_file))
filenames = [entry['filename'] for entry in data]
print('filenames', filenames)
basefolder ='/home/shimwell/openmc_workshop/tasks/task_12/'
for filename in filenames:
  print(basefolder+filename)
  cubit.cmd('import step "' + basefolder+filename + '"')
cubit.cmd('separate body all')

cubit.cmd('imprint body all')
cubit.cmd('merge tolerance '+tolerance)  # optional as there is a default
cubit.cmd('merge vol all group_results')
cubit.cmd('graphics tol angle 3')


cubit.cmd('delete mesh')
current_vols =cubit.parse_cubit_list("volume", "all")


cubit.cmd('Trimesher volume gradation 1.3')

cubit.cmd('volume all size auto factor 5')


for volume in current_vols:
    cubit.cmd('volume '+str(volume)+' size auto factor 2') # this number is the size of the mesh 1 is small 10 is large
    cubit.cmd('volume all scheme tetmesh proximity layers off geometric sizing on')
    cubit.cmd('mesh volume '+str(volume))


cubit.cmd('save as "'+output_filename_stub+'.cub" overwrite')

print('unstrutured mesh saved as ',output_filename_stub+'.cub')

save_tet_details_to_json_file(geometry_details)


# additional steps needed for unstructured mesh https://svalinn.github.io/DAGMC/usersguide/tally.html
# os.system('rm *.jou')
# os.system('rm *.log')

# os.system('mbconvert '+output_filename_stub+'.cub '+output_filename_stub+'.h5m')
# os.system('mbconvert '+output_filename_stub+'.h5m '+output_filename_stub+'.vtk')

#for each element in the mesh
# find all material names
# allocate material numbers based on these names ('alpha')
# write mcr2s material card using

# find material name
# alocate materials using their name