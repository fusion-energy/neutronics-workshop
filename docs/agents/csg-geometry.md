# CSG geometry

Constructive solid geometry: define **surfaces**, combine them with boolean operators into **regions**, wrap regions in **cells**, and collect cells into a **Geometry**.

## Surfaces

```python
import openmc

# Spheres
inner = openmc.Sphere(r=500)
outer = openmc.Sphere(r=610, boundary_type='vacuum')

# Planes
xp = openmc.XPlane(x0=0, boundary_type='reflective')
yp = openmc.YPlane(y0=0)
zp = openmc.ZPlane(z0=0, boundary_type='vacuum')

# Cylinders
zcyl = openmc.ZCylinder(r=50)                # infinite along z
zcyl_bounded_top    = openmc.ZPlane(z0=100)
zcyl_bounded_bottom = openmc.ZPlane(z0=-100)

# Others: XCylinder, YCylinder, Cone, Quadric, GeneralPlane, Torus (limited support)
```

**Boundary types** (`boundary_type=`):
- `'transmission'` (default) — particles cross freely
- `'vacuum'` — particles that cross are killed
- `'reflective'` — specular reflection; use on symmetry planes
- `'periodic'` — pair with a matching periodic surface
- `'white'` — isotropic reflection

For fusion sector models, use `reflective` on the sector cut planes to model 1/N of the torus.

## Regions

Boolean algebra on half-spaces. `+surface` = positive side, `-surface` = negative side. Combine with `&` (intersection), `|` (union), `~` (complement).

```python
# Spherical shell between two spheres
shell_region = +inner & -outer

# Half of that shell, cut by a plane
half_shell = +inner & -outer & +xp

# Union of two regions
either = shell_region | other_region

# Everything except shell
outside = ~shell_region
```

Parentheses work as expected. Regions are lazy — they don't do anything until wrapped in a cell.

## Cells

```python
breeder_cell = openmc.Cell(region=shell_region, fill=breeder_material, name='breeder')
void_cell    = openmc.Cell(region=-inner)                          # no fill = vacuum
```

Pass `fill=` a `Material`, another `Universe` / `DAGMCUniverse`, or leave it None for vacuum.

## Geometry assembly

```python
my_geometry = openmc.Geometry([breeder_cell, fw_cell, vv_cell, void_cell])
```

Cells must collectively cover every point in space that a particle might visit, and must not overlap. If they don't, OpenMC will either run into a "lost particle" error mid-simulation or silently give wrong results. For fusion sphere-in-sphere models it's easy to get right; for complex architectures, check with `geometry.plot(...)` before running.

## Plotting & sanity checks

```python
# 2D slice plot — call on the Model (preferred, includes materials) or Geometry
plot = my_geometry.plot(basis='xz', color_by='material', pixels=(600, 600))
plot.figure.savefig('xz.png')

# In a Model with materials and settings set, this ray-traces and shows the CSG
model.plot(basis='xy', width=(1200, 1200), pixels=400000, color_by='material')
```

Common failure mode: a geometry looks fine in `plot()` but OpenMC reports lost particles — that usually means cells overlap or there's a tiny gap between surfaces. Quick fix: slightly oversize the outer boundary or make the inner surface's match exactly the same coefficients.

## Fusion sphere model — canonical minimal example

```python
# Layers: void → FW → breeder → vacuum boundary
vessel_inner = openmc.Sphere(r=500)
fw_outer     = openmc.Sphere(r=510)
bz_outer     = openmc.Sphere(r=610, boundary_type='vacuum')

void_cell    = openmc.Cell(region=-vessel_inner)
fw_cell      = openmc.Cell(region=+vessel_inner & -fw_outer,  fill=eurofer)
bz_cell      = openmc.Cell(region=+fw_outer     & -bz_outer,  fill=breeder)

geometry = openmc.Geometry([void_cell, fw_cell, bz_cell])
```

This is the pattern used by `task_05` (TBR), `task_06` (DPA), `task_07` (spectra), `task_08` (mesh tally).

## Hybrid CSG + DAGMC

You can put a `DAGMCUniverse` inside a CSG cell (e.g. to add reflective boundaries around a CAD model, or embed a CAD blanket inside a simple CSG vessel). See [`cad-geometry.md`](cad-geometry.md) for the pattern.

## Canonical tasks

`tasks/task_03_making_CSG_geometry/`, `tasks/task_05_CSG_cell_tally_TBR/`, `tasks/task_17_using_DAGMC_models_in_openmc/` (hybrid CSG+DAGMC).
