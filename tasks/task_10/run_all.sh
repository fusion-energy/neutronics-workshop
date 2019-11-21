trelis -batch -nographics make_faceted_geometry_with_materials.py 

make_watertight dagmc_notwatertight.h5m -o dagmc_watertight.h5m

build_obb dagmc_watertight.h5m -o dagmc.h5m

mbconvert dagmc.h5m dagmc.stl

mbconvert dagmc.h5m dagmc.vtk

python3 example_CAD_simulations.py