steps2h5m geometry_details.json 1. dagmc_notwatertight.h5m

make_watertight dagmc_notwatertight.h5m -o dagmc.h5m

# the mbconvert commands are optional but it helps if you want to inspect the geometry
mbconvert dagmc.h5m dagmc.stl
mbconvert dagmc.h5m dagmc.vtk

python3 example_CAD_simulation.py
