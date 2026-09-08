# Variance reduction

Deep-penetration fusion problems (dose behind shielding, flux in coils through many mfp) are impossible to resolve with plain analogue Monte Carlo — most particles die before reaching the detector. Use **weight windows** to split particles that move toward the tally region and roulette those that move away. OpenMC provides three routes, from simplest to most powerful.

## Route 1 — single run with in-line weight-window generation

Generate weight windows on the fly as the simulation proceeds. Good for medium-depth problems.

```python
import numpy as np

mesh = openmc.RegularMesh().from_domain(geometry, dimension=(50, 50, 1))

wwg = openmc.WeightWindowGenerator(
    mesh=mesh,
    energy_bounds=np.linspace(0.0, 14.1e6, 10),
    particle_type='neutron',
)

settings.weight_window_generators = wwg
settings.max_history_splits = 1000      # cap on total splits per source particle
settings.particles = 5_000              # you can lower this — each particle does more work
model.run()
```

## Route 2 — iterative weight windows (per-batch updates)

The generator updates the window estimate between batches, so late batches benefit from windows informed by early ones. Better for deep shielding than route 1. See `tasks/task_14_variance_reduction/3_` and `/4_`.

## Route 3 — FW-CADIS (most powerful)

Forward-Weighted CADIS generates **optimal** weight windows for a *specific tally* by running a cheap deterministic-style adjoint first (via OpenMC's random-ray solver), then using that adjoint to weight the forward problem. Handles multi-room, multi-bend geometries that defeat analogue MC entirely.

```python
import copy

# 1. Start with your continuous-energy model (the "real" run)
ce_model = openmc.Model(geometry, materials, settings)

# 2. Make a multigroup copy for the random-ray adjoint
rr_model = copy.deepcopy(ce_model)
rr_model.convert_to_multigroup(
    method='stochastic_slab',         # fast, robust; 'material_wise' is slower but more accurate
    overwrite_mgxs_library=True,
    nparticles=2000,                  # bump up if MG XS look noisy
)
rr_model.convert_to_random_ray()

# 3. Set a mesh for the random-ray source regions AND the weight windows
mesh = openmc.RegularMesh().from_domain(geometry, dimension=(100, 100, 1))
rr_model.settings.random_ray['source_region_meshes'] = [(mesh, [rr_model.geometry.root_universe])]

rr_model.settings.weight_window_generators = openmc.WeightWindowGenerator(
    method='fw_cadis',
    mesh=mesh,
)

rr_model.run()                        # produces weight_windows.h5

# 4. Load the windows into the real CE model
weight_windows = openmc.hdf5_to_wws('weight_windows.h5')

ce_model.settings.weight_windows = weight_windows
ce_model.settings.weight_window_checkpoints = {'collision': True, 'surface': True}
ce_model.settings.survival_biasing = False
ce_model.run()
```

The random-ray adjoint pass is typically 10–100× cheaper than a single CE batch, so the overhead is tiny versus the huge convergence speedup on the actual tally.

## Survival biasing — the quick-and-dirty baseline

One-liner, no mesh needed, crude but free:

```python
settings.survival_biasing = True
```

Use this for medium-depth problems where you just want "good enough" faster. Turn it off when using weight windows (the two mechanisms interfere).

## Choosing a variance-reduction strategy

| Problem | Start with |
|---|---|
| Few-mfp shielding, want flux in bulk | Analogue, 10⁷+ particles |
| Dose at one point behind 1–2 m concrete | Weight windows route 1 or 2 |
| Dose map through a shielded room with a labyrinth | FW-CADIS |
| Tritium breeding in a breeder blanket | Analogue — neutrons are abundant, no VR needed |
| Activation flux in TF coils | Weight windows route 2 |
| Shutdown dose map after a pulse | FW-CADIS on the photon model |

## Loading / saving weight windows

```python
# save (automatic when a WWG is set)
# load
ww = openmc.hdf5_to_wws('weight_windows.h5')        # list of WeightWindow objects
settings.weight_windows = ww
settings.weight_windows_on = True                   # default when set; flip off to compare
```

## Inspecting weight windows

```python
from matplotlib.colors import LogNorm
lower = ww[0].lower_ww_bounds.squeeze().T
plt.imshow(lower, origin='lower', extent=mesh.bounding_box.extent['xy'], norm=LogNorm())
```

A well-formed set of windows shows smooth gradients from source toward the tally. Sharp edges or zeros mean the underlying adjoint didn't converge in that region — increase `nparticles` on the random-ray pass.

## Canonical tasks

`tasks/task_14_variance_reduction/`:
1. Survival biasing baseline
2. Single-run weight windows
3. Iterative WW (per-run)
4. Iterative WW (per-batch)
5. FW-CADIS — the full pattern shown above
