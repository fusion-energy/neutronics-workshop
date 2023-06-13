Varience reduction examples

Currently OpenMC supports two types of variance reduction.
A detailed description of each method can be found in the [documentation](https://docs.openmc.org/en/stable/methods/neutron_physics.html?highlight=survival#variance-reduction-techniques).

The workshop contains the following variance reduction examples:

| Filename | variance reduction technique | geometry | mesh type |
|---|---|---|---|
| shielded_room_survival_biasing.py | survival_biasing | shielded bunker | RegularMesh |
| generate_single_ww_and_apply.ipynb | weight windows | sphere | SphericalMesh |
| iterative_spherical_mesh_weight_windows.py | weight windows | sphere | SphericalMesh |
| batch_by_batch_till_tally_convergence_limit.py | weight windows | sphere | SphericalMesh |