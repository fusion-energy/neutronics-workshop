#!/usr/bin/env python3

"""example_CAD_simulation.py: uses a dagmc.h5m file for the geometry."""

__author__ = "Jonathan Shimwell"

import openmc
import json
import os
from neutronics_material_maker import Material
from parametric_plasma_source import Plasma

# MATERIALS using the neutronics material maker

breeder_material = Material(material_name='Li4SiO4',
                            enrichment=90,
                            # material_tag='blanket_material').neutronics_material
                            ).neutronics_material
breeder_material.name='blanket_material'
copper = Material(material_name="copper",
                #   material_tag="center_column_material").neutronics_material
                  ).neutronics_material
copper.name='center_column_material'


eurofer = Material(material_name='eurofer').neutronics_material

mats = openmc.Materials([breeder_material, eurofer, copper])


# GEOMETRY using dagmc doesn't contain any CSG geometry

universe = openmc.Universe()
geom = openmc.Geometry(universe)


# SIMULATION SETTINGS

# Instantiate a Settings object
sett = openmc.Settings()
batches = 1002
sett.batches = batches
sett.inactive = 0
sett.particles = 1000
sett.run_mode = 'fixed source'
# sett.output = {'tallies': False}
sett.dagmc = True  # this is the openmc command enables use of the dagmc.h5m file as the geometry


# creates a source object
source = openmc.Source()
# this creates a neutron distribution with the shape of a tokamak plasma
my_plasma = Plasma(elongation=2.9,
                   minor_radius=1.118*100,
                   major_radius=1.9*100,
                   triangularity = 0.55)
# there are other parameters that can be set for the plasma, but we can use the defaults for now
my_plasma.export_plasma_source('my_custom_plasma_source.so')
# sets the source poition, direction and energy with predefined plasma parameters (see source_sampling.cpp)
source.library = './my_custom_plasma_source.so'
sett.source = source


tallies = openmc.Tallies()

# this loads up the tet mesh created in Trelis so that it can be used as a mesh filter
# umesh = openmc.UnstructuredMesh("tet_mesh.inp")
# umesh = openmc.UnstructuredMesh("tet_mesh.exo")
umesh = openmc.UnstructuredMesh("tet_mesh.h5m")
mesh_filter = openmc.MeshFilter(umesh)

umesh_tally = openmc.Tally(name='tally_on_umesh')
umesh_tally.filters = [mesh_filter]
umesh_tally.scores = ['heating']
umesh_tally.estimator = 'tracklength'
tallies.append(umesh_tally)


# Run OpenMC!
model = openmc.model.Model(geom, mats, sett, tallies)
# model.run()
model.run()
