# %% [markdown]
# ---
# title: FW CADIS Weight Windows
# ---

# %% [markdown]
# Creating and utilizing a weight window to accelerate deep shielding simulations
#
# This example simulates a shield room / bunker with corridor entrance and a neutron source in the center of the room. This example implements a FW-CADIS of weight window generation. 
#
# In this tutorial we shall focus on generating a weight window to accelerate the simulation of particles through a shield.
#
# Weight Windows are found using the FW-CADIS method and used to accelerate the simulation.
#
# The variance reduction method used for this simulation is well documented in the OpenMC documentation
# https://docs.openmc.org/en/stable/usersguide/variance_reduction.html

# %% [markdown]
# First we import ```openmc``` and other packages needed for the example and configure the nuclear data path

# %%
import copy

from matplotlib import pyplot as plt
from matplotlib.colors import LogNorm  # used for plotting log scale graphs

import openmc
from pathlib import Path
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# We create a couple of materials for the simulation

# %%
mat_air = openmc.Material(name="air")
mat_air.add_element("N", 0.784431)
mat_air.add_element("O", 0.210748)
mat_air.add_element("Ar", 0.0046)
mat_air.set_density("g/cc", 0.001205)

mat_concrete = openmc.Material(name='concrete')
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

materials_continuous_xs = openmc.Materials([mat_air, mat_concrete])

# %% [markdown]
# Now we define and plot the geometry. This geometry is defined by parameters for every width and height. The parameters input into the geometry in a stacked manner so they can easily be adjusted to change the geometry without creating overlapping cells.

# %%
width_a = 100
width_b = 100
width_c = 500
width_d = 100
width_e = 100
width_f = 100
width_g = 100

depth_a = 100
depth_b = 100
depth_c = 700
depth_d = 600
depth_e = 100
depth_f = 100

height_j = 100
height_k = 500
height_l = 100

xplane_0 = openmc.XPlane(x0=0, boundary_type="vacuum")
xplane_1 = openmc.XPlane(x0=xplane_0.x0 + width_a)
xplane_2 = openmc.XPlane(x0=xplane_1.x0 + width_b)
xplane_3 = openmc.XPlane(x0=xplane_2.x0 + width_c)
xplane_4 = openmc.XPlane(x0=xplane_3.x0 + width_d)
xplane_5 = openmc.XPlane(x0=xplane_4.x0 + width_e)
xplane_6 = openmc.XPlane(x0=xplane_5.x0 + width_f)
xplane_7 = openmc.XPlane(x0=xplane_6.x0 + width_g, boundary_type="vacuum")

yplane_0 = openmc.YPlane(y0=0, boundary_type="vacuum")
yplane_1 = openmc.YPlane(y0=yplane_0.y0 + depth_a)
yplane_2 = openmc.YPlane(y0=yplane_1.y0 + depth_b)
yplane_3 = openmc.YPlane(y0=yplane_2.y0 + depth_c)
yplane_4 = openmc.YPlane(y0=yplane_3.y0 + depth_d)
yplane_5 = openmc.YPlane(y0=yplane_4.y0 + depth_e)
yplane_6 = openmc.YPlane(y0=yplane_5.y0 + depth_f, boundary_type="vacuum")

zplane_1 = openmc.ZPlane(z0=0, boundary_type="vacuum")
zplane_2 = openmc.ZPlane(z0=zplane_1.z0 + height_j)
zplane_3 = openmc.ZPlane(z0=zplane_2.z0 + height_k)
zplane_4 = openmc.ZPlane(z0=zplane_3.z0 + height_l, boundary_type="vacuum")

outside_left_region = +xplane_0 & -xplane_1 & +yplane_1 & -yplane_5 & +zplane_1 & -zplane_4
wall_left_region = +xplane_1 & -xplane_2 & +yplane_2 & -yplane_4 & +zplane_2 & -zplane_3
wall_right_region = +xplane_5 & -xplane_6 & +yplane_2 & -yplane_5 & +zplane_2 & -zplane_3
wall_top_region = +xplane_1 & -xplane_4 & +yplane_4 & -yplane_5 & +zplane_2 & -zplane_3
outside_top_region = +xplane_0 & -xplane_7 & +yplane_5 & -yplane_6 & +zplane_1 & -zplane_4
wall_bottom_region = +xplane_1 & -xplane_6 & +yplane_1 & -yplane_2 & +zplane_2 & -zplane_3
outside_bottom_region = +xplane_0 & -xplane_7 & +yplane_0 & -yplane_1 & +zplane_1 & -zplane_4
wall_middle_region = +xplane_3 & -xplane_4 & +yplane_3 & -yplane_4 & +zplane_2 & -zplane_3
outside_right_region = +xplane_6 & -xplane_7 & +yplane_1 & -yplane_5 & +zplane_1 & -zplane_4

room_region = +xplane_2 & -xplane_3 & +yplane_2 & -yplane_4 & +zplane_2 & -zplane_3
gap_region = +xplane_3 & -xplane_4 & +yplane_2 & -yplane_3 & +zplane_2 & -zplane_3
corridor_region = +xplane_4 & -xplane_5 & +yplane_2 & -yplane_5 & +zplane_2 & -zplane_3

roof_region = +xplane_1 & -xplane_6 & +yplane_1 & -yplane_5 & +zplane_1 & -zplane_2
floor_region = +xplane_1 & -xplane_6 & +yplane_1 & -yplane_5 & +zplane_3 & -zplane_4

outside_left_cell = openmc.Cell(region=outside_left_region, fill=mat_air)
outside_right_cell = openmc.Cell(region=outside_right_region, fill=mat_air)
outside_top_cell = openmc.Cell(region=outside_top_region, fill=mat_air)
outside_bottom_cell = openmc.Cell(region=outside_bottom_region, fill=mat_air)
wall_left_cell = openmc.Cell(region=wall_left_region, fill=mat_concrete)
wall_right_cell = openmc.Cell(region=wall_right_region, fill=mat_concrete)
wall_top_cell = openmc.Cell(region=wall_top_region, fill=mat_concrete)
wall_bottom_cell = openmc.Cell(region=wall_bottom_region, fill=mat_concrete)
wall_middle_cell = openmc.Cell(region=wall_middle_region, fill=mat_concrete)
room_cell = openmc.Cell(region=room_region, fill=mat_air)
gap_cell = openmc.Cell(region=gap_region, fill=mat_air)
corridor_cell = openmc.Cell(region=corridor_region, fill=mat_air)

roof_cell = openmc.Cell(region=roof_region, fill=mat_concrete)
floor_cell = openmc.Cell(region=floor_region, fill=mat_concrete)

geometry = openmc.Geometry(
    [
        outside_bottom_cell,
        outside_top_cell,
        outside_left_cell,
        outside_right_cell,
        wall_left_cell,
        wall_right_cell,
        wall_top_cell,
        wall_bottom_cell,
        wall_middle_cell,
        room_cell,
        gap_cell,
        corridor_cell,
        roof_cell,
        floor_cell,
    ]
)

# %% [markdown]
# Now we plot the geometry and color by materials.

# %%
plot = geometry.plot(basis='xy',  color_by='material')
plot.figure.savefig('geometry_top_down_view.png', bbox_inches="tight")

# %% [markdown]
# Next we create a point source, this also uses the same geometry parameters to place in the center of the room regardless of the values of the parameters.

# %%
# location of the point source
source_x = width_a + width_b + width_c * 0.5
source_y = depth_a + depth_b + depth_c * 0.75
source_z = height_j + height_k * 0.5
space = openmc.stats.Point((source_x, source_y, source_z))

# all (100%) of source particles are 2.5MeV energy
source = openmc.IndependentSource(
    space=space,
    angle=openmc.stats.Isotropic(),
    energy=openmc.stats.Discrete([2.5e6], [1.0]),
    particle="neutron"
)

# %% [markdown]
# Make the settings for our continuous energy MC solver

# %%
# Create settings
settings = openmc.Settings()
settings.run_mode = "fixed source"
settings.source = source
settings.particles = 80
settings.batches = 100
# Normally in fixed source problems we don't use inactivie batches.
# However when using Random Ray we do need to use inactive batches
# More info here https://docs.openmc.org/en/stable/usersguide/random_ray.html#batches
settings.inactive = 50

ce_model = openmc.Model(geometry, materials_continuous_xs, settings)

# %% [markdown]
# At this point, we have a valid continuous energy Monte Carlo model!
#
# # Convert to Multigroup and Random Ray
#
# We begin by making a clone of our original continuous energy deck, and then convert it to multigroup.
#
# This step will automatically compute material-wise multigroup cross sections for us by running a continous energy OpenMC simulation internally.

# %%
rr_model = copy.deepcopy(ce_model)
rr_model.convert_to_multigroup(
    # I tend to use "stochastic_slab" method here.
    # Using the "material_wise" method is more accurate but slower
    # In problems where one needs weight windows to solve we don't really want
    # the calculation of weight windows to be slow.
    # In extreme cases the "material_wise" method could require its own weight windows to solve.
    # The "stochastic_slab" method is much faster and works well for most problems.
    # more details here https://docs.openmc.org/en/latest/usersguide/random_ray.html#the-easy-way
    method="stochastic_slab", 
    overwrite_mgxs_library=True,  # overrights the 
    nparticles=2000 # this is the default but can be adjusted upward to improve the fidelity of the generated cross section library
)

# %% [markdown]
# We now have a valid multigroup Monte Carlo input deck, complete with a "mgxs.h5" multigroup cross section library file. Next, we convert the model to use random ray instead of multigroup monte carlo.
#
# Random ray is needed for use with the FW-CADIS algorithm (which requires global adjoint flux information that the random ray solver generates).
#
# The below function will analyze the geometry and initialize the random ray solver with reasonable parameters.
#
# Users are free to tweak these parameters to improve the performance of the random ray solver, but the defaults are likely sufficient for weight window generation purposes for most cases.

# %%
rr_model.convert_to_random_ray()

# %% [markdown]
# # Create a Mesh for: Tallies / Weight Windows / Random Ray Source Region Subdivision

# %% [markdown]
# Now we setup a mesh that will be used in three ways:
# 1. For a mesh flux tally for viewing results
# 2. For subdividing the random ray source regions into smaller cells
# 3. For computing weight window parameters on

# %%
mesh = openmc.RegularMesh().from_domain(geometry)
mesh.dimension = (100, 100, 1)
mesh.id = 1

# 1. Make a flux tally for viewing the results of the simulation
mesh_filter = openmc.MeshFilter(mesh)
flux_tally = openmc.Tally(name="flux tally")
flux_tally.filters = [mesh_filter]
flux_tally.scores = ["flux"]
flux_tally.id = 42  # we set the ID because we need to access this later
tallies = openmc.Tallies([flux_tally])

# 2. Subdivide random ray source regions
rr_model.settings.random_ray['source_region_meshes'] = [(mesh, [rr_model.geometry.root_universe])]

# Attach the tally to the random ray model so that BOTH the forward solve
# and the adjoint solve record it. The forward solve is saved to
# statepoint.forward.<batch>.h5, letting us compare both fluxes below.
rr_model.tallies = tallies

# %% [markdown]
# Not required for WW generation, but one can run the regular (forward flux) random ray solver to make sure things are working before we attempt to generate weight windows with the command ```random_ray_wwg_statepoint = rr_model.run()```

# %% [markdown]
# # Use FW-CADIS to Generate Weight Windows

# %% [markdown]
# Now add the weight window generator

# %%
rr_model.settings.weight_window_generators = openmc.WeightWindowGenerator(
    method='fw_cadis',
    mesh=mesh,
)

# %% [markdown]
# Then run the random ray model. This will automatically run a normal forward flux solve followed by a subsequent adjoint solve that is used to compute the weight windows. Our outputted flux tally data will be in terms of adjoint fluxes.

# %%
random_ray_wwg_statepoint = rr_model.run()

# %% [markdown]
# # Compare the Forward and Adjoint Flux
#
# The FW-CADIS `run()` above actually performed **two** solves back to back:
#
# 1. a **forward** solve, giving the physical neutron flux streaming out from the source, and
# 2. an **adjoint** solve, giving the *importance* function, i.e. how much a neutron at each
#    location matters for getting good statistics everywhere in the problem.
#
# The adjoint source used in step 2 is built directly from the forward flux of step 1. That
# coupling is what the **FW** (forward-weighted) in FW-CADIS refers to, and it is why the random
# ray solver runs a forward pass before the adjoint pass. The weight windows we use later are
# derived from this adjoint flux.
#
# The forward solve writes `statepoint.forward.<batch>.h5` (and `tallies.forward.out`) while the
# adjoint solve keeps the usual `statepoint.<batch>.h5`, so a single run gives us both fluxes to
# load and compare.
#
# Plotting them side by side is the clearest way to build intuition for why variance reduction
# is needed and what it does:
#
# * The **forward flux** is bright near the source and falls by many orders of magnitude through
#   each concrete wall. This is exactly why an unbiased (analog) simulation starves the
#   deep-shield and corridor regions of particles, and why the *weight windows off* error map
#   further down blows up in those regions.
# * The **adjoint flux** is elevated in those same hard-to-reach regions, because that is where a
#   neutron is most valuable for achieving uniform global statistics. The weight windows
#   (roughly proportional to 1/adjoint) then encourage particle splitting into exactly those
#   regions.
#
# Notice the two fields live on very different scales, so each panel uses its own colour bar.

# %%
# The forward solve statepoint is named with a 'forward' infix and lives at the final batch.
forward_statepoint = f'statepoint.forward.{rr_model.settings.batches}.h5'


def get_mesh_flux(statepoint_file):
    with openmc.StatePoint(statepoint_file) as sp:
        tally = sp.get_tally(name='flux tally')
    return tally.get_reshaped_data(value='mean', expand_dims=True).squeeze()


forward_flux = get_mesh_flux(forward_statepoint)
adjoint_flux = get_mesh_flux(random_ray_wwg_statepoint)  # the adjoint solve statepoint

mesh_extent = mesh.bounding_box.extent['xy']

fig, (ax_fwd, ax_adj) = plt.subplots(ncols=2, figsize=(12, 5))

for ax, data, title in [
    (ax_fwd, forward_flux, 'Forward flux (where neutrons actually go)'),
    (ax_adj, adjoint_flux, 'Adjoint flux (neutron importance)'),
]:
    im = ax.imshow(
        data.T,
        origin='lower',
        extent=mesh_extent,
        norm=LogNorm(),
    )
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    # overlay the geometry outline so the walls, room and corridor are visible
    ce_model.plot(
        outline='only',
        extent=ce_model.bounding_box.extent['xy'],
        axes=ax,
        pixels=10_000_000,  # avoids rounded corners on outline
        color_by='material',
    )
    ax.set_title(title)

fig.suptitle('FW-CADIS: forward flux vs adjoint (importance) flux from a single run')
plt.tight_layout()
plt.savefig('forward_vs_adjoint_flux.png', bbox_inches='tight')

# %% [markdown]
# Now we should see a weight_windows.h5 file has been created

# %%
print(f'weight_windows.h5 is {Path("weight_windows.h5").stat().st_size / 1e6:.1f} MB')

# %% [markdown]
# Plot the resulting weight windows with the geometry overlay

# %%
weight_windows = openmc.hdf5_to_wws('weight_windows.h5')

ax1 = plt.subplot()
im = ax1.imshow(
    weight_windows[0].lower_ww_bounds.squeeze().T,
    origin='lower',
    extent=mesh.bounding_box.extent['xy'],
    norm=LogNorm()
)

plt.colorbar(im, ax=ax1)

ax1 = ce_model.plot(
    outline='only',
    extent=ce_model.bounding_box.extent['xy'],
    axes=ax1,  # Use the same axis as ax1\n",
    pixels=10_000_000,  #avoids rounded corners on outline
    color_by='material',
)
ax1.set_title("lower_ww_bounds")

# %% [markdown]
# # Use Weight Windows to Accelerate Original Continuous Energy Monte Carlo Solve
#
# Now, to utilize the weight windows, we will add the weight windows into our settings object and configure things for continuous energy MC.

# %%
settings = openmc.Settings()

settings.weight_window_checkpoints = {'collision': True, 'surface': True}
settings.survival_biasing = False
settings.weight_windows = weight_windows
settings.particles = 40000
settings.batches = 12
settings.source = source
settings.run_mode = "fixed source"

tallies = openmc.Tallies([flux_tally])

# %% [markdown]
# First, to demonstrate the impacts of the weight windows, let's run OpenMC without using them and plot the relative error in the fluxes. Given that the shield is optically thick, many regions will receive no tallies and/or have very high errors.

# %%
settings.weight_windows_on = False # Turn off weight windows for now
simulation_using_ww_off = openmc.Model(geometry, materials_continuous_xs, settings, tallies)


# %% [markdown]
# Creating a plotting function that we will reuse to plot results from the different simulations

# %%
def run_and_plot(model: openmc.Model, image_filename: str) -> openmc.StatePoint:

    for f in Path('.').glob('s*.h5'):
        f.unlink(missing_ok=True)
    sp_filename = model.run()

    with openmc.StatePoint(sp_filename) as sp:
        flux_tally = sp.get_tally(name="flux tally")

    mesh_extent = mesh.bounding_box.extent['xy']

    # create a plot of the mean flux values
    flux_mean = flux_tally.get_reshaped_data(value='mean', expand_dims=True).squeeze()

    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(10, 5))
    ax1.imshow(
        flux_mean.T,
        origin="lower",
        extent=mesh_extent,
        norm=LogNorm(),
    )

    ax1 = model.plot(
        outline='only',
        extent=model.bounding_box.extent['xz'],
        axes=ax1,  # Use the same axis as ax1\n",
        pixels=10_000_000,  #avoids rounded corners on outline
        color_by='material',
    )
    ax1.set_title("Flux Mean")

    # create a plot of the flux relative error
    flux_std_dev = flux_tally.get_reshaped_data(value='std_dev', expand_dims=True).squeeze()
    ax2.imshow(
        flux_std_dev.T,
        origin="lower",
        extent=mesh_extent,
        norm=LogNorm(),
    )

    ax2 = model.plot(
        outline='only',
        extent=model.bounding_box.extent['xz'],
        axes=ax2,  # Use the same axis as ax2\n",
        pixels=10_000_000,  #avoids rounded corners on outline
        color_by='material',
    )
    ax2.set_title("Flux Std. Dev.")

    plt.savefig(image_filename)
    return sp


# %%
run_and_plot(simulation_using_ww_off, "no_fw_cadis.png")

# %% [markdown]
# As expected, the error spikes quickly once entering the shield, with most areas deep into the shield receiving no tallies at all.

# %% [markdown]
# On this computer the simulation speed was 32553 particles per second for the simulation without weight windows and 6379 particles per second when weight windows were turned on. The particle splitting means individual particles take longer to simulate as the continue to be transported more.
#
# So the simulation with weight window took longer to run and consumed more compute, to make this a fair comparison we should chage the particles per batch or batches so that the simulations both have the same compute.
#
# Next, let's run OpenMC with weight windows enabled, and see the impact.

# %%
settings.weight_windows_on = True # Now, turn on the FW-CADIS generated weight windows
settings.batches = 2
simulation_using_ww_on = openmc.Model(geometry, materials_continuous_xs, settings, tallies)

# %%
run_and_plot(simulation_using_ww_on, "fw_cadis.png")
