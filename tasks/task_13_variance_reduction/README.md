Varience reduction examples

Currently OpenMC supports two types of variance reduction.
A detailed description of each method can be found in the [documentation](https://docs.openmc.org/en/stable/methods/neutron_physics.html?highlight=survival#variance-reduction-techniques).

The workshop contains the following variance reduction examples:

| Filename | variance reduction technique | geometry | mesh type |
|---|---|---|---|
| 1_shielded_room_survival_biasing.py | survival_biasing | shielded bunker | RegularMesh | Flux map | air space and concrete |
| 2_shielded_room_single_ww.ipynb | weight windows | sphere | RegularMesh | air space and concrete |
| 3_sphere_iterative_per_run_ww.py | weight windows | cube | RegularMesh | Water |
| 4_sphere_iterative_per_batch_ww.py | weight windows | sphere | SphericalMesh | concrete |