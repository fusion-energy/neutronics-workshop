# This example has a sphere of concrete with a second smaller shell of concrete
# surrounding the sphere.

# The first simulation is analog with no variance reduction / weight windows.
# This simulation shows that not many neutrons get to the shell and the 
# consequently the neutron spectra on the shell cell is unresolved. Additional
# batches improve the neutron spectra but it is clear that it would take many
# batches to get a reasonable neutron spectra.
#
# The second simulation makes use of a variance reduction method called weight
# windows. The value of the weight windows is assigned using the MAGIC method.
# https://scientific-publications.ukaea.uk/papers/application-of-novel-global-variance-reduction-methods-to-fusion-radiation-transport-problems/
# The value of the weight windows are updated with each simulated batch and as
# the simulation runs for longer the weight windows improve gradually as does
# spectra tally.

import openmc
# Note this example makes use of OpenMC lib which provides python bindings to
# the C/C++ methods in OpenMC and allows more direct control of the Monte Carlo
# simulation. In this example we iterate through the batches and access the
# tally result each time.
# Link to openmc.lib documentation https://docs.openmc.org/en/stable/pythonapi/capi.html
import openmc.lib
import numpy as np
import matplotlib.pyplot as plt


# This makes concrete which is a regular shielding material
mat_concrete = openmc.Material()
mat_concrete.add_element("H",0.168759)
mat_concrete.add_element("C",0.001416)
mat_concrete.add_element("O",0.562524)
mat_concrete.add_element("Na",0.011838)
mat_concrete.add_element("Mg",0.0014)
mat_concrete.add_element("Al",0.021354)
mat_concrete.add_element("Si",0.204115)
mat_concrete.add_element("K",0.005656)
mat_concrete.add_element("Ca",0.018674)
mat_concrete.add_element("Fe",0.00426)
mat_concrete.set_density("g/cm3", 2.3)

my_materials = openmc.Materials([mat_concrete])

# surfaces
surf1 = openmc.Sphere(r=170)
outer_surface = openmc.Sphere(r=200, boundary_type="vacuum")

# regions
region_1 = -surf1
region_2 = -outer_surface & +surf1

# cells
cell_1 = openmc.Cell(region=region_1)
cell_1.fill = mat_concrete
cell_2 = openmc.Cell(region=region_2)
cell_2.fill = mat_concrete

# settings
my_settings = openmc.Settings()

my_geometry = openmc.Geometry([cell_1, cell_2])

# A point source 14MeV emitting neutron
source = openmc.Source()
source.space = openmc.stats.Point((0.0, 0.0, 0.0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1.0])
source.particle = "neutron"

my_settings = openmc.Settings()
my_settings.run_mode = "fixed source"
my_settings.source = source
my_settings.particles = 50000
my_settings.batches = 5
# the mesh tallies produce large tallies.out files so this output setting avoids writing the tallies.out and saves time
my_settings.output = {'tallies': False}

my_tallies = openmc.Tallies()

# This spherical mesh tally is used for generating the weight windows.
mesh = openmc.SphericalMesh()
mesh.r_grid = np.linspace(0, outer_surface.r, 5000)
mesh_filter = openmc.MeshFilter(mesh)
flux_tally_for_ww = openmc.Tally(name="flux tally")
flux_tally_for_ww.filters = [mesh_filter]
flux_tally_for_ww.scores = ["flux"]
flux_tally_for_ww.id = 42
my_tallies.append(flux_tally_for_ww)

# This spectrum tally is on the outer shell and shows then energy distribution
# of neutrons present in the cell.
energy_filter = openmc.EnergyFilter.from_group_structure('CCFE-709')
surface_filter = openmc.CellFilter(cell_2)
outer_surface_spectra_tally = openmc.Tally(name='outer_surface_spectra_tally')
outer_surface_spectra_tally.scores = ['current']
outer_surface_spectra_tally.filters = [surface_filter, energy_filter]
outer_surface_spectra_tally.id = 12
my_tallies.append(outer_surface_spectra_tally)

# creates and exports the model to an xml file. When using openmc.lib this
# export is needed as we don't use the normal model.run() method.
model = openmc.model.Model(my_geometry, my_materials, my_settings, my_tallies)
model.export_to_xml()

fig, axs = plt.subplots(my_settings.batches, 2, sharex=True, sharey=True)

# We run the model in analog mode batch by batch. Each time we plot the spectra
# tally result. The spectra tally will gradually to get better with each batch
# as the batches combine to continually improve the result.

# this context manager helps close openmc lib when the code indent closes
with openmc.lib.run_in_memory():

    # gets a live pointer to the tally, this updates as the tally is accumulated
    spectra_tally = openmc.lib.tallies[outer_surface_spectra_tally.id]
    
    # simulation_init is needed prior to iter_batches
    openmc.lib.simulation_init()

    # loops through each batch getting the latest tally result and plotting it
    for counter, batch in enumerate(openmc.lib.iter_batches()):

        axs[counter][0].step(energy_filter.values[:-1], spectra_tally.mean.flatten())
        axs[counter][0].set_title(f'Batch {counter+1}')
        axs[counter][0].set_yscale('log')
        axs[counter][0].set_xscale('log')

    openmc.lib.simulation_finalize()


# originally we had 2000 particles per batch
# on my computer the analog simulation ran with 12470 particles/second
# and the weight windows simulation that comes next runs with 87 particles/second
# therefore we are going to decrease the settings.particles so that both simulations
# get the same amount of compute time
model.settings.particles = int(model.settings.particles*(87/12470))
model.export_to_xml()
with openmc.lib.run_in_memory():

    # gets a live pointer to the mesh tally that we use to generate the 
    ww_tally = openmc.lib.tallies[flux_tally_for_ww.id]
    # generates a weight window from the tally (which is currently empty)
    wws = openmc.lib.WeightWindows.from_tally(ww_tally)
    
    # gets a live pointer to the spectra tally that we will plot with each batch
    spectra_tally = openmc.lib.tallies[outer_surface_spectra_tally.id]

    # turn the weight windows on
    openmc.lib.settings.weight_windows_on = True

    openmc.lib.simulation_init()
    for counter, batch in enumerate(openmc.lib.iter_batches()):

        # updates the weight window with the latest mesh tally flux results 
        wws.update_magic(ww_tally)

        # plots the spectra tally for the batch
        axs[counter][1].step(energy_filter.values[:-1], spectra_tally.mean.flatten())
        axs[counter][1].set_title(f'Batch {counter+1}')
        axs[counter][1].set_yscale('log')
        axs[counter][1].set_xscale('log')

    openmc.lib.simulation_finalize()

# sets titles, labels and saves the plot
axs[1][0].set_title('Analog simulation')
axs[2][0].set_title('Iterative weight windows simulation')
axs[0][4].set_xlabel(f'Energy [eV]')
axs[0][4].set_xlabel(f'Energy [eV]')
plt.savefig('ww.png', bbox_inches="tight")
plt.show()
