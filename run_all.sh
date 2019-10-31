bash clean_up_directory.sh 

unzip -o model.zip

python3 resave_step_files.py

csg2csg -i materials.serp -f serpent -d -o openmc

mv openmc/materials.xml .
# trelis make_faceted_geometry_with_materials.py

trelis -batch -nographics make_faceted_geometry_with_materials.py 

make_watertight dagmc_notwatertight.h5m -o dagmc_watertight.h5m

build_obb dagmc_without_obb.h5m -o dagmc.h5m

mbconvert dagmc.h5m dagmc.stl

mbconvert dagmc.h5m dagmc.vtk

python3 perform_CAD_neutronics_simulations.py

openmc

python3 get_results.py





# bash Dockerfile.sh

