# %% [markdown]
# ---
# title: Simulating Displacements Per Atom (DPA)
# ---

# %% [markdown]
# Displacements per atom (DPA) is one measure of damage within materials exposed to neutron irradiation. Damage energy can be tallied in OpenMC with MT reaction number 444 and DPA can be estimated.
#
# In the case of DPA a neutronics code alone can't fully calculate the value as material science techniques are needed to account for the material and recombination effects. For example, after a displacement there is a chance that the atom relocates to it's original lattice position (recombination) and different atoms require different amounts of energy to [displace](https://fispact.ukaea.uk/wiki/Output_interpretation#DPA_and_KERMA). The DPA tally from neutronics is therefore only an estimate of the DPA.
#
# The MT 444 / damage energy tally is in units of eV per source particle. Therefore the result needs scaling by the source intensity (in neutrons per second), the irradiation duration (in seconds) and the number of atoms in the volume.

# %%
from IPython.display import IFrame
IFrame(src="https://www.youtube.com/embed/VLn59FSc4GA", width=560, height=340)

# %% [markdown]
# First import OpenMC and configure the nuclear data path

# %%
import openmc
from pathlib import Path
# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# This first stage sets up the geometry and materials for the simulation.

# %%
# MATERIALS

density_of_iron_in_g_per_cm3 = 7.75
mat_iron = openmc.Material()
mat_iron.set_density('g/cm3', density_of_iron_in_g_per_cm3)
mat_iron.add_element('Fe', 1.0, percent_type='wo')
mat_iron.id = 1 # the id is set so that is can be accessed later from the volume calculation
my_materials = openmc.Materials([mat_iron])


# GEOMETRY

# surfaces
outer_surface = openmc.Sphere(r=100, boundary_type='vacuum')

# cells
vessel_region = -outer_surface
vessel_cell = openmc.Cell(region=vessel_region)
vessel_cell.id = 1 # the id is set so that is can be accessed later from the volume calculation
vessel_cell.fill = mat_iron

my_geometry = openmc.Geometry([vessel_cell])


# SIMULATION SETTINGS

# Instantiate a Settings object
my_settings = openmc.Settings()
batches = 10
my_settings.batches = batches
my_settings.inactive = 0
my_settings.particles = 10000
my_settings.run_mode = 'fixed source'

# Create a DT point source
my_source = openmc.IndependentSource(
    space=openmc.stats.Point((0, 0, 0)),
    angle=openmc.stats.Isotropic(),
    energy=openmc.stats.Discrete([14e6], [1])
)
my_settings.source = my_source

# %% [markdown]
# This sets up the damage energy tally using the score name 'damage-energy' which the same as the ENDF MT number 444. A list of MT numbers including their reaction discription can be found [here](https://t2.lanl.gov/nis/endf/mts.html).

# %%
# added a cell tally for DPA to the iron vessel cell
cell_filter = openmc.CellFilter(vessel_cell)
dpa_reaction_tally = openmc.Tally(name='DPA')
dpa_reaction_tally.filters = [cell_filter]
dpa_reaction_tally.scores = ['damage-energy']  # Could use '444' instead, which is the MT reaction number for damage energy more MT numbers here https://t2.lanl.gov/nis/endf/mts.html
dpa_reaction_tally.nuclides = ['Fe54', 'Fe56', 'Fe57', 'Fe58'] # this records the tally for each nuclide in the list
my_tallies = openmc.Tallies([dpa_reaction_tally])

# %% [markdown]
# The geometry is very simple but we can still plot it with the source term just to check we have made the geometry as expected

# %%
model = openmc.Model(my_geometry, my_materials, my_settings, my_tallies)
model.plot(n_samples=10, pixels=400000)

# %% [markdown]
# This runs the simulation.

# %%
for f in Path('.').glob('*.h5'):
    f.unlink(missing_ok=True)
sp_filename = model.run()

# %% [markdown]
# This extracts the simulation results and displays the damage-energy (444 MT number tally) for each nuclide

# %%
with openmc.StatePoint(sp_filename) as sp:

    # access the tally
    tally = sp.get_tally(name='DPA')

    df = tally.get_pandas_dataframe()

    print(df)

# %% [markdown]
# The damage-energy ($T_{d}$) represents the the kinetic energy available for creating atomic displacements. This variable can be used to compute the total number of displacements per atom - or DPA. The current international standard [1] for quantifying DPA is based on the Kinchin-Pease model or NRT equation [2], which states that the number of Frenkel pairs produced $N_{d}$ in a material with displacement energy $E_{d}$ for a nuclear deposited energy $T_{d}$ is
#
# $$N_{d} = \dfrac{0.8T_{d}}{2E_d},$$
#
# where the factor 0.8 was introduced by the authors to allow for realistic atomic scattering instead of the hard core approximation.
#
# [1] ASTM Standard E693-94, 'Standard practice for characterising neutron exposure in iron and low alloy steels in terms of displacements per atom (dpa)', 1994
#
# [2] https://doi.org/10.1016%2F0029-5493%2875%2990035-7

# %%
damage_energy_in_ev = df['mean'].sum() #T_D in NRT equation
E_D = 40 # threshold displacement energy of Fe in eV

print('Damage energy deposited per source neutron = ', f"{damage_energy_in_ev:.2f}", 'eV\n')

print('Two times the threshold energy of 40eV is needed to displace an atom')
displacements_per_source_neutron = 0.8*damage_energy_in_ev / (2*E_D)
print('(NRT) Displacements per source neutron = ', f"{displacements_per_source_neutron:.2f}", '\n')

# %%
fusion_power = 3e9  # units Watts
energy_per_fusion_reaction = 17.6e6  # units eV
eV_to_Joules = 1.60218e-19  # multiplication factor to convert eV to Joules
number_of_neutrons_per_second = fusion_power / (energy_per_fusion_reaction * eV_to_Joules)
print('Number of neutrons per second', f"{number_of_neutrons_per_second:.2e}", '\n')

number_of_neutrons_per_year = number_of_neutrons_per_second * 60 * 60 * 24 * 365.25
print('Number of neutrons per full power year ', f"{number_of_neutrons_per_year:.2e}")

displacements_for_all_atoms = number_of_neutrons_per_year * displacements_per_source_neutron
print('(NRT) Displacements for all atoms in the volume ', f"{displacements_for_all_atoms:.2e}", '\n')

print('Now the number of atoms in the volume must be found to find displacements per atom (DPA)')

volume_of_firstwall_cell = 4.18879e6  # 4/3PiR^3 with R=100

iron_atomic_mass_in_g = 55.845*1.66054E-24  # molar mass multiplier by the atomic mass unit (u)
number_of_iron_atoms = volume_of_firstwall_cell * density_of_iron_in_g_per_cm3 / (iron_atomic_mass_in_g)

print('Number of iron atoms in the firstwall ', f"{number_of_iron_atoms:.2e}")

# %% [markdown]
# Therefore, as the total number of atoms and the total number of displacements is known, NRT-DPA can be found.

# %%
DPA_NRT = displacements_for_all_atoms / number_of_iron_atoms

print('NRT-DPA =', f"{DPA_NRT:.2f}")

# %% [markdown]
# Recently, a new method [3] was proposed in 2018 to solve the limitations of NRT equation. Namely, experiments have shown that "the number of radiation defects produced in energetic cascades in metals is only ~1/3 the NRT-DPA prediction". The arc-DPA (athermal recombination corrected) extends the NRT-DPA approach by assuming that, after the so-called 'thermal spike', "almost all atoms regain positions in the perfect lattice sites [...] only interstitials transported to the cascade outer periphery will result in stable defects". 
#
# Hence, in order to account for this behaviour, the authors modified the original NRT equation as follows:
#
# $$N_{d} = \dfrac{0.8T_{D}}{2E_d} \cdot \xi(T_d)= \dfrac{0.8T_{D}}{2E_d}\left( \dfrac{1-c}{{(2E_D/0.8)}^b} {T_D}^b + c\right),$$
#
# where $\xi$ is a surviving defect fraction factor and $b$ and $c$ are constants for a given metal. For Fe, $b=−0.568$ and $c=0.286$.
#
# [3] DOI: 10.1038/s41467-018-03415-5

# %%
b = -0.568 # constant for Fe
c = 0.286

surviving_defect_fraction_factor = (1-c)*(displacements_per_source_neutron)**b+c
displacements_per_source_neutron_arc = displacements_per_source_neutron*surviving_defect_fraction_factor

print('(arc) Displacements per source neutron = ', f"{displacements_per_source_neutron_arc:.2f}", '\n')

displacements_for_all_atoms_arc = number_of_neutrons_per_year * displacements_per_source_neutron_arc
print('(arc) Displacements for all atoms in the volume ', f"{displacements_for_all_atoms_arc:.2e}", '\n')

arc_NRT = displacements_for_all_atoms_arc / number_of_iron_atoms

print('arc-DPA =', f"{arc_NRT:.2f}", '\n')

print('arc/NRT =', f"{arc_NRT/DPA_NRT:.2f}")

# %% [markdown]
# In this task we knew the volume of the cell as it was a sphere of radius 100. If you don't know the volume of the cell there is a stochastic volume task that might be of interest as it shows you how OpenMC can find the volume of more complex cells.
#
# **Extra topics
# There are better methods of predicting DPA, further reading https://www.nature.com/articles/s41467-018-03415-5/
#
# **Learning Outcomes for Task 6:**
#
# - Damage energy deposited can be found with the OpenMC MT 444 tally.
# - Post tally calculations are sometimes required to convert neutronics numbers into something more useful.
