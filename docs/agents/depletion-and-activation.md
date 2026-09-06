# Depletion & activation

For fusion, "depletion" usually means **activation** — neutron irradiation producing radioactive daughter nuclides, then decay during cooldown. The patterns differ from fission depletion in two ways:

1. **Normalisation is by source rate (n/s)**, not reactor power. Use `normalization_mode='source-rate'`.
2. **Spectra change slowly with burnup** in most fusion problems, so you usually want `IndependentOperator` (transport once, then pure Bateman across many timesteps) rather than `CoupledOperator` (re-transport every step). The independent form is 10–100× faster and accurate enough for activation and shutdown dose.

Prerequisites (every depletion script):

```python
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'
openmc.config['chain_file']     = Path.home() / 'nuclear_data' / 'chain-endf-b8.0.xml'

mat.volume = V_cm3                    # REQUIRED — computes atom counts
mat.depletable = True                 # REQUIRED — marks for depletion
```

See [`install-and-data.md`](install-and-data.md) for chain-file downloads.

## Pattern 1 — single material, pre-computed flux spectrum (`Material.deplete`)

Simplest case: you already know the flux spectrum (e.g. from a FISPACT-style first-wall library, or a prior OpenMC run) and want to deplete one material under it. No transport is run inside `deplete()`.

```python
import openmc
import openmc.deplete
from openmc.mgxs import GROUP_STRUCTURES

HOUR = 3600; DAY = 86400

mat = openmc.Material()
mat.add_element('Fe', 1)
mat.set_density('g/cm3', 7.87)
mat.volume = 1000                     # cm³
mat.depletable = True

# Flux spectrum per LLNL-616 group (values = n/cm²/s per group)
flux_values = [...]
energy_bin_edges = GROUP_STRUCTURES['LLNL-616']   # 617 values

# Optional: reduce the chain to nuclides reachable from the starting material
full_chain = openmc.deplete.Chain.from_xml(openmc.config['chain_file'])
reduced = full_chain.reduce(initial_isotopes=[n.name for n in mat.nuclides], level=3)

timesteps    = [365*DAY] + [30*DAY]*6           # 1 yr irradiation, 6 months cooldown in monthly steps
source_rates = [4.4e14] + [0]*6                 # n/cm²/s during irradiation, 0 during cooling

results = mat.deplete(
    multigroup_flux=flux_values,
    energy_group_structure='LLNL-616',
    timesteps=timesteps,
    source_rates=source_rates,
    timestep_units='s',
    chain_file=reduced,                         # or openmc.config['chain_file']
    reactions=reduced.reactions,
)
# results is a list: [initial_material, after_step_1, after_step_2, ...]
```

Querying results:

```python
for step_mat in results[1:]:
    print(step_mat.get_activity(units='Bq'))
    print(step_mat.get_decay_heat(units='W'))
    print(step_mat.get_photon_contact_dose_rate(dose_quantity='effective'))   # Sv/hr

# Per-nuclide breakdown at shutdown
shutdown = results[1]
by_nuc = shutdown.get_activity(units='Bq', by_nuclide=True)
for nuc, a in sorted(by_nuc.items(), key=lambda x: -x[1])[:10]:
    print(f'{nuc:8} {a:.3e} Bq')

# Mass of a specific nuclide over time
for i, m in enumerate(results[1:]):
    print(times[i], m.get_mass(nuclide='Co60'))
```

## Pattern 2 — `IndependentOperator` (preferred for fusion)

Transport is run once against the full model to get flux and micro XS in each depletable region, then the Bateman equations are solved independently across the pulse schedule. Fast, fine for anything where neutron spectrum doesn't change materially with burnup.

```python
import openmc, openmc.deplete

model = openmc.Model(geometry, materials, settings)    # settings.run_mode='fixed source'

# Step 1: one transport run to get flux + microscopic XS
flux_in_each_group, micro_xs = openmc.deplete.get_microxs_and_flux(
    model=model,
    domains=[cell_to_deplete],                         # or a list of cells / materials
    energies=[0, 30e6],                                # bin edges; 1 bin is fine for most fusion
    chain_file=openmc.config['chain_file'],
)

# Step 2: build the operator
op = openmc.deplete.IndependentOperator(
    materials=materials,
    fluxes=[f[0] for f in flux_in_each_group],
    micros=micro_xs,
    reduce_chain_level=5,                              # aggressive chain pruning — keeps only relevant nuclides
    normalization_mode='source-rate',                  # FUSION: source-rate, not power
)

# Step 3: pulse schedule — list of (duration, source_rate) pairs
schedule = [
    (24*3600, 1e20),    # 1 day irradiation
    (24*3600, 1e20),
    (24*3600, 1e20),
    (24*3600, 0),       # 1 day decay
    (7*24*3600, 0),     # 1 week cooldown
]
timesteps    = [s[0] for s in schedule]
source_rates = [s[1] for s in schedule]

# Step 4: integrate
integrator = openmc.deplete.PredictorIntegrator(
    operator=op, timesteps=timesteps, source_rates=source_rates, timestep_units='s',
)
integrator.integrate()                                 # writes depletion_results.h5

# Step 5: analyse
results = openmc.deplete.Results('depletion_results.h5')
times, atoms_Ag110 = results.get_atoms(mat, 'Ag110')
mat_at_step_2 = results[2].get_material(str(mat.id))
```

Integrator choice: `PredictorIntegrator` is the simplest and fine for most activation work. More accurate alternatives for fast-changing systems: `CECMIntegrator`, `CELIIntegrator`, `CF4Integrator`, `LEQIIntegrator`, `SICELIIntegrator`.

## Pattern 3 — `CoupledOperator` (re-transport each step)

Only needed when the neutron spectrum changes significantly over time — e.g. heavy burn-up of a strong absorber like boron, or when tallies themselves evolve. Slower by a factor of (number of timesteps):

```python
op = openmc.deplete.CoupledOperator(
    model,
    chain_file=openmc.config['chain_file'],
    normalization_mode='source-rate',
    reduce_chain_level=5,
)
integrator = openmc.deplete.PredictorIntegrator(op, timesteps, source_rates, timestep_units='s')
integrator.integrate()
```

For fusion activation, default to `IndependentOperator` unless you have a specific reason.

## Pulse schedules — a practical recipe

Real fusion devices pulse. Build schedules as lists of `(duration_seconds, source_rate_n_per_s)`:

```python
DT_NEUTRONS_PER_MW = 3.55e17                           # n/s per MW of fusion power

fusion_power_MW = 500
src = fusion_power_MW * DT_NEUTRONS_PER_MW             # ~1.775e20 n/s

# 20 × (10 min pulse + 50 min dwell), then 24 h cooldown sampled in 12 log steps
schedule = []
for _ in range(20):
    schedule += [(600, src), (3000, 0)]
schedule += [(3600 * t, 0) for t in [0.1, 0.3, 1, 2, 4, 8, 12, 18, 24]]

timesteps    = [s[0] for s in schedule]
source_rates = [s[1] for s in schedule]
```

A zero `source_rate` for a step is a pure decay step — no neutrons, just Bateman.

## Micro-XS tricks

`get_microxs_and_flux(..., energies=[0, 30e6])` uses one broad energy bin — fastest. For more accurate spectrum-dependent cross sections, use a multi-group structure:

```python
energies = openmc.mgxs.GROUP_STRUCTURES['CCFE-709']
flux, micro = openmc.deplete.get_microxs_and_flux(model, [cell], energies=energies, chain_file=chain)
```

This is mainly worth it for thermal / epithermal problems where resolved resonances matter; for pure-fast DT first-wall spectra, one bin is usually fine.

## Results analysis — full menu

```python
results = openmc.deplete.Results('depletion_results.h5')

# Number of atoms over time
t, atoms = results.get_atoms(mat, 'Co60')

# Activity / decay heat / dose (call on the material from each step)
for step in results:
    m = step.get_material(str(mat.id))
    print(m.get_activity(units='Bq'), m.get_decay_heat(units='W'))

# Reaction rates (if you need them)
t, rates = results.get_reaction_rate(mat, 'Fe56', '(n,p)')

# Keff is only meaningful for fission — ignore for fusion
```

Plot helpers in `openmc_depletion_plotter` — check the package README for the current function names; typical usage is `plot_atoms_vs_time(results, ...)` or similar.

## Shutdown dose rate

Depletion gives you the material composition after cooldown. To compute **dose rate in the surrounding space** you need a second transport pass with the decayed materials emitting photons — see [`shutdown-dose-rate.md`](shutdown-dose-rate.md) (R2S and D1S workflows).

## Common pitfalls

- **Forgot `mat.volume`** → atom counts are zero, everything is wrong silently.
- **Forgot `mat.depletable = True`** → material isn't depleted, results flat.
- **`normalization_mode='energy-deposition'` on a fusion problem** → wrong. Use `'source-rate'`.
- **Re-running without cleaning `depletion_results.h5`** → OpenMC usually overwrites cleanly, but some plotters cache.
- **Chain file too ambitious** → `reduce_chain_level=3` or `5` trims to what's reachable from your starting materials and makes CRAM solves 10–100× faster.
- **Wrong chain for your library** — ENDF/B-VIII.0 chain goes with ENDF/B-VIII.0 cross sections. TENDL chains go with TENDL. Mixing can produce warnings about missing nuclide yields.

## Canonical tasks

`tasks/task_10_activation_transmutation_depletion/`:
- `1_depletion_with_flux_spectra.py` — `Material.deplete()` with pre-computed spectrum
- `2_simple_transmutation_reaction_rate_simulation.py` — reaction rate tallies
- `3_example_transmutation_isotope_build_up.py` — `CoupledOperator`, results extraction
- `4_example_tally_change_with_burnup.py` — coupled case with tally evolution
- `5_full_pulse_schedule.py` — the IndependentOperator pulse-schedule canon
