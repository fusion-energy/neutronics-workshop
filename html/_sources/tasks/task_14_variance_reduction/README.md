# Task Introduction

Currently OpenMC supports two types of variance reduction (survival biasing and weight windows).
A detailed description of each method can be found in the [documentation](https://docs.openmc.org/en/stable/methods/neutron_physics.html?highlight=survival#variance-reduction-techniques).

OpenMC also supports methods of generating weight windows including the [Magic Method and FW-CADIS](https://docs.openmc.org/en/stable/methods/variance_reduction.html?highlight=magic)

The notebooks contain all the methods for completeness, however ff you just have time to learn one method then I would recommend the FW-CADIS approach.

The workshop contains the following variance reduction examples:

| Filename | variance reduction technique | geometry | mesh type |
|---|---|---|---|
| 1_shielded_room_survival_biasing.py | survival_biasing | shielded bunker | RegularMesh | Flux map | air space and concrete |
| 2_shielded_room_single_ww.ipynb | weight windows | sphere | RegularMesh | air space and concrete |
| 3_sphere_iterative_per_run_ww.py | weight windows | cube | RegularMesh | Water |
| 4_sphere_iterative_per_batch_ww.py | weight windows | sphere | SphericalMesh | concrete |
| 5_shielded_room_single_fw_cadis.py | survival_biasing | shielded bunker | RegularMesh | Flux map | air space and concrete |