# Task Introduction

Variance reduction techniques are essential for efficiently simulating deep-penetration shielding problems where analogue Monte Carlo would require prohibitively many particles. In this task you will use OpenMC to apply survival biasing, weight windows and both global and local FW-CADIS to shielding and sphere problems.

A detailed description of each method can be found in the [OpenMC documentation](https://docs.openmc.org/en/stable/methods/neutron_physics.html?highlight=survival#variance-reduction-techniques). OpenMC also supports methods of generating weight windows including the [Magic Method and FW-CADIS](https://docs.openmc.org/en/stable/methods/variance_reduction.html?highlight=magic).

The examples cover all methods for completeness, however if you only have time to learn one method then the FW-CADIS approach is recommended.

**Learning Outcomes**

- Survival biasing prevents particles from being killed by absorption, instead reducing their weight, which improves statistics in deep-penetration problems.
- Weight windows control particle weights across the geometry, splitting particles in important regions and killing them in unimportant regions.
- Weight windows can be generated iteratively (per-run or per-batch) using the Magic method.
- FW-CADIS (Forward-Weighted Consistent Adjoint Driven Importance Sampling) automates weight window generation using an adjoint flux calculation.
- FW-CADIS weight windows can be global (uniform statistics everywhere) or local (optimised for specific target tallies).