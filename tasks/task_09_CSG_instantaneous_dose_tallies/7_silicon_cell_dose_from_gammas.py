# %% [markdown]
# ---
# title: Silicon dose from gammas without any silicon in the model
# ---

# %% [markdown]
# Notebook 6 finds the neutron dose in silicon without putting any silicon in the model, using `multiply_density=False` together with `Tally.apply_virtual_material`. That works because neutron heating is scored as a flux multiplied by a microscopic cross section, so OpenMC can simply substitute an atom density of your choosing.
#
# **The same approach does not work for photons.** OpenMC scores photon energy deposition collision by collision, from the energy balance of each interaction, and attributes it to the nuclide that was actually struck. There is no atom density in that score at all, so:
#
# - in a cell containing no silicon, a silicon nuclide bin scores exactly zero
# - in a cell that does contain silicon, the score already includes the atom density, so applying a virtual material on top would count it twice
#
# The second case does at least raise, `apply_virtual_material` refuses to run on a tally with `multiply_density` left at `True`. The first case is the dangerous one: everything runs and you get a silicon dose of zero. It is worth knowing what that failure looks like.
#
# This task demonstrates both failure modes and then shows a way around them. Instead of a microscopic cross section we fold the photon flux with the silicon mass energy-absorption coefficient, which turns a fluence directly into an absorbed dose and, like the neutron method, needs no silicon in the model.
#
# **Treat what follows as a work around for a current OpenMC limitation, not as the intended way to do this.** The neutron method is clean because OpenMC stores neutron kerma coefficients that a tally can score against, and `multiply_density` and `apply_virtual_material` are built on top of them. There is no equivalent photon kerma cross section in OpenMC, so there is nothing for a virtual material to scale and the response has to be supplied from outside, here from the NIST tables that ship with `openmc.data`. If OpenMC gains a photon kerma response then the neutron approach would extend to gammas directly and this task would no longer be needed.

# %%
from pathlib import Path

import numpy as np
import openmc

# Setting the cross section path to the correct location in the docker image.
# If you are running this outside the docker image you will have to change this path to your local cross section path.
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# %% [markdown]
# ## Model
#
# A deliberately small model, a Co-60 gamma source at the centre of an iron sphere with a thin shell of real silicon around it.
#
# The iron sphere contains no silicon, so it is where the virtual material would be useful. The silicon shell is only there so that the answer can be checked against a material that really is silicon.

# %%
iron = openmc.Material(name='iron')
iron.add_element('Fe', 1.0)
iron.set_density('g/cm3', 7.874)

# the real silicon shell, used only to check the answer
real_silicon = openmc.Material(name='real silicon')
real_silicon.add_element('Si', 1.0)
real_silicon.set_density('g/cm3', 2.329)

inner_sphere = openmc.Sphere(r=10.0)
outer_sphere = openmc.Sphere(r=11.0, boundary_type='vacuum')

iron_cell = openmc.Cell(name='iron', region=-inner_sphere, fill=iron)
shell_cell = openmc.Cell(name='silicon shell', region=+inner_sphere & -outer_sphere, fill=real_silicon)

# cell tallies are not divided by volume by OpenMC so the volumes are needed later
iron_cell.volume = 4 / 3 * np.pi * 10.0**3
shell_cell.volume = 4 / 3 * np.pi * (11.0**3 - 10.0**3)

geometry = openmc.Geometry([iron_cell, shell_cell])
materials = openmc.Materials([iron, real_silicon])

source = openmc.IndependentSource(
    space=openmc.stats.Point((0.0, 0.0, 0.0)),
    energy=openmc.stats.Discrete([1.1732e6, 1.3325e6], [0.5, 0.5]),  # Co-60
    angle=openmc.stats.Isotropic(),
    particle='photon',
)

settings = openmc.Settings(
    run_mode='fixed source',
    photon_transport=True,
    particles=100_000,
    batches=10,
    source=source,
    seed=1,
)

# %% [markdown]
# ## The virtual silicon
#
# This is the material we want the dose in. As in task 6 it is never added to the geometry.

# %%
silicon = openmc.Material(name='virtual silicon')
silicon.add_element('Si', 1.0)
silicon.set_density('g/cm3', 2.329)

# %% [markdown]
# ## Tallies
#
# Six photon tallies, all on cells, in four groups:
#
# 1. `si_virtual_iron`, the approach that does not work, a heating tally with silicon nuclide bins and `multiply_density=False` in the iron cell
# 2. `si_micro_shell` and `si_macro_shell`, the same heating tally in the real silicon shell with `multiply_density` set to `False` and to `True`, to show that the setting is ignored for photons
# 3. `si_kerma_iron`, the approach that does work, the photon flux folded with the silicon mass energy-absorption coefficient, in the iron cell
# 4. `si_kerma_shell` and `si_heating_shell`, the same response and a plain heating tally in the real silicon shell, so the two routes can be compared where silicon really is present
#
# The mass energy-absorption coefficient is tabulated in cm2/g, so multiplying it by the energy gives the eV cm2/g needed to turn a fluence into a dose. It is tabulated from 1 keV, which is also the default photon cutoff in OpenMC, so no photon flux is lost at the bottom of the range. The table stops at 20 MeV, which is comfortably above anything a Co-60 source or a DT-driven model produces, but an `EnergyFunctionFilter` silently scores nothing outside its tabulated range so it is worth checking for a harder source.

# %%
photon_filter = openmc.ParticleFilter('photon')
iron_filter = openmc.CellFilter(iron_cell)
shell_filter = openmc.CellFilter(shell_cell)

mu_en = openmc.data.mass_energy_absorption_coefficient('Si')
kerma_filter = openmc.EnergyFunctionFilter(mu_en.x, mu_en.x * mu_en.y)
kerma_filter.interpolation = 'log-log'

def heating_tally(name, cell_filter, multiply_density):
    tally = openmc.Tally(name=name)
    tally.filters = [cell_filter, photon_filter]
    tally.scores = ['heating']
    tally.nuclides = silicon.get_nuclides()
    tally.multiply_density = multiply_density
    return tally

def kerma_tally(name, cell_filter):
    tally = openmc.Tally(name=name)
    tally.filters = [cell_filter, photon_filter, kerma_filter]
    tally.scores = ['flux']
    return tally

si_virtual_iron = heating_tally('si_virtual_iron', iron_filter, multiply_density=False)
si_micro_shell = heating_tally('si_micro_shell', shell_filter, multiply_density=False)
si_macro_shell = heating_tally('si_macro_shell', shell_filter, multiply_density=True)

si_kerma_iron = kerma_tally('si_kerma_iron', iron_filter)
si_kerma_shell = kerma_tally('si_kerma_shell', shell_filter)

si_heating_shell = openmc.Tally(name='si_heating_shell')
si_heating_shell.filters = [shell_filter, photon_filter]
si_heating_shell.scores = ['heating']

# %%
model = openmc.Model(
    geometry=geometry,
    materials=materials,
    settings=settings,
    tallies=[
        si_virtual_iron, si_micro_shell, si_macro_shell,
        si_kerma_iron, si_kerma_shell, si_heating_shell,
    ],
)
model.run(apply_tally_results=True)

# %% [markdown]
# ## Failure mode 1, silicon bins score nothing where there is no silicon
#
# The iron cell contains no silicon, so every silicon nuclide bin is exactly zero. Calling `apply_virtual_material` on this tally would multiply zero by the atom densities and report a silicon dose of zero, without any warning.

# %%
for nuclide, value in zip(si_virtual_iron.nuclides, si_virtual_iron.mean.flatten()):
    print(f"{nuclide} heating in the iron cell: {value}")

# %% [markdown]
# ## Failure mode 2, `multiply_density` is ignored for photons
#
# In the silicon shell the same tally does score, but the two settings of `multiply_density` give identical numbers. The atom density is already baked in, so applying a virtual material here would apply the densities a second time.

# %%
micro = si_micro_shell.mean.flatten()
macro = si_macro_shell.mean.flatten()
for nuclide, a, b in zip(si_micro_shell.nuclides, micro, macro):
    print(f"{nuclide}: multiply_density=False {a:.6e}   multiply_density=True {b:.6e}")
print(f"identical: {np.array_equal(micro, macro)}")

# %% [markdown]
# ## What works instead
#
# The photon flux folded with the silicon mass energy-absorption coefficient gives eV cm3/g per source particle. Dividing by the cell volume and converting grams to kilograms and eV to joules gives Gy per source particle. No silicon is needed anywhere in the model.

# %%
GRAMS_PER_KG = 1000

def kerma_dose(tally, volume):
    """Gy per source particle from a flux tally folded with E * mu_en/rho."""
    ev_cm3_per_g = tally.mean.sum()
    return ev_cm3_per_g / volume * GRAMS_PER_KG * openmc.data.JOULE_PER_EV

dose_in_iron = kerma_dose(si_kerma_iron, iron_cell.volume)
error_in_iron = si_kerma_iron.std_dev.sum() / si_kerma_iron.mean.sum()
print(f"Silicon dose in the iron cell: {dose_in_iron:.4e} Gy per source photon "
      f"+/- {100 * error_in_iron:.2f}%")

# %% [markdown]
# ## Checking the answer
#
# Where silicon really is present the same response function can be compared with a plain heating tally, which needs no tricks.
#
# This checks the response function, the interpolation and the whole unit chain against OpenMC's own photon physics. It is not a fully independent test of the underlying dose concept, because OpenMC does not transport electrons by default and deposits their energy where they are created, which is the same charged particle equilibrium assumption that the mass energy-absorption coefficient makes.

# %%
dose_kerma = kerma_dose(si_kerma_shell, shell_cell.volume)

si_kg_per_cm3 = real_silicon.get_mass_density() * 1e-3
dose_heating = (
    si_heating_shell.mean.sum() * openmc.data.JOULE_PER_EV
    / (shell_cell.volume * si_kg_per_cm3)
)

# the relative uncertainty carries straight through the unit conversion
error_kerma = si_kerma_shell.std_dev.sum() / si_kerma_shell.mean.sum()
error_heating = si_heating_shell.std_dev.sum() / si_heating_shell.mean.sum()

print(f"silicon shell, mass energy-absorption route: {dose_kerma:.4e} Gy per source photon "
      f"+/- {100 * error_kerma:.2f}%")
print(f"silicon shell, direct heating tally:         {dose_heating:.4e} Gy per source photon "
      f"+/- {100 * error_heating:.2f}%")
print(f"ratio: {dose_kerma / dose_heating:.4f}")

# %% [markdown]
# **Learning Outcomes:**
#
# - The virtual material technique works for neutron heating but not for photon heating, and it fails silently in both directions.
# - The mass energy-absorption route is a work around for that gap rather than a supported feature, because OpenMC has no photon kerma cross section for a virtual material to scale.
# - OpenMC scores photon energy deposition collision by collision, against the nuclide that was actually struck, so there is no atom density for a virtual material to replace.
# - Photon dose in a material that is not in the model can instead be found by folding the photon flux with `openmc.data.mass_energy_absorption_coefficient`.
# - The mass energy-absorption coefficient gives the collision kerma, which is the absorbed dose under charged particle equilibrium. It is the mass energy-transfer coefficient that gives the total kerma, the two differing by the electron energy lost to bremsstrahlung.
# - Cell and mesh tallies are not divided by volume by OpenMC, so the volume division has to be done by hand.
