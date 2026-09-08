# Materials

OpenMC materials are built either from **nuclides** (specific isotopes) or **elements** (natural abundance mix expanded internally). Always set a density.

## The two canonical patterns

```python
import openmc

# By nuclide — full control, useful for enriched materials
breeder = openmc.Material(name='LiPb')
breeder.add_nuclide('Li6', 0.5, percent_type='ao')
breeder.add_nuclide('Li7', 0.5, percent_type='ao')
breeder.add_nuclide('Pb208', 1.0, percent_type='ao')
breeder.set_density('g/cm3', 9.4)

# By element — natural abundance expanded automatically
steel = openmc.Material(name='SS316')
steel.add_element('Fe', 0.68, percent_type='wo')
steel.add_element('Cr', 0.17, percent_type='wo')
steel.add_element('Ni', 0.12, percent_type='wo')
steel.add_element('Mo', 0.03, percent_type='wo')
steel.set_density('g/cm3', 7.99)
```

`percent_type`: `'ao'` = atomic, `'wo'` = weight. Density units: `'g/cm3'`, `'atom/b-cm'` (atoms per barn-cm), `'kg/m3'`.

## Enrichment shorthand

Lithium-6 enrichment for tritium breeding:

```python
breeder = openmc.Material()
breeder.add_element('Pb', 84.2, percent_type='ao')
breeder.add_element(
    'Li', 15.8, percent_type='ao',
    enrichment=60.0,           # percent Li6
    enrichment_target='Li6',
    enrichment_type='ao',
)
breeder.set_density('atom/b-cm', 3.272e-2)
```

Using `atom/b-cm` density means the atom density stays constant across enrichment sweeps — the physical g/cm³ would shift slightly.

## Mixing materials

```python
air = openmc.Material(); air.add_element('N', 0.78); air.add_element('O', 0.21); air.set_density('g/cm3', 0.00122)
water = openmc.Material(); water.add_element('H', 2); water.add_element('O', 1); water.set_density('g/cm3', 1.0)

humid_air = openmc.Material.mix_materials([air, water], [0.99, 0.01], percent_type='vo')
```

## For depletion — two required fields

```python
mat.volume = (4/3) * math.pi * radius**3   # cm³ — must match geometric cell volume
mat.depletable = True
```

Leaving `volume` unset silently produces zero or wrong atom counts. Only mark materials that you actually intend to deplete — every additional depletable material multiplies runtime.

## `neutronics_material_maker` — curated fusion materials

Pre-canned recipes for common fusion materials (Eurofer, SS316L, Be12Ti, breeder ceramics, PbLi at various enrichments) with density functions of temperature/pressure:

```python
from neutronics_material_maker import Material

eurofer = Material.from_library(name='eurofer').openmc_material
pbli = Material.from_library(
    name='lithium-lead',
    enrichment=60.0,                 # Li6 at%
    temperature=600,                 # K
).openmc_material
```

Returns a standard `openmc.Material`, so downstream use is identical.

## Assembly into `Materials`

OpenMC wants all materials collected into a `Materials` object (even though `Model` takes a list directly — either works):

```python
my_materials = openmc.Materials([breeder, steel, eurofer])
```

For DAGMC workflows, the material `name` **must match** the DAGMC material tag in the `.h5m` file. See [`cad-geometry.md`](cad-geometry.md).

## Common pitfalls

- Forgetting to set density → OpenMC errors out loudly, not silently.
- Using `add_element('Li', ...)` when you actually want enriched Li6 — use the `enrichment=...` kwargs, don't split into two `add_element` calls.
- Mixing weight and atom fractions without setting `percent_type` consistently within a material.
- Not all nuclides are in every data library. If `Pb208` fails, your library may only have `Pb` as element-level data, or missing that isotope — use `openmc_data_downloader` to fetch it.

## Canonical task

`tasks/task_02_making_materials/` — six tasks covering isotopes, elements, enrichment sweeps, mixing, and `neutronics_material_maker`.
