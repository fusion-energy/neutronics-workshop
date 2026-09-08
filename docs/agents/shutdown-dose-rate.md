# Shutdown dose rate

After the plasma is off, activated materials continue to emit photons — this is the dose field people are exposed to during maintenance. Two workflows:

- **R2S** (Rigorous 2-Step) — deplete each mesh voxel to get its nuclide inventory, then transport decay photons from those voxels. Most accurate; two transport passes + a depletion step.
- **D1S** (Direct 1-Step) — fold activation cross sections and decay data into a single transport calculation. Faster but makes approximations (no build-up of intermediate nuclides).

This repo shows R2S in detail; D1S is in `task_11_CSG_shut_down_dose_tallies/4_D1S_*`.

## R2S — full recipe

### Step 1 — neutron transport onto a tet mesh

Build your DAGMC model *and* an overlay unstructured tet mesh that shares the outer surface:

```python
from cad_to_dagmc import CadToDagmc
dagmc_h5m, umesh_vtk = model.export_dagmc_h5m_file(
    filename='dagmc.h5m',
    max_mesh_size=0.8, min_mesh_size=0.1,
    unstructured_volumes=[1],                # volumes to tet-mesh for depletion
    umesh_filename='umesh.vtk',
)

dag_univ = openmc.DAGMCUniverse('dagmc.h5m').bounded_universe(padding_distance=1)
geometry = openmc.Geometry(dag_univ)
umesh    = openmc.UnstructuredMesh('umesh.vtk', library='moab')
```

The tet mesh will hold one activated material per voxel.

### Step 2 — neutron run, extract flux + micro-XS per voxel

```python
import openmc.deplete

materials = openmc.Materials([my_material])      # with volume, depletable=True
my_material.depletable = True

neutron_source = openmc.IndependentSource(
    space=openmc.stats.Point(geometry.bounding_box.center),
    energy=openmc.stats.Discrete([14e6], [1]),
    angle=openmc.stats.Isotropic(),
)
settings = openmc.Settings(run_mode='fixed source', batches=5, particles=5000, source=neutron_source)
model = openmc.Model(geometry, materials, settings)

flux_in_each_voxel, micro_xs = openmc.deplete.get_microxs_and_flux(
    model=model,
    domains=umesh,
    energies=[0, 30e6],
    chain_file=openmc.config['chain_file'],
    run_kwargs={'cwd': '.'},                     # keep statepoint local
    nuclides=my_material.get_nuclides(),
)
```

### Step 3 — grab voxel volumes from the statepoint

```python
sp = openmc.StatePoint(f'statepoint.{settings.batches}.h5')
umesh_sp = sp.meshes[umesh.id]                   # reading triggers centroid/volume calc
mesh_vols = umesh_sp.volumes
```

### Step 4 — deplete each voxel's material independently

```python
voxel_materials = []
for i, vol in enumerate(mesh_vols, start=2):     # start=2 to avoid ID collision with my_material
    vm = my_material.clone()
    vm.id = i
    vm.volume = vol
    voxel_materials.append(vm)

op = openmc.deplete.IndependentOperator(
    materials=openmc.Materials(voxel_materials),
    fluxes=[f[0] for f in flux_in_each_voxel],
    micros=micro_xs,
    reduce_chain_level=5,
    normalization_mode='source-rate',
)

integrator = openmc.deplete.PredictorIntegrator(
    op,
    timesteps=[5, 60, 60],                       # 5 s pulse + two 60 s cool steps
    source_rates=[1e20, 0, 0],
    timestep_units='s',
)
integrator.integrate()
```

### Step 5 — build a mesh photon source from the depleted materials

```python
results = openmc.deplete.Results('depletion_results.h5')
last = results[-1]

photon_sources = []
for i, vol in enumerate(mesh_vols, start=2):
    activated = last.get_material(str(i))
    activated.volume = vol
    energy = activated.get_decay_photon_energy(clip_tolerance=1e-6, units='Bq')
    strength = energy.integral() if energy else 0.0

    photon_sources.append(openmc.IndependentSource(
        energy=energy,
        particle='photon',
        strength=strength,
    ))

mesh_source = openmc.MeshSource(mesh=umesh_sp, sources=photon_sources)
```

`get_decay_photon_energy(units='Bq')` returns an energy distribution normalised by activity so that `source.strength = integral()` gives photons/second.

### Step 6 — photon transport with a dose tally

```python
photon_settings = openmc.Settings(
    run_mode='fixed source',
    batches=100,
    particles=10_000,
    source=mesh_source,
    photon_transport=True,
)

e_p, c_p = openmc.data.dose_coefficients(particle='photon', geometry='AP')
dose_filter = openmc.EnergyFunctionFilter(e_p, c_p, interpolation='cubic')

dose_mesh = openmc.RegularMesh().from_domain(geometry, dimension=(100, 100, 100))
dose_tally = openmc.Tally(name='shutdown_photon_dose')
dose_tally.filters = [openmc.MeshFilter(dose_mesh), dose_filter, openmc.ParticleFilter(['photon'])]
dose_tally.scores  = ['flux']

gamma_model = openmc.Model(geometry, materials, photon_settings, openmc.Tallies([dose_tally]))
Path('photons').mkdir(exist_ok=True)
gamma_sp = gamma_model.run(cwd='photons')
```

### Step 7 — normalise and plot

Tally units are pSv·cm³ per source photon; source strength is already in photons/s, so tally × strength / voxel_volume = pSv/s.

```python
from openmc_regular_mesh_plotter import plot_mesh_tally
from matplotlib.colors import LogNorm

pico_to_micro = 1e-6
seconds_to_hours = 3600
scale = (seconds_to_hours * pico_to_micro) / dose_mesh.volumes[0, 0, 0]

with openmc.StatePoint(gamma_sp) as sp:
    photon_tally = sp.get_tally(name='shutdown_photon_dose')
    plot_mesh_tally(
        tally=photon_tally, basis='xz', value='mean',
        colorbar_kwargs={'label': 'Decay photon dose [µSv/h]'},
        norm=LogNorm(),
        volume_normalization=False,               # we handle volume in `scale`
        scaling_factor=scale,
    ).figure.savefig('shutdown_dose.png')
```

## Running R2S at each cooling timestep

The loop above uses the last timestep. For a decay-curve dose map, wrap steps 5–7 in a loop over `results[i]` for each post-irradiation step. This is how `task_20/2_unstructured_mesh_R2S_shutdown_dose_rate_several_materials.py` works.

## D1S shortcut (when you can afford the approximation)

If the activation is dominated by a single isotope with a single dominant decay channel (e.g. Fe56 → Mn56 → photons for steel), D1S folds the photon source directly into the neutron transport via `openmc.deplete.d1s.time_correction_factors`. See `tasks/task_11_CSG_shut_down_dose_tallies/4_D1S_*`.

## Cost and when to use VR

R2S photon transport through shielded structures often needs FW-CADIS — see [`variance-reduction.md`](variance-reduction.md). Run the photon pass with weight windows generated against the dose mesh.

## Canonical tasks

`tasks/task_20_CAD_shut_down_dose_rate/`:
- `1_unstructured_mesh_R2S_shutdown_dose_rate.py` — single material, single timestep
- `2_unstructured_mesh_R2S_shutdown_dose_rate_several_materials.py` — multi-material, multiple cooling times

`tasks/task_11_CSG_shut_down_dose_tallies/` — CSG versions including D1S.
