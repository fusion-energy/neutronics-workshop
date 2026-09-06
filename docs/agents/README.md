# `docs/agents/` — AI-agent reference files

Focused reference files for coding agents working on fusion neutronics with this workshop. The entry point is [`../../AGENTS.md`](../../AGENTS.md) at the repo root — read that first to choose which file below to load.

| File | Topic |
|---|---|
| [install-and-data.md](install-and-data.md) | Installing OpenMC + ecosystem via the shimwell.github.io wheel index; nuclear data via `openmc_data` / `openmc_data_downloader` / direct download from openmc.org/data |
| [materials.md](materials.md) | `openmc.Material` — isotopes, elements, enrichment, mixing, `neutronics_material_maker` |
| [csg-geometry.md](csg-geometry.md) | CSG surfaces, regions, cells, boundary types; sphere-in-sphere fusion blanket pattern |
| [cad-geometry.md](cad-geometry.md) | `cadquery`, `paramak`, `cad_to_dagmc`, `DAGMCUniverse` |
| [sources.md](sources.md) | `IndependentSource`, DT point / ring / plasma, `openmc_plasma_source.tokamak_source`, source plotting |
| [tallies.md](tallies.md) | Cell / mesh / spectrum / surface tallies, `apply_tally_results=True`, per-nuclide, reshaping |
| [depletion-and-activation.md](depletion-and-activation.md) | `Material.deplete()`, `IndependentOperator`, pulse schedules, `get_microxs_and_flux`, results extraction |
| [dose.md](dose.md) | ICRP dose coefficients, surface / cell / mesh dose tallies |
| [shutdown-dose-rate.md](shutdown-dose-rate.md) | R2S workflow: depletion → decay photon source → photon transport → dose map |
| [variance-reduction.md](variance-reduction.md) | Survival biasing, weight windows, FW-CADIS with the random-ray adjoint |

Each file ends with pointers to the canonical `tasks/task_XX_*` task(s) where the patterns are worked through at full length.
