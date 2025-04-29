# Introduction

This section contains tasks on converting CAD geometry to DAGMC neutronics.

Examples show how to convert CAD files (e.g. STEP files) and in memory CAD objects into both surface meshed DAGMC geometry and volume meshed neutronics geometry.

Background reading recommendations [DAGMC](https://svalinn.github.io/DAGMC/), [Gmsh](https://gmsh.info/) and [cad-to-dagmc](https://github.com/fusion-energy/cad_to_dagmc).

To convert a CAD geometry generally speaking we require clean CAD that can be meshed. To convert the mesh to a DAGMC geometry we also benefit from imprinting and merging shared surfaces. This accelerates the particle transport stage of the simulation.

There are various efforts to compare simulation results of CAD geometry with CSG (Constructive Solid Geometry) so we can have confidence the two geometry representations give the same result. Care should be taken to provide a fine enough mesh to ensure the results are alike.

Benchmark efforts include:
- [model benchmark zoo](https://github.com/fusion-energy/model_benchmark_zoo)
todo add to this list with other benchmarks (pull requests welcome)