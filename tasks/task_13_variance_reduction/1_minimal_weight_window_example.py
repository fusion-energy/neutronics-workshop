import openmc
import matplotlib.pyplot as plt

# MATERIALS

# creates two materials, one is a neutron multiplier (lead) and the other a tritium breeder (lithium)
mats = openmc.Materials()
 
breeder_material = openmc.Material(name="breeder") 
breeder_material.add_element('Li', 1, percent_type='ao')
breeder_material.set_density('g/cm3', 2.0)

multiplier_material = openmc.Material(name="multiplier") 
multiplier_material.add_element('Pb', 1, percent_type='ao')
multiplier_material.set_density('g/cm3', 11.0)

mats = [breeder_material, multiplier_material]



# GEOMETRY

# surfaces
sph1 = openmc.Sphere(r=50)
sph2 = openmc.Sphere(r=90, boundary_type='vacuum')
plane1 = openmc.XPlane(20)

# cells
breeder_cell = openmc.Cell(region=+sph1 & -sph2 & -plane1)
breeder_cell.fill = breeder_material

multiplier_cell = openmc.Cell(region=+sph1 & -sph2 & +plane1)
multiplier_cell.fill = multiplier_material

inner_vacuum_cell = openmc.Cell(region=-sph1)

universe = openmc.Universe(cells=[inner_vacuum_cell, breeder_cell, multiplier_cell])

geom = openmc.Geometry(universe)

# Create mesh which will be used for tally and weight window
my_mesh = openmc.RegularMesh()
mesh_height = 4   # number of cells in the X and Z dimensions
mesh_width = mesh_height
my_mesh.dimension = [mesh_width, 1, mesh_height] # only 1 cell in the Y dimension
my_mesh.lower_left = [-200, -200, -200]   # physical limits (corners) of the mesh
my_mesh.upper_right = [200, 200, 200]

# SETTINGS

# Instantiate a Settings object
sett = openmc.Settings()
sett.batches = 100
sett.inactive = 0
sett.particles = 50
sett.particle = "neutron"
sett.run_mode = 'fixed source'

lower_ww_bounds=[]
energy_bins = []
upper_ww_bounds=[]
for mesh_element in range(mesh_height * mesh_width):
    print(mesh_element)
    energy_bins.append(1.1)
    energy_bins.append(1e9)
    lower_ww_bounds.append(1)
    lower_ww_bounds.append(10)
    upper_ww_bounds.append(40)
    upper_ww_bounds.append(30)
    # lower_ww_bounds.append()

# docs on ww https://docs.openmc.org/en/latest/_modules/openmc/weight_windows.html?highlight=weight%20windows
ww = openmc.WeightWindows(
    mesh =my_mesh,
    lower_ww_bounds=lower_ww_bounds,
    energy_bins=energy_bins,
    upper_ww_bounds=upper_ww_bounds
)

sett.weight_windows = ww



# creates a 14MeV point source
source = openmc.Source()
source.space = openmc.stats.Point((0, 0, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])
sett.source = source






tallies = openmc.Tallies()
# Create mesh filter for tally
mesh_filter = openmc.MeshFilter(my_mesh)
mesh_tally = openmc.Tally(name='tallies_on_mesh')
mesh_tally.filters = [mesh_filter]
mesh_tally.scores = ['flux', 'absorption', '(n,2n)']  # change flux to absorption
tallies.append(mesh_tally)

# combines the geometry, materials, settings and tallies to create a neutronics model
model = openmc.model.Model(geom, mats, sett, tallies)

# plt.show(universe.plot(width=(180, 180), basis='xz'))

# # deletes old files
# !rm summary.h5
# !rm statepoint.*.h5

# runs the simulation
output_filename = model.run()

# open the results file
results = openmc.StatePoint(output_filename)

# access the flux tally
my_tally = results.get_tally(scores=['flux'])
my_slice = my_tally.get_slice(scores=['flux'])
my_slice.mean.shape = (mesh_width, mesh_height)

fig = plt.subplot()

# when plotting the 2d data, added the extent is required.
# otherwise the plot uses the index of the 2d data arrays
# as the x y axis
fig.imshow(my_slice.mean, extent=[-200,200,-200,200], vmin=1e-9, vmax=1)

plt.show()

# notice that neutrons are produced and emitted isotropically from a point source.
# There is a slight increase in flux within the neutron multiplier.
