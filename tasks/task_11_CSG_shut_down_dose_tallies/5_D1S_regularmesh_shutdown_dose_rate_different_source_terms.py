# %% [markdown]
# ---
# title: Shutdown dose rate D1S method different sources (DD+DT)
# ---

# %% [markdown]
# This script simulates D1S method of shut down dose rate on a simple CSG model with one aluminum sphere and one iron sphere.
#
# This adds the additional complexity of mixed neutron source terms. In this case we simulate two pulses of neutrons from DD fusion reactions which have energy of 2.5MeV and then a pulse of neutrons from a DT fusion reaction which have neutrons of 14MeV.
#
# This need to simulate the activation after different neutron source terms is a common need in fusion power plants which typically plan to start operations without using tritium and gradually work up to full DT operation.
#
# You should notice in this example that we have to perform two transport simulating (one for DD and on for DT) then accounting for the combined activation is done by synchronizing pulse schedule so that the decay can be combined from both roots.
#
# More details on D1S method in the OpenMC documentation
# https://docs.openmc.org/en/stable/usersguide/decay_sources.html#direct-1-step-d1s-calculations

# %%
import math
from pathlib import Path

import openmc

import numpy as np
import matplotlib.pyplot as plt

from matplotlib.colors import LogNorm
from openmc.deplete import d1s
from openmc.data.data import half_life

# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'
# the chain file was downloaded with
# pip install openmc_data
# download_endf_chain -r b8.0
openmc.config['chain_file'] = Path.home() / 'nuclear_data' / 'chain-endf-b8.0.xml'

# %% [markdown]
# Make the materials.
#
# Note that they don't need the volume setting and don't need to be made depletable. The R2S shutdown dose rate workflow requires both of these to be set.

# %%
# We make a iron material which should produce a few activation products
mat_iron = openmc.Material()
mat_iron.add_nuclide("Al27", 1.0)
mat_iron.set_density("g/cm3", 8.0)
mat_iron.volume = 2* (4/3) * math.pi**3

# We make a Al material which should produce a few different activation products
mat_aluminum = openmc.Material()
mat_aluminum.add_nuclide("Fe56", 1.0)
mat_aluminum.set_density("g/cm3", 2.7)
mat_aluminum.volume = 3* (4/3) * math.pi**3

# %% [markdown]
# Now we make a simple geometry, a cube with two sphere inside.
#
# The sphere have different materials and the cube is the edge of the simulation space.

# %%
sphere_surf_1 = openmc.Sphere(r=2, y0=10, x0=-10)
sphere_region_1 = -sphere_surf_1
sphere_cell_1 = openmc.Cell(region=sphere_region_1, fill=mat_iron)

sphere_surf_2 = openmc.Sphere(r=3, y0=-10, x0=10)
sphere_region_2 = -sphere_surf_2
sphere_cell_2 = openmc.Cell(region=sphere_region_2, fill=mat_aluminum)

xplane_surf_1 = openmc.XPlane(x0=-20, boundary_type='vacuum')
xplane_surf_2 = openmc.XPlane(x0=20, boundary_type='vacuum')
yplane_surf_1 = openmc.YPlane(y0=-20, boundary_type='vacuum')
yplane_surf_2 = openmc.YPlane(y0=20, boundary_type='vacuum')
zplane_surf_1 = openmc.ZPlane(z0=-20, boundary_type='vacuum')
zplane_surf_2 = openmc.ZPlane(z0=20, boundary_type='vacuum')
sphere_region_3 = +xplane_surf_1 & -xplane_surf_2 & +yplane_surf_1 & -yplane_surf_2  & +zplane_surf_1 & -zplane_surf_2 & +sphere_surf_1 & +sphere_surf_2  # void space
sphere_cell_3 = openmc.Cell(region=sphere_region_3)

my_geometry = openmc.Geometry([sphere_cell_1, sphere_cell_2, sphere_cell_3])

my_materials = openmc.Materials([mat_iron, mat_aluminum])

# %% [markdown]
# Next we make a minimal source term.
#
# A 14MeV neutron source that activates material, located in the center of the geometry

# %%
my_source_dd = openmc.IndependentSource(
    space=openmc.stats.Point((0, 0, 0)),
    angle=openmc.stats.Isotropic(),
    energy=openmc.stats.Discrete([2.5e6], [1]),
    particle="neutron"
)

my_source_dt = openmc.IndependentSource(
    space=openmc.stats.Point((0, 0, 0)),
    angle=openmc.stats.Isotropic(),
    energy=openmc.stats.Discrete([14.06e6], [1]),
    particle="neutron"
)

# %% [markdown]
# Then we make the simulation settings, note that photon_transport is enabled and a D1S specific setting ```use_decay_photons``` is used

# %%
# settings for the DT neutron simulation with decay photons
settings_dd = openmc.Settings()
settings_dd.run_mode = "fixed source"
settings_dd.particles = 1000000
settings_dd.batches = 10
settings_dd.source = my_source_dd
settings_dd.photon_transport = True

# D1S specific setting
settings_dd.use_decay_photons = True

# settings for the DD neutron simulation with decay photons
settings_dt = openmc.Settings()
settings_dt.run_mode = "fixed source"
settings_dt.particles = 1000000
settings_dt.batches = 10
settings_dt.source = my_source_dt
settings_dt.photon_transport = True

# D1S specific setting
settings_dt.use_decay_photons = True

# %% [markdown]
# We now make the photon dose tally which uses a regular mesh so that we can make a dose map

# %%
# creates a regular mesh that surrounds the geometry for the tally
mesh = openmc.RegularMesh().from_domain(
    my_geometry,
    dimension=[100, 100, 1],
    # 100 voxels in x and y axis directions and 1 voxel in z as we want a xy plot
)

# adding a dose tally on a regular mesh
# AP, PA, LLAT, RLAT, ROT, ISO are ICRP incident dose field directions, AP is front facing
energies, pSv_cm2 = openmc.data.dose_coefficients(particle="photon", geometry="AP")
dose_filter = openmc.EnergyFunctionFilter(
    energies, pSv_cm2, interpolation="cubic"  # interpolation method recommended by ICRP
)
particle_filter = openmc.ParticleFilter(["photon"])
mesh_filter = openmc.MeshFilter(mesh)
dose_tally = openmc.Tally()
dose_tally.filters = [particle_filter, mesh_filter, dose_filter]
dose_tally.scores = ["flux"]
dose_tally.name = "photon_dose_on_mesh"

tallies = openmc.Tallies([dose_tally])

# %% [markdown]
# Now we make the model and importantly for D1S we prepare the tallies
#
# this run runs the neutron and decay photon steps 

# %%
model_dd = openmc.Model(my_geometry, my_materials, settings_dd, tallies)
model_dt = openmc.Model(my_geometry, my_materials, settings_dt, tallies)

# this adds ParentNuclideFilter to each tally, which the D1S method requires
d1s.prepare_tallies(model=model_dd)
d1s.prepare_tallies(model=model_dt)

output_path_dd = model_dd.run(cwd='dd_results')
output_path_dt = model_dt.run(cwd='dt_results')

# %% [markdown]
# Now we read in the tally from the simulation output file

# %%
# Get tally from DD simulation statepoint
with openmc.StatePoint(output_path_dd) as sp:
    dose_tally_from_sp_dd = sp.get_tally(name='photon_dose_on_mesh')

# Get tally from DT simulation statepoint
with openmc.StatePoint(output_path_dt) as sp:
    dose_tally_from_sp_dt = sp.get_tally(name='photon_dose_on_mesh')

# %% [markdown]
# Making the time steps and source rates together ensures the time steps for the DD and DT pulses are aligned.
#
# This is important to do as, later we need to combine the decay dose from DD pulses and DT pulses for the same point in time.

# %%
timesteps_and_source_rates = [
    (1, 1e18, 0),  # pulse of DD neutrons
    (60*20, 0, 0),  # 20 minutes
    (60*20, 0, 0),  # 40 minutes
    (60*20, 0, 0),  # 60 minutes
    (60*20, 0, 0),  # 80 minutes
    (60*20, 0, 0),  # 100 minutes
    (1, 1e18, 0),  # pulse of DD neutrons
    (60*20, 0, 0),  # 20 minutes
    (60*20, 0, 0),  # 40 minutes
    (60*20, 0, 0),  # 60 minutes
    (60*20, 0, 0),  # 80 minutes
    (60*20, 0, 0),  # 100 minutes
    (1, 0, 1e19),  # larger pulse of DT neutrons
    (60*20, 0, 0),  # 20 minutes
    (60*20, 0, 0),  # 40 minutes
    (60*20, 0, 0),  # 60 minutes
    (60*20, 0, 0),  # 80 minutes
    (60*20, 0, 0),  # 100 minutes
]

timesteps = [item[0] for item in timesteps_and_source_rates]

source_rates_dd = [item[1] for item in timesteps_and_source_rates]
source_rates_dt = [item[2] for item in timesteps_and_source_rates]

# %% [markdown]
# This section defines the neutron pulse schedule time steps to take dose tally measurements.
#
# Also some D1S specific steps to get the time correction factors that we use to modify the tally result later.

# %%
# this gets all the unstable nuclides that can be produced during D1S
# both models have the same materials so this function will return the same radionuclides regarless of which model (model_dt or model dd) is passed in.
radionuclides = d1s.get_radionuclides(model_dt)

# Compute time correction factors based on irradiation schedule
time_factors_dd = d1s.time_correction_factors(
    nuclides=radionuclides,
    timesteps=timesteps,
    source_rates=source_rates_dd,
    timestep_units = 's'
)

# Compute time correction factors based on irradiation schedule
time_factors_dt = d1s.time_correction_factors(
    nuclides=radionuclides,
    timesteps=timesteps,
    source_rates=source_rates_dt,
    timestep_units = 's'
)

# %% [markdown]
# Note the use of ```apply_time_correction``` which is a D1S specific command

# %%
# multiplication by pico_to_milli converts from (pico) pSv to (milli) mSv
pico_to_milli = 1e-9

# divided by mesh element volume converts from mSv-cm3 to mSv
volume_normalization = mesh.volumes[0][0][0]

scaled_max_tally_value_all_timesteps = 0
corrected_tally_mean_for_each_timestep = []
for i_cool in range(1, len(timesteps)):  # missing the first timestep as it is the irradiation step

    # Apply time correction factors
    # this includes the source_rates which are in units of neutrons per second
    # dose_tally_from_sp is in units of pSv-cm3/source neutron
    # corrected tally is now in units of pSv-cm3/second
    corrected_tally_dd = d1s.apply_time_correction(
        tally=dose_tally_from_sp_dd,
        time_correction_factors=time_factors_dd,
        index=i_cool,
        sum_nuclides=True
    )
    corrected_tally_dt = d1s.apply_time_correction(
        tally=dose_tally_from_sp_dt,
        time_correction_factors=time_factors_dt,
        index=i_cool,
        sum_nuclides=True
    )

    # get a slice of mean values on the xy basis mid z axis
    corrected_tally_mean_dd = corrected_tally_dd.get_reshaped_data(value='mean', expand_dims=True).squeeze()
    
    # get a slice of mean values on the xy basis mid z axis
    corrected_tally_mean_dt = corrected_tally_dt.get_reshaped_data(value='mean', expand_dims=True).squeeze()
    

    corrected_tally_mean = corrected_tally_mean_dd + corrected_tally_mean_dt

    corrected_tally_mean_for_each_timestep.append(corrected_tally_mean)

    # # this section simply gets the maximum value of the mean tally across all time steps
    # # and uses this to set the max value of the color bar in the plots
    max_tally_value = max(corrected_tally_mean.flatten())
    scaled_max_tally_value = (max_tally_value * pico_to_milli) / volume_normalization

    # getting a max value to scale the color bar in the plots later
    if scaled_max_tally_value > scaled_max_tally_value_all_timesteps:
        scaled_max_tally_value_all_timesteps = scaled_max_tally_value

# %% [markdown]
# We then plot the tally for each time in the time steps of interest

# %%
for i_cool, corrected_tally_mean in enumerate(corrected_tally_mean_for_each_timestep, start=1):

    scaled_corrected_tally_mean = (corrected_tally_mean * pico_to_milli) / volume_normalization

    fig, ax1 = plt.subplots(figsize=(6, 4))

    # create a plot of the mean flux values
    plot_1 = ax1.imshow(
        X=scaled_corrected_tally_mean.T,
        origin="lower",
        extent=mesh.bounding_box.extent['xy'],
        norm=LogNorm(vmax=scaled_max_tally_value_all_timesteps, vmin=1e-6),
    )

    # add the geometry outline to the plot
    ax2 = my_geometry.plot(
        outline='only',
        extent=my_geometry.bounding_box.extent['xy'],
        axes=ax1,  # Use the same axis as ax1
        pixels=10_000_00,  #avoids rounded corners on outline
    )

    time_in_mins = round(sum(timesteps[1:i_cool])/(60),2)  # not including the first timestep 

    ax2.set_xlim(ax1.get_xlim())
    ax2.set_ylim(ax1.get_ylim())
    ax2.set_aspect(ax1.get_aspect())  # Match aspect ratio
    ax2.set_xlabel("X (cm)")
    ax2.set_ylabel("Y (cm)")
    cbar = plt.colorbar(plot_1, ax=ax1)
    cbar.set_label("Dose [milli Sv per second]")  # Label for the color bar
    
    max_dose_in_timestep = max(scaled_corrected_tally_mean.flatten())
    ax2.set_title(f"Dose Rate at time {time_in_mins} minutes after first irradiation\nMax dose rate: {max_dose_in_timestep:e} mSv/s")
    cbar.ax.hlines(max_dose_in_timestep, *cbar.ax.get_xlim(), color='red', linewidth=2, label='Max value')

    plt.show()
    plt.close()

# %% [markdown]
# One of the really nice aspects of the D1S workflow is the dose values are computed as a post process.
#
# This means we don't need to resimulate if we want to change the pulse scheduel

# %%
scaled_max_tally_values = []

for corrected_tally_mean in corrected_tally_mean_for_each_timestep:

    # this section simply gets the maximum value of the mean tally across all time steps
    scaled_max_tally_values.append((max(corrected_tally_mean.flatten())* pico_to_milli) / volume_normalization)

# %% [markdown]
# This plots the max dose rate at each time step for the 5 pulse decay irradiation.
#
# The plot has the shut down dose just after the irradiation and for a few times after each shot to show how the dose decreases.
#
# This plot shows shows a sharp drop in the dose rate after the shot, that is caused by some unstable isotopes decaying quickly are the irradiation stops
#
# After 5000 seconds the dose rate starts to level out, this is due to longer lived unstable isotopes that have now become the dominant contributor to the dose.
#
# We also notice that each shot causes the total dose rate to steadily climb. This is due to the build up of these longer lived unstable isotopes that have not had time to completely decay away before the next pulse of neutrons arrives.

# %%
plt.plot(np.cumsum(timesteps[1:]), scaled_max_tally_values)
plt.xlabel("Time (s)")
plt.yscale("log")
plt.ylabel("Max Dose Rate (mSv/s)")
plt.title("Max Dose Rate Over Time")
plt.grid()
plt.show()

# %% [markdown]
# This next code block loops through the tallies for each time step only this time we set ```sum_nuclides=False```.
#
# This allows us to get the individual contributions to the dose tally per nuclide.

# %%
scaled_max_tally_values_per_nuclide = {str(nuclide): [] for nuclide in radionuclides}

for i_cool in range(1, len(timesteps)):  # missing the first timestep as it is the irradiation step

    # Apply time correction factors
    # this includes the source_rates which are in units of neutrons per second
    # dose_tally_from_sp is in units of pSv-cm3/source neutron
    # corrected tally is now in units of pSv-cm3/second
    corrected_tally_dd = d1s.apply_time_correction(
        tally=dose_tally_from_sp_dd,
        time_correction_factors=time_factors_dd,
        index=i_cool,
        sum_nuclides=False
    )
    corrected_tally_dt = d1s.apply_time_correction(
        tally=dose_tally_from_sp_dt,
        time_correction_factors=time_factors_dt,
        index=i_cool,
        sum_nuclides=False
    )

    mean_values_per_nuclide_dt = corrected_tally_dt.mean.squeeze().reshape(len(radionuclides), -1)
    mean_values_per_nuclide_dd = corrected_tally_dd.mean.squeeze().reshape(len(radionuclides), -1)
    
    for i_nuclide, nuclide in enumerate(radionuclides):

        # this section simply gets the maximum value of the mean tally across all time steps
        max_value_for_nuclide_dd = (max(mean_values_per_nuclide_dd[i_nuclide]).flatten()* pico_to_milli) / volume_normalization
        max_value_for_nuclide_dt = (max(mean_values_per_nuclide_dt[i_nuclide]).flatten()* pico_to_milli) / volume_normalization

        combine_nuclide_number = float(max_value_for_nuclide_dd[0]) + float(max_value_for_nuclide_dt[0])

        scaled_max_tally_values_per_nuclide[str(nuclide)].append(combine_nuclide_number)

# %% [markdown]
# Plotting the dose contribution of the individual isotopes allows us to see that the build up of the longer lived isotopes and identify the main driver for the more long lived dose contribution.

# %%
plt.figure(figsize=(12, 8))
plt.plot(np.cumsum(timesteps[1:]), scaled_max_tally_values, label='total', linewidth=3)

for i, nuclide in enumerate(radionuclides):
    nuclide_str = str(nuclide)
    if sum(scaled_max_tally_values_per_nuclide[str(nuclide)]) > 2.0:
        plt.plot(
            np.cumsum(timesteps[1:]),
            scaled_max_tally_values_per_nuclide[nuclide_str],
            label=f"{nuclide_str} half-life={half_life(nuclide_str):.1e}s",
            linestyle='--',
        )
plt.legend()
plt.xlabel("Time (s)")
plt.yscale('log')
# plt.xscale('log')
plt.ylabel("Max Dose Rate (mSv/s)")
plt.title("Max Dose Rate Over Time")
plt.grid()
plt.show()

# %% [markdown]
# Task extension suggestion.
#
# You might have observed that the aluminum sphere doesn't get activated during the DD pules.
#
# This is visible in the heatmap plots which show aluminum (the larger sphere) not contributing to the dose map in the initial stages.
#
# This is because aluminum is not emitting gammas at these time steps.
#
# However the iron sphere is emitting gammas at these time steps.
#
# Take a look at the cross sections of the two nuclides (Fe56 and Al27) and see if you can identify threshold reactions that require more than 2.5MeV to trigger.
#
# Then see if these threshold reactions result in an unstable nuclide that is contributing to the dose only after the DT pulse.
