# Tallies

Tallies measure things. In OpenMC you stack **filters** (what to tally over — cells, meshes, energies, particles) with **scores** (the quantity — flux, heating, `(n,Xt)`, damage-energy).

## The three patterns you need for fusion

### 1. Cell tally — TBR, heating-per-cell, flux-per-cell

```python
cell_filter = openmc.CellFilter(breeder_cell)
tbr = openmc.Tally(name='TBR')
tbr.filters = [cell_filter]
tbr.scores  = ['H3-production']   # equivalent to (n,Xt): tritium from (n,t) + (n,nt) on Li6/Li7
tbr.nuclides = ['Li6', 'Li7']     # optional — per-nuclide breakdown

heating = openmc.Tally(name='heating')
heating.filters = [openmc.CellFilter(fw_cell)]
heating.scores  = ['heating']     # eV per source particle (neutron + photon heating)

tallies = openmc.Tallies([tbr, heating])
```

Common fusion scores: `flux`, `heating` (eV/source, total nuclear heating including secondaries — requires coupled n+γ transport), `heating-local` (eV/source, assumes secondary photons deposit locally — for neutron-only runs), `H3-production`, `damage-energy` (DPA precursor, eV), `(n,2n)`, `(n,a)`, `(n,p)`, `(n,gamma)`, `absorption`.

### 2. Mesh tally — spatial maps of flux / dose / damage

```python
import numpy as np

mesh = openmc.RegularMesh().from_domain(geometry, dimension=(100, 100, 1))
# or explicit: mesh.lower_left = (-600, -600, -1); mesh.upper_right = (600, 600, 1); mesh.dimension = (100, 100, 1)

flux_map = openmc.Tally(name='flux_map')
flux_map.filters = [openmc.MeshFilter(mesh), openmc.ParticleFilter('neutron')]
flux_map.scores  = ['flux', 'heating', '(n,2n)']     # several scores share one tally — more memory efficient
```

Multiple scores on one tally is strictly better than one tally per score: one transport pass populates all of them, and the file size is smaller.

For huge meshes, disable the `tallies.out` ASCII dump:

```python
settings.output = {'tallies': False}
```

### 3. Spectrum tally — flux per energy group

```python
# 709-group VITAMIN-J structure is standard for fusion shielding
from openmc.mgxs import GROUP_STRUCTURES
energies = GROUP_STRUCTURES['VITAMIN-J-175']   # or 'CCFE-709', 'UKAEA-1102', 'LLNL-616' (fusion-friendly options)

spectrum = openmc.Tally(name='fw_spectrum')
spectrum.filters = [
    openmc.CellFilter(fw_cell),
    openmc.EnergyFilter(energies),
]
spectrum.scores = ['flux']
```

## Running and reading results — two idioms

### Preferred: `apply_tally_results=True`

`model.run(apply_tally_results=True)` both runs OpenMC and populates `tally.mean` / `tally.std_dev` in-memory on your Python `Tally` objects. No need to reopen a statepoint.

```python
model = openmc.Model(geometry, materials, settings, tallies)
model.run(apply_tally_results=True)

print(tbr.mean.sum())          # scalar TBR
print(flux_map.mean.shape)     # reshape per filter dimensions below
```

### Classic: `StatePoint`

Useful when you want to re-analyse old results or when `apply_tally_results` isn't available for some reason (e.g. MPI / cluster setups that pickle things).

```python
sp_file = model.run()
with openmc.StatePoint(sp_file) as sp:
    tally = sp.get_tally(name='TBR')
    df    = tally.get_pandas_dataframe()
    total = df['mean'].sum()
```

Always clean old files first or `openmc.StatePoint` may read a stale file:

```python
from pathlib import Path
for f in Path('.').glob('*.h5'): f.unlink(missing_ok=True)
```

## Reshaping mesh results for plotting

```python
flux = flux_map.get_reshaped_data(value='mean',    expand_dims=True).squeeze()
err  = flux_map.get_reshaped_data(value='std_dev', expand_dims=True).squeeze()

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
fig, ax = plt.subplots()
ax.imshow(flux.T, origin='lower', extent=mesh.bounding_box.extent['xy'], norm=LogNorm())
geometry.plot(outline='only', axes=ax, extent=mesh.bounding_box.extent['xy'], pixels=10_000_000)
```

`.T` is usually needed because `imshow` expects (y, x) ordering; `extent` is required or axes default to array indices. The `outline='only'` overlay on the same `axes` draws the geometry on top of the heatmap.

## Per-nuclide breakdowns

```python
tbr.nuclides = ['Li6', 'Li7']
# after run:
df = tbr.get_pandas_dataframe()
li6 = df[df['nuclide'] == 'Li6']['mean'].sum()
li7 = df[df['nuclide'] == 'Li7']['mean'].sum()
```

## Surface / current tallies — for dose on a surface

```python
surf_filter     = openmc.SurfaceFilter(measurement_sphere)
particle_filter = openmc.ParticleFilter('photon')
energy_fn       = openmc.EnergyFunctionFilter(energy_bins, dose_coeffs)  # see dose.md
energy_fn.interpolation = 'cubic'

dose_surf = openmc.Tally(name='surface_dose')
dose_surf.filters = [surf_filter, particle_filter, energy_fn]
dose_surf.scores  = ['current']   # not 'flux' — we want the crossings
```

The tally result is in **pSv·cm²** (dose per source particle, integrated over the surface). Divide by the surface area and multiply by the real source rate to get pSv/s.

## Normalising to a real source rate

Tally means are "per source particle". To get absolute units, multiply by the source rate (n/s) — for a 500 MW DT plasma, that's ~1.775e20 n/s. For DT:

```python
DT_NEUTRONS_PER_MW = 3.55e17       # n/s per MW of fusion
source_rate = fusion_power_MW * DT_NEUTRONS_PER_MW
absolute = tally.mean * source_rate
```

## Useful fusion-specific tally helpers

- `openmc_regular_mesh_plotter` — one-line heatmap plots with geometry outline
- `dagmc_geometry_slice_plotter` — plot slices through a DAGMC model alongside mesh results
- DPA: tally `'damage-energy'` (eV), divide by 2·E_d with E_d = threshold displacement energy (40 eV for Fe) and the atom density in the cell

## Canonical tasks

- Cell tally / TBR: `tasks/task_05_CSG_cell_tally_TBR/`
- DPA: `tasks/task_06_CSG_cell_tally_DPA/`
- Spectrum: `tasks/task_07_CSG_cell_tally_spectra/`
- Mesh: `tasks/task_08_CSG_mesh_tally/`, `tasks/task_18_CAD_mesh_fast_flux/`
- Neutron wall loading: `tasks/task_19_CAD_neutron_wall_loading/`
