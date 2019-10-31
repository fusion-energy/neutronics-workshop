
trelis -batch -nographics make_faceted_geometry_with_materials.py 

make_watertight dagmc_notwatertight.h5m 

mv dagmc_notwatertight_zip.h5m dagmc_watertight.h5m

check_watertight dagmc_watertight.h5m

mv dagmc_watertight.h5m dagmc_without_obb.h5m

build_obb dagmc_without_obb.h5m

mv dagmc_without_obb_obb.h5m dagmc.h5m

mbconvert dagmc.h5m dagmc.stl

mbconvert dagmc.h5m dagmc.vtk

python3 example_CAD_simulations.py

