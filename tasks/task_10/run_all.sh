

# rm -r  manifest_processed
# part of a package that is not currently opensource, this produces the brep file below
# geomPipeline.py manifest.json

rm dagmc_notwatertight.h5m
# -t is the mesh tolerance
occ_faceter manifest_processed/manifest_processed.brep -t 0.0001 -o dagmc_notwatertight.h5m

rm dagmc.h5m
make_watertight dagmc_notwatertight.h5m -o dagmc.h5m

# optional stl for visualization
mbconvert dagmc.h5m dagmc.stl

# optional vtk for visualization
mbconvert dagmc.h5m dagmc.vtk

python example_CAD_simulation.py
