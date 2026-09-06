# Sources

Fusion neutronics is almost always **fixed-source** with a 14 MeV DT neutron source. The basic building block is `openmc.IndependentSource`, which combines independent `space`, `angle`, and `energy` distributions. (Older examples may use `openmc.Source` — that alias still works but `IndependentSource` is the current name.)

## The minimum 14 MeV DT point source

```python
import openmc

my_source = openmc.IndependentSource(
    space=openmc.stats.Point((0, 0, 0)),
    angle=openmc.stats.Isotropic(),
    energy=openmc.stats.Discrete([14.06e6], [1.0]),  # eV, single line
    particle='neutron',
)

settings = openmc.Settings(
    run_mode='fixed source',
    batches=10,
    particles=10_000,
    source=my_source,
)
```

`run_mode='fixed source'` is mandatory for fusion — the default is eigenvalue, which assumes a fissile system.

## Spatial distributions

```python
# Point
openmc.stats.Point((x, y, z))

# Ring source at major radius R on the z=0 midplane (approximate tokamak plasma)
import math
openmc.stats.CylindricalIndependent(
    r=openmc.stats.Discrete([600.0], [1.0]),         # fixed radius in cm
    phi=openmc.stats.Uniform(0, 2*math.pi),
    z=openmc.stats.Discrete([0.0], [1.0]),
    origin=(0.0, 0.0, 0.0),
)

# Box (uniform sampling)
openmc.stats.Box(lower_left=(-10, -10, -10), upper_right=(10, 10, 10))

# Mesh source — sample from a spatial distribution defined on a mesh
mesh = openmc.RegularMesh()
mesh.lower_left = (-300, -300, -300); mesh.upper_right = (300, 300, 300)
mesh.dimension = (30, 30, 30)
openmc.stats.MeshSpatial(mesh, strengths=flux_array)
```

## Energy distributions

```python
# Mono-energetic
openmc.stats.Discrete([14.06e6], [1.0])

# Watt fission spectrum — rarely relevant for fusion
# Maxwellian at DT plasma temperature (approximate)
openmc.stats.Muir(e0=14.08e6, m_rat=5.0, kt=20_000.0)   # kT in eV, m_rat = DT mass ratio

# Tabulated arbitrary spectrum
openmc.stats.Tabular(x=energies, p=probs, interpolation='histogram')
```

Muir is the right choice for realistic DT thermal broadening of the 14.1 MeV peak; for most shielding/TBR work a `Discrete([14.06e6], [1.0])` peak is fine.

## Angular distributions

```python
openmc.stats.Isotropic()                              # the default choice for fusion
openmc.stats.Monodirectional((1, 0, 0))               # parallel beam (e.g. for benchmarking)
openmc.stats.PolarAzimuthal(...)                      # explicit mu, phi
```

## Plasma-shaped sources — `openmc-plasma-source`

For realistic tokamak / spherical-tokamak plasma emission (Shafranov shift, temperature/density profiles, H/L mode pedestal):

```python
from openmc_plasma_source import tokamak_source

# Units for major/minor/pedestal radius depend on the openmc_plasma_source version
# — check the workshop task_04/3 task for the convention your installed version uses.
# The values below are from task_04/3 and represent an ITER-like plasma.
my_sources = tokamak_source(
    elongation=1.557,
    triangularity=0.270,
    major_radius=9.06,
    minor_radius=2.92258,
    pedestal_radius=0.8 * 2.92258,
    ion_density_centre=1.09e20, ion_density_pedestal=1.09e20, ion_density_separatrix=3e19,
    ion_density_peaking_factor=1,
    ion_temperature_centre=45.9, ion_temperature_pedestal=6.09, ion_temperature_separatrix=0.1,
    ion_temperature_peaking_factor=8.06, ion_temperature_beta=6,
    shafranov_factor=0.44789,
    mode='H',
    mesh_resolution=(100, 100),         # mesh bins in (r, z)
    start_angle=0, rotation_angle=2*3.14159,  # toroidal start angle and extent in radians
)

settings.source = my_sources            # an openmc.MeshSource — OpenMC handles this natively
```

Returns an `openmc.MeshSource` backed by a `CylindricalMesh`; assign it directly to `settings.source` (a single source or a list both work). Each mesh voxel carries a strength proportional to the local neutron emission.

Other useful helpers in the same package: `tokamak_source`, `spherical_tokamak_source`, `fusion_ring_source`, `fusion_point_source`.

## Inspecting / plotting sources

```python
from openmc_source_plotter import plot_source_position, plot_source_direction, plot_source_energy

plot_source_position(this=model, n_samples=2000).show()   # 3D scatter
plot_source_direction(this=model, n_samples=500).show()   # direction quivers
plot_source_energy(this=model, n_samples=50_000).show()   # energy histogram
```

Always plot a new source before running a long simulation — catches unit errors (m vs cm), wrong origin, and missing Shafranov shift.

## Biased / multi-particle sources

```python
# Photon source — useful for R2S second-stage transport and dose-from-gamma-source models
gamma_source = openmc.IndependentSource(
    space=openmc.stats.Point((0, 0, 0)),
    angle=openmc.stats.Isotropic(),
    energy=openmc.stats.Discrete([1.1732e6, 1.3325e6], [0.5, 0.5]),   # Co-60
    particle='photon',
)

# Multiple sources with strength weights
settings.source = [neutron_src, photon_src]        # equal strength by default
neutron_src.strength = 0.7; photon_src.strength = 0.3   # explicit
```

## Canonical tasks

`tasks/task_04_make_sources/` — point, ring, plasma, gamma, mesh-based, and structured mesh sources, each with source-plotter visualisation.
