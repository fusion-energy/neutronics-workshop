# Dose tallies

Two flavours:

- **Instantaneous dose** — dose rate during operation from neutrons + prompt photons. Uses `EnergyFunctionFilter` with ICRP flux-to-dose coefficients.
- **Shutdown dose rate** — dose from activated materials after the source is turned off. Requires depletion first — see [`shutdown-dose-rate.md`](shutdown-dose-rate.md).

This file covers the instantaneous case.

## ICRP flux-to-dose coefficients

OpenMC ships ICRP-116 tabulated coefficients:

```python
import openmc

e_n, c_n = openmc.data.dose_coefficients(particle='neutron', geometry='AP')
e_p, c_p = openmc.data.dose_coefficients(particle='photon',  geometry='AP')
```

`geometry` options follow ICRP: `'AP'` (front-to-back, most conservative — default choice for unknown orientations), `'PA'`, `'LAT'`, `'ROT'`, `'ISO'`.

Units: `e_*` in eV, `c_*` in pSv·cm².

## Surface dose tally — receptor on a bounding sphere

Classic setup: source, shielding, and a "detector" sphere around it. Tally photon current through the sphere, weighted by the dose coefficients, divide by the sphere surface area.

```python
# --- dose filter ---
ef_p = openmc.EnergyFunctionFilter(e_p, c_p)
ef_p.interpolation = 'cubic'              # ICRP recommendation — not linear

photon_only = openmc.ParticleFilter(['photon'])

# --- measurement surface (radius 100 cm, just inside the vacuum boundary) ---
detector = openmc.Sphere(r=100)
boundary = openmc.Sphere(r=101, boundary_type='vacuum')
# ...build cells so detector is a real surface particles can cross...

surf_filter = openmc.SurfaceFilter(detector)

dose = openmc.Tally(name='surface_dose')
dose.filters = [surf_filter, photon_only, ef_p]
dose.scores  = ['current']                # not flux
```

After running:

```python
import math
# Mean is in pSv·cm² per source particle
df = tally.get_pandas_dataframe()
area = 4 * math.pi * 100**2
pSv_per_source_particle = df['mean'].sum() / area

source_rate = activity_bq * emission_multiplicity      # e.g. 56_000 Bq Co-60 × 2 γ/decay
pSv_per_s = pSv_per_source_particle * source_rate
```

Always use a `SurfaceFilter` on a real (non-boundary) surface — you can't tally on a surface that has `boundary_type='vacuum'`. Put a second sphere of radius `r+1` as the vacuum boundary, tally on the inner one.

## Cell dose tally — dose in a tissue-equivalent volume

```python
tissue = openmc.Material(); tissue.add_element('H', 0.101); tissue.add_element('C', 0.111)
# ... full ICRU tissue recipe ...

cell_filter = openmc.CellFilter(tissue_cell)
dose = openmc.Tally(name='cell_dose')
dose.filters = [cell_filter, ef_n]
dose.scores  = ['flux']
```

Score is `flux`, not `current`. The `EnergyFunctionFilter` turns it into pSv·cm³ per source particle (flux has units of cm/source, × pSv·cm² from the coefficients). Divide by the cell volume to get pSv per source particle.

## Mesh dose — spatial dose map

```python
mesh = openmc.RegularMesh().from_domain(geometry, dimension=(200, 200, 1))

dose_map = openmc.Tally(name='dose_map')
dose_map.filters = [
    openmc.MeshFilter(mesh),
    openmc.ParticleFilter(['neutron', 'photon']),
    ef_n,                  # or concatenate separate neutron + photon tallies
]
dose_map.scores  = ['flux']
```

For both neutron and photon dose, it's cleaner to make **two** tallies (one per particle + its coefficient table) and sum them in post-processing than to try to use a single mixed tally.

## Neutron-only (no photon transport)

By default OpenMC transports both neutrons and photons if the data library supports it. To compute dose from neutrons only, either:

```python
settings.photon_transport = False
```

(kills secondary photons, so you get the neutron component of dose only), or include both by keeping photon transport on and tallying separately with `ParticleFilter`.

For shielding studies, **turn photon transport on** (it's the default when using ENDF/B-VIII.0) — secondary photons from (n,γ) dominate the dose behind thick shields.

## Absolute units — one more multiplier

Tally means are "per source particle". If your source is a 500 MW DT plasma:

```python
DT_N_PER_MW = 3.55e17
src_rate = fusion_power_MW * DT_N_PER_MW        # n/s
absolute_dose_rate_pSv_s = dose_tally.mean * src_rate
```

## Tally convergence

Dose tallies converge slowly because they're weighted by an energy function that peaks in minor parts of the spectrum. Expect to need either many particles (10⁷–10⁸) or **variance reduction** — see [`variance-reduction.md`](variance-reduction.md). FW-CADIS is designed precisely for dose maps behind thick shields.

## Canonical tasks

`tasks/task_09_CSG_instantaneous_dose_tallies/` — surface and cell dose from a Co-60 source, gamma dose coefficient plots, parameter study over shield thickness.
