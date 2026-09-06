# CAD geometry → DAGMC → OpenMC

Four libraries cooperate. Know their roles before you write code:

- **`cadquery`** — scripted CAD (boxes, cuts, fillets, revolutions). Output: `cq.Workplane` or `cq.Assembly`.
- **`paramak`** — parametric fusion reactors (tokamak, spherical tokamak, TF/PF coils). Built on cadquery. Output: higher-level reactor objects that export to STEP or directly to `cad_to_dagmc`.
- **`cad_to_dagmc`** — meshes CAD into a DAGMC `.h5m` file with material tags. Input: STEP file or cadquery object. Output: `dagmc.h5m`.
- **`openmc`** — reads the `.h5m` via `DAGMCUniverse` and runs transport.

## Scripted CAD with cadquery

```python
import cadquery as cq

# Simple primitives
box    = cq.Workplane('XY').box(10, 10, 10)
sphere = cq.Workplane('XY').sphere(5)
cyl    = cq.Workplane('XY').cylinder(height=20, radius=3)

# Boolean ops
shell = sphere.cut(cq.Workplane('XY').sphere(4))

# Revolve a profile
profile = cq.Workplane('XZ').polyline([(300, -700), (300, 0), (400, 0), (400, -700)]).close()
div = profile.revolve(180)                 # 180° sector

# Extrude text (for quick tests)
label = cq.Workplane().text(txt='fusion', fontsize=10, distance=1)

# Collect into an assembly — each member can have its own material tag
assy = cq.Assembly()
assy.add(box,   name='steel_box',   color=cq.Color('red'))
assy.add(shell, name='breeder',     color=cq.Color('blue'))
assy.export('my_geometry.step')
```

## Parametric fusion reactors with paramak

```python
import paramak

reactor = paramak.tokamak(
    radial_build=[
        (paramak.LayerType.GAP,   10),
        (paramak.LayerType.SOLID, 30),    # center column
        (paramak.LayerType.SOLID, 50),    # inboard blanket
        (paramak.LayerType.SOLID, 10),    # inboard first wall
        (paramak.LayerType.GAP,   60),
        (paramak.LayerType.PLASMA, 300),
        (paramak.LayerType.GAP,   60),
        (paramak.LayerType.SOLID, 10),    # outboard first wall
        (paramak.LayerType.SOLID, 110),   # outboard blanket
        (paramak.LayerType.SOLID, 10),    # rear wall
    ],
    vertical_build=[                       # same LayerType pattern, vertical
        (paramak.LayerType.SOLID, 15),
        (paramak.LayerType.SOLID, 80),
        (paramak.LayerType.SOLID, 10),
        (paramak.LayerType.GAP,   50),
        (paramak.LayerType.PLASMA, 700),
        (paramak.LayerType.GAP,   60),
        (paramak.LayerType.SOLID, 10),
        (paramak.LayerType.SOLID, 40),
        (paramak.LayerType.SOLID, 15),
    ],
    elongation=2,
    triangularity=0.55,
    rotation_angle=180,                   # 180° sector — use reflective BC in OpenMC
)
```

Other paramak builders: `spherical_tokamak_from_plasma`, `toroidal_field_coil_rectangle`, `poloidal_field_coil`, `poloidal_field_coil_case`. You can mix them via `extra_cut_shapes=` and `extra_intersect_shapes=`:

```python
tf = paramak.toroidal_field_coil_rectangle(
    horizontal_start_point=(10, 520),
    vertical_mid_point=(860, 0),
    thickness=50, distance=40,
    rotation_angle=180, with_inner_leg=True,
    azimuthal_placement_angles=[0, 30, 60, 90, 120, 150, 180],
)
reactor = paramak.tokamak(radial_build=..., vertical_build=..., extra_cut_shapes=[tf], ...)
```

## CAD → DAGMC (`cad_to_dagmc`)

Three input routes. Output is always a meshed `.h5m` file tagged with material names.

```python
from cad_to_dagmc import CadToDagmc

m = CadToDagmc()

# (a) from a STEP file — list of material tags, one per volume
m.add_stp_file('my_geometry.step', material_tags=['steel', 'breeder', 'vacuum_vessel'])

# (b) from a cadquery object — list per volume, or 'assembly_names' to use Assembly member names
import cadquery as cq
text = cq.Workplane().text(txt='fusion', fontsize=10, distance=1)
m.add_cadquery_object(text, material_tags=['mat1'] * 10)   # 10 letter-volumes all tagged mat1

# (c) from a paramak reactor — reactor.export_dagmc_h5m_file(...) does it directly
reactor.export_dagmc_h5m_file(
    filename='dagmc.h5m',
    material_tags=['void', 'center_col', 'blanket', 'fw_in', 'fw_out', 'blanket_out', 'rear_wall'],
    max_mesh_size=10, min_mesh_size=2,
)

# Finalise — control mesh density globally or per-volume
m.export_dagmc_h5m_file('dagmc.h5m', max_mesh_size=10, min_mesh_size=2)

# Per-volume mesh size for fine features
m.export_dagmc_h5m_file('dagmc.h5m', set_size={1: 0.5, 2: 2.0, 3: 2.0})

# Also export the tet-mesh version for unstructured mesh tallies
m.export_unstructured_mesh_file('dagmc.vtk', max_mesh_size=10, min_mesh_size=2)
```

Using an `Assembly` with `name=` on each member + `material_tags='assembly_names'` is the cleanest route — the names propagate directly, no need to keep a separate list in sync.

## DAGMC in OpenMC

```python
# Load the meshed CAD as a universe
dag_univ = openmc.DAGMCUniverse(filename='dagmc.h5m', auto_geom_ids=True)

# Inspect what's inside (tag names, bounding box)
print(dag_univ.material_names)        # -> ['steel', 'breeder', ...]
print(dag_univ.bounding_box)

# Route A — let the DAGMC universe cover everything with a vacuum boundary
bounded = dag_univ.bounded_universe()     # wraps in a CSG sphere with vacuum BC
geometry = openmc.Geometry(bounded)

# Route B — embed DAGMC inside your own CSG, e.g. to add reflective sector cuts
sphere = openmc.Sphere(r=1000, boundary_type='vacuum')
xp = openmc.XPlane(x0=0, boundary_type='reflective')
yp = openmc.YPlane(y0=0, boundary_type='reflective')
cell = openmc.Cell(region=-sphere & +xp & +yp, fill=dag_univ)
geometry = openmc.Geometry([cell])
```

**The tag-to-material link.** Every material name in OpenMC must match a DAGMC tag exactly, or OpenMC will refuse to start. For tag `steel`:

```python
steel = openmc.Material(name='steel')       # name is load-bearing
steel.add_element('Fe', 1); steel.set_density('g/cm3', 7.9)
materials = openmc.Materials([steel])
```

Set `auto_geom_ids=True` to avoid ID collisions with any surrounding CSG.

## Plotting / slicing DAGMC models

```python
from dagmc_geometry_slice_plotter import plot_slice
plot_slice(filename='dagmc.h5m', plane_origin=(0, 0, 0), plane_normal=(0, 0, 1))
```

Or the built-in `model.plot(...)` works once materials + a minimal source + settings are defined.

## Common failure modes

- **Tag/name mismatch** — `dag_univ.material_names` doesn't match any `openmc.Material(name=...)`. Print both and diff.
- **Mesh too coarse** — particles escape through faceting gaps. Lower `max_mesh_size`, or set per-volume `set_size` for thin regions (first walls, coil cases).
- **Geometry not watertight** — comes from imported STEP files with small gaps; `cad_to_dagmc` warns but still exports. Inspect with `pydagmc` or `dagmc_h5m_file_inspector`.
- **No vacuum boundary** — if you use route A (`bounded_universe()`), OpenMC adds one; if route B, you must ensure the outer CSG boundary is `boundary_type='vacuum'` or particles leak infinitely.

## Canonical tasks

- Scripted CAD: `tasks/task_15_making_CAD_geometry/1_making_cad_with_cadquery.py`
- Paramak: `tasks/task_15_making_CAD_geometry/2_making_cad_with_paramak.py`
- CAD → DAGMC: `tasks/task_16_converting_CAD_geometry_to_DAGMC/`
- DAGMC in OpenMC: `tasks/task_17_using_DAGMC_models_in_openmc/` (minimal, boundary types, hybrid CSG)
- Mesh fast flux on CAD: `tasks/task_18_CAD_mesh_fast_flux/`
- Neutron wall loading: `tasks/task_19_CAD_neutron_wall_loading/`
