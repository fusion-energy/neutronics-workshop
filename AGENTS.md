# AGENTS.md — Fusion Neutronics with OpenMC

Agent-oriented guide for writing **fusion neutronics** simulations with OpenMC and the surrounding CAD/DAGMC/paramak ecosystem. This repo is a living catalogue of patterns for fixed-source DT simulations, activation/depletion, dose, and shutdown dose rate — see `tasks/task_XX_*` for worked examples.

**Fusion-first defaults, not fission-first.** Simulations here are almost always `run_mode='fixed source'` with a 14 MeV DT source (or a plasma-shaped source), not eigenvalue. Depletion is driven by `source_rates` (n/s), not reactor power. When in doubt, prefer `openmc.deplete.IndependentOperator` (transport once, then pure Bateman) over `CoupledOperator` (re-transports every step) — fusion spectra vary slowly with burnup so the independent operator is usually accurate enough and much faster.

## When to use this guide

Load this when the user wants to:
- Write or debug an **OpenMC** simulation (materials, geometry, sources, tallies, `model.run()`)
- Build CAD geometry with **paramak** (parametric fusion reactors) or **cadquery** (scripted CAD)
- Convert CAD to **DAGMC** via `cad_to_dagmc` and use it inside OpenMC (`DAGMCUniverse`)
- Run **depletion / activation / transmutation** with `openmc.deplete` or `Material.deplete()`
- Compute **dose** (instantaneous ICRP, shutdown, R2S)
- Set up **variance reduction** (weight windows, FW-CADIS)

Topics like tritium breeding ratio (TBR), damage (DPA), neutron wall loading, and spectra tallies all fall under this guide — they are just specialised tally setups.

## First things an agent should check

Before writing any OpenMC script, verify these two requirements:

1. **OpenMC is installed.** If not, see `docs/agents/install-and-data.md`. The workshop installs via a custom wheel index (`--extra-index-url https://shimwell.github.io/wheels`) so that `openmc` comes pre-built with DAGMC support.
2. **Nuclear data is available.** OpenMC needs `cross_sections.xml`. Depletion additionally needs a `chain_file`. Check for either the env var `OPENMC_CROSS_SECTIONS` or a `cross_sections.xml` under `~/nuclear_data/`. If neither exists, install `openmc_data` and run `download_chain` — see `docs/agents/install-and-data.md`.

Every script should set these once at the top:

```python
import openmc
from pathlib import Path
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'
openmc.config['chain_file']     = Path.home() / 'nuclear_data' / 'chain-endf-b8.0.xml'  # only if depleting
```

(Or rely on the `OPENMC_CROSS_SECTIONS` / `OPENMC_CHAIN_FILE` env vars.)

## Reference files — load on demand

All live under `docs/agents/`. Read the ones relevant to the task at hand; do not bulk-load.

| File | When to read |
|---|---|
| [`install-and-data.md`](docs/agents/install-and-data.md) | Installing OpenMC, DAGMC, paramak, cad-to-dagmc; downloading nuclear data |
| [`materials.md`](docs/agents/materials.md) | Building `openmc.Material` — isotopes, elements, enrichment, mixing, `neutronics_material_maker` |
| [`csg-geometry.md`](docs/agents/csg-geometry.md) | Building CSG geometry — surfaces, regions, cells, boundary types |
| [`cad-geometry.md`](docs/agents/cad-geometry.md) | CAD geometry via `cadquery` and `paramak`; converting to DAGMC with `cad_to_dagmc`; using `DAGMCUniverse` in OpenMC |
| [`sources.md`](docs/agents/sources.md) | `IndependentSource`, point/ring/mesh sources, plasma sources via `openmc-plasma-source`, plotting with `openmc_source_plotter` |
| [`tallies.md`](docs/agents/tallies.md) | Cell / mesh / spectrum / surface tallies, filters, `get_pandas_dataframe`, `model.run(apply_tally_results=True)` |
| [`depletion-and-activation.md`](docs/agents/depletion-and-activation.md) | `openmc.deplete.CoupledOperator`, `IndependentOperator`, `Material.deplete()`, pulse schedules, activity / decay heat |
| [`dose.md`](docs/agents/dose.md) | `openmc.data.dose_coefficients`, `EnergyFunctionFilter`, surface / mesh dose tallies |
| [`shutdown-dose-rate.md`](docs/agents/shutdown-dose-rate.md) | R2S and D1S workflows combining depletion + photon transport |
| [`variance-reduction.md`](docs/agents/variance-reduction.md) | `WeightWindowGenerator`, iterative WW, FW-CADIS |

Each reference file ends with pointers to the canonical `tasks/task_XX_*` task(s) for deeper worked examples.

## Sanity rules that trip agents up

- **Don't fabricate the OpenMC API.** If unsure whether a class or argument exists, search the installed package (`python -c "import openmc; help(openmc.Material.add_element)"`) rather than guessing. The API is stable but evolving — e.g. `openmc.IndependentSource` replaced the older `openmc.Source` name in recent versions.
- **`model.run()` returns a statepoint path.** The statepoint file is named `statepoint.<batches>.h5`. Prefer `model.run(apply_tally_results=True)` — it runs the simulation AND pulls mean/std-dev into your `Tally` objects in-memory, so you can use `tally.mean` directly without reopening a `StatePoint`.
- **Clean up stale HDF5 files** (`statepoint.*.h5`, `summary.h5`, `*.xml`) before re-running, or OpenMC may read an old file. Idiom:
  ```python
  from pathlib import Path
  for f in Path('.').glob('*.h5'): f.unlink(missing_ok=True)
  ```
- **Depletion requires `material.volume` and `material.depletable = True`** on any material being depleted. Forgetting `volume` silently produces wrong results.
- **DAGMC material tags must match OpenMC material names.** If `dagmc.h5m` has material tag `mat1`, create `openmc.Material(name='mat1')`. Inspect tags with `dag_universe.material_names`.
- **Run mode for fusion is almost always `'fixed source'`**, not `'eigenvalue'`. Fusion has an external source (DT plasma) — there is no fissile critical system.
- **Units**: OpenMC uses **cm** for length, **eV** for energy, **barns** for cross sections, **atoms/b-cm** or **g/cm3** for density. Temperatures default to 293.6 K unless set.

## Testing a change

The tasks under `tasks/` are percent format `.py` files, so they can be run
straight through with `python` or opened as notebooks with jupytext. If the user
is modifying a task, re-run it to confirm. For a new script:

```bash
python my_script.py            # should complete without raising
ls statepoint.*.h5 summary.h5  # confirm outputs exist
```

For the workshop itself, the pytest suite in `tests/` executes every task headlessly, which is long but authoritative.

## Canonical references

- OpenMC docs: https://docs.openmc.org
- OpenMC data page (cross-section and chain downloads): https://openmc.org/data/
- `openmc_data` package (download scripts): https://github.com/openmc-data-storage/openmc_data
- `openmc_data_downloader`: https://github.com/openmc-data-storage/openmc_data_downloader
- `cad_to_dagmc`: https://github.com/fusion-energy/cad_to_dagmc
- `paramak`: https://github.com/fusion-energy/paramak
- DAGMC: https://svalinn.github.io/DAGMC/
