# Task Introduction

These tasks demonstrate how to make use of DAGMC surface and volume meshes in neutronics simulations.

DAGMC offers two "geometries" although some may consider just the surface mesh as geometry and the volume mesh more of a scoring / tallying mesh.

The DAGMC surface mesh is able to represent volumes by surface meshing their faces with triangles.

DAGMC (via MOAB) also adds tetrahedral volume mesh support to OpenMC and allows for volume meshes to score / tally particles.

The tasks start with the most minimal example of using a DAGMC surface mesh

The tasks then continue with common user needs, namely adding reflective boundary conditions so that sector models can be simulated and combining DAGMC geometry with CSG geometry in a hybrid model.