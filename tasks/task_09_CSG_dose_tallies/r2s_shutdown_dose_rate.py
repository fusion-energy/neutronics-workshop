# makes a sphere of Silver and irradiates it with a 14MeV neutron source.
# The activated material emits gammas and these are transported and tallied
# on a mesh tally. The resulting decay gamma flux is plotted as a series of
# images so that the variation over time can be observed. Note that silver
# activation results in Ag110 which has a half life of 24 seconds. The
# irradiation and decay timescales are set so that the buildup and decay can be
# observed

import openmc

sphere_surf_1 = openmc.Sphere(r=20, boundary_type="vacuum")
sphere_surf_2 = openmc.Sphere(r=5, x0=10)

sphere_region_1 = -sphere_surf_1 & +sphere_surf_2  # void space
sphere_region_2 = -sphere_surf_2

sphere_cell_1 = openmc.Cell(region=sphere_region_1)

sphere_cell_2 = openmc.Cell(region=sphere_region_2)

mat_silver = openmc.Material()
mat_silver.add_element("Ag", 1.0)
mat_silver.set_density("g/cm3", 10.49)
mat_silver.depletable = True
mat_silver.volume = 523.6
sphere_cell_2.fill = mat_silver

universe = openmc.Universe(cells=[sphere_cell_1, sphere_cell_2])
my_geometry = openmc.Geometry(universe)

my_materials = openmc.Materials([mat_silver])

my_neutron_settings = openmc.Settings()
my_neutron_settings.batches = 10
my_neutron_settings.particles = 500000
my_neutron_settings.run_mode = "fixed source"

source = openmc.Source()
source.space = openmc.stats.Point((0, 0, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])
my_neutron_settings.source = source

my_photon_settings = openmc.Settings()
my_photon_settings.batches = 10
my_photon_settings.particles = 50000
my_photon_settings.run_mode = "fixed source"

# Create mesh which will be used for tally
mesh = openmc.RegularMesh().from_domain(
    my_geometry,  # the corners of the mesh are being set automatically to surround the geometry
    dimension=[200, 200, 1],
)

mesh_filter = openmc.MeshFilter(mesh)

my_photon_tallies = openmc.Tallies()
# Create mesh filter for tally

# Create flux mesh tally to score flux
mesh_tally_1 = openmc.Tally(name="photon_flux_on_mesh")
particle_filter = openmc.ParticleFilter(['photon'])
mesh_tally_1.filters = [mesh_filter, particle_filter]
mesh_tally_1.scores = ["flux"]
my_photon_tallies.append(mesh_tally_1)

r2s_model = openmc.R2SModel(
    geometry=my_geometry,
    materials=my_materials,
    settings=my_neutron_settings,
)

r2s_model.timesteps = [200] * 100  # neutron irradiation timesteps
r2s_model.source_rates = [1e18] * 20 + [0] * 80  # 6 full power and 6 zero power neutron irradiation source rates
r2s_model.photon_settings = my_photon_settings
r2s_model.photon_tallies = my_photon_tallies
# runs photon transport on every timestep but could change to  after [6, 7, 8, 9, 10, 11] which would be ever step after the neutron source goes to 0
r2s_model.photon_timesteps = list(range(100))


statepoints = r2s_model.execute_run()
print([str(s) for s in statepoints])

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np

plotted_part_of_tallys=[]

for i, statepoint_file in enumerate(statepoints):
    with openmc.StatePoint(statepoint_file) as statepoint:
        my_tally = statepoint.get_tally(name="photon_flux_on_mesh")
        plotted_part_of_tally = my_tally.mean.flatten()
        print(sum(plotted_part_of_tally))
        plotted_part_of_tallys.append(plotted_part_of_tally)
        reshaped_tally = plotted_part_of_tally.reshape(mesh.dimension, order="F")
        tally_aligned = reshaped_tally.transpose(2, 0, 1) # specific transpose for slicing z axis
        image_slice = tally_aligned[int(mesh.dimension[2] / 2)] # mid mesh slice
        left = mesh.lower_left[2]  # 2 as z axis slice
        right = mesh.upper_right[2]
        bottom = mesh.lower_left[2]
        top = mesh.upper_right[2]
        norm = LogNorm(vmin=1e-4, vmax=1e1)
        mpl_image_slice = np.rot90(image_slice)
        plt.cla()
        plt.clf()
        plt.axes(title=f"Photon Flux from Activated Ag, timestep {i} = {sum(r2s_model.timesteps[:i])}s", xlabel='X [cm]', ylabel='y [cm]')
        plt.imshow(X=mpl_image_slice, extent=(left, right, bottom, top), norm=norm)
        plt.contour(mpl_image_slice, levels=[1e1])
        plt.colorbar(label='flux')
        plt.savefig(f'photon_flux_map{str(i).zfill(3)}.png')

plt.cla()
plt.clf()
plt.plot(plotted_part_of_tallys)
plt.savefig(f'flux_vs_time.png')
import os
os.system('convert -delay 20 -loop 0 photon_*.png  r2s.gif')
