#!/usr/bin/env python3

"""2_find_cell_volume.py: Calculates the volume of cells and materials."""

import openmc
import json

#MATERIALS#

density_of_iron_in_g_per_cm3 = 7.75
firstwall_material = openmc.Material(name='iron')
firstwall_material.set_density('g/cm3', density_of_iron_in_g_per_cm3)
firstwall_material.add_element('Fe', 1., percent_type='wo')

breeder_material = openmc.Material(name="lithium")
breeder_material.set_density('g/cm3', 8.5)
breeder_material.add_element('Li', 1.0)

mats = openmc.Materials([firstwall_material, breeder_material])
mats.export_to_xml()

#GEOMETRY#

#surfaces
vessel_inner_surface = openmc.Sphere(r=500) # when increasing the radius this number needs to change
first_wall_outer_surface = openmc.Sphere(r=510) # when increasing the radius this number needs to change
breeder_blanket_outer_surface = openmc.Sphere(r=610,boundary_type='vacuum')


# cells
inner_vessel_region = -vessel_inner_surface
inner_vessel_cell = openmc.Cell(region=inner_vessel_region)
# there is no material fill as the default is a void

first_wall_region = -first_wall_outer_surface & +vessel_inner_surface
first_wall_cell = openmc.Cell(region=first_wall_region)
first_wall_cell.fill = firstwall_material

breeder_blanket_region = +first_wall_outer_surface & -breeder_blanket_outer_surface
breeder_blanket_cell = openmc.Cell(region=breeder_blanket_region)
breeder_blanket_cell.fill = breeder_material

universe = openmc.Universe(cells=[inner_vessel_cell, first_wall_cell, breeder_blanket_cell])
geom = openmc.Geometry(universe)
geom.export_to_xml()


# volume calculates for materials require a bounding box
lower_left = (-1000, -1000, -1000.)
upper_right = (1000, 1000, 1000.)
material_vol_calc = openmc.VolumeCalculation([firstwall_material, breeder_material], 100000, lower_left, upper_right)

cell_vol_calc = openmc.VolumeCalculation([inner_vessel_cell, first_wall_cell, breeder_blanket_cell], 100000)

settings = openmc.Settings()
settings.volume_calculations = [cell_vol_calc, material_vol_calc]
settings.run_mode = 'volume'
settings.export_to_xml()
openmc.run()

cell_vol_calc_results = openmc.VolumeCalculation.from_hdf5('volume_1.h5')




print('\ninner_vessel_cell volume', cell_vol_calc_results.volumes[1], 'cm3')
print('first_wall_cell volume', cell_vol_calc_results.volumes[2], 'cm3')
print('breeder_blanket_cell volume', cell_vol_calc_results.volumes[3], 'cm3\n')


material_vol_calc_results = openmc.VolumeCalculation.from_hdf5('volume_2.h5')
print('firstwall_material volume', material_vol_calc_results.volumes[1], 'cm3')
print('breeder_material volume', material_vol_calc_results.volumes[2], 'cm3')

# the cell_vol_calc_results are combined with errors, you can access the
# result using the .nominal_value method

volume_of_firstwall_cell = cell_vol_calc_results.volumes[2].nominal_value

iron_atomic_mass_in_g = 55.845*1.66054E-24 # molar mass multiplier by the atomic mass unit (u)
number_of_iron_atoms = volume_of_firstwall_cell * density_of_iron_in_g_per_cm3 / (iron_atomic_mass_in_g)

print('Number of iron atoms in the firstwall ',number_of_iron_atoms)

json_output = {'Firstwall cell volume': volume_of_firstwall_cell,
               'Number of iron atoms in firstwall': number_of_iron_atoms}

with open('2_find_cell_volume_results.json', 'w') as file_object:
    json.dump(json_output, file_object, indent=2)