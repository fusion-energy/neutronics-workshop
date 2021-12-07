
## Task 1 - Cross sections

Please allow 30 minutes for this task.

Expected outputs from this task are also in the [presentation](https://slides.com/neutronics_workshop/neutronics_workshop#/13.

In this task you will be using OpenMC, DAGMC to perform neutronics simulations
on 2D meshes and 3D meshes.

The results will processed into VTK files and png images depending on the part.

- part 1 creates a 3D mesh tally of a CAD geometry made from shapes and exports it in VTK format
- part 2 creates a 2D mesh tally of a CAD geometry made from components and exports it in VTK format
- part 3 creates a 2D mesh tally of a CAD geometry made from components and exports it in as a PNG image along with a slice of the geometry


**Learning Outcomes**

- Mesh tallies can obtain spatial response throughout the geometry   
- 3D and 2D spatial maps can be made
- The bounding box of DAGMC geometry can be found using
- How to convert 2D and 3D mesh tallies to VTK files using [openmc_mesh_tally_to_vtk](https://github.com/fusion-energy/openmc_mesh_tally_to_vtk)
- How to process 2D mesh tallies into images using [regular_mesh_plotter](https://github.com/fusion-energy/regular_mesh_plotter)
- How to make sliced images of DAGMC geometry using [dagmc_geometry_slice_plotter](https://github.com/fusion-energy/dagmc_geometry_slice_plotter)
