# Task Introduction

Please allow 20 minutes for this task.

Expected outputs from this task are also in the [presentation](https://slides.com/neutronics_workshop/neutronics_workshop#/15).

In this task you will use OpenMC to simulate transmutation, activation and depletion of materials under neutron irradiation. The examples progress from a simple flux-spectrum-based depletion (no transport required) through to coupled transport-depletion simulations with pulsed irradiation schedules.

**Learning Outcomes**

- OpenMC can perform depletion using a precomputed multigroup flux spectrum, similar to inventory codes like FISPACT, ORIGEN and ALARA. This is fast and requires no geometry.
- OpenMC can also perform coupled transport-depletion where the neutron flux is recalculated as the material composition evolves.
- Activation products build up during irradiation and start to saturate at around five half-lives, when the rate of creation approaches the rate of decay.
- Activity, decay heat and contact dose rate can be extracted from depleted materials.
- Material evolution during irradiation affects tally results. For example, Tritium Breeding Ratio decreases as lithium-6 is burnt up.
- Pulsed irradiation schedules can be modelled to simulate realistic reactor operating conditions.

## Flowing-Liquid Activation

[6_flowing_liquid_activation.ipynb](6_flowing_liquid_activation.ipynb) models
ideal plug flow through an irradiation region into a well-mixed storage pool.
Run the cells in order, editing the material, total irradiated volume, total
flow, transit time, pool inventory and pumping schedule directly. The example
uses 10 cm3 of water, 1 kg/s flow, and a five-second pulse of 1e19 neutrons.

One neutron-transport calculation supplies reaction rates for OpenMC's
activation and decay matrices. Continuous parcel arrivals are integrated with
CRAM, including startup, shutdown and decay during transit. Only liquid that
has reached the pool contributes to its dose. Equivalent parallel branches use
total volume and total flow, without requiring a pipe count. The transport
geometry is a replaceable example, not part of the flow equations.

Use an OpenMC installation supporting material photon contact dose, with
matching neutron and activation data. Configure
the paths in the notebook or use `OPENMC_CROSS_SECTIONS` and `OPENMC_CHAIN_FILE`.
For water, include O16(n,p)N16 and N16 decay-photon data in the chain.

The model assumes constant flow, one rectangular pulse, equivalent branch
exposures and complete pool mixing. It does not infer flow splitting or
exposure histories from geometry, and does not include recirculation or pool
outflow. Those cases require an extended path history or inventory balance.

The result is absorbed-air photon dose in Gy/h using a material slab
approximation, not a finite-tank calculation or a guaranteed conservative bound.
Direct beta, bremsstrahlung and delayed-neutron dose are excluded.