
# install openmc with dagmc embree and double down into a new conda enviroment
# packages are compiled in this install script using all available CPU cores.
# to reduce the core usage to 2 replace -j commands with -j2


sudo apt-get --yes update
sudo apt-get --yes upgrade


# install dependancies
# needed for embree
sudo apt-get install libglfw3
# needed for embree
sudo apt-get install -y libglfw3-dev
# needed for moab compile
sudo apt-get install -y libopenblas-dev
# needed for openmc compile
sudo apt-get install -y libpng-dev
sudo apt-get install -y libeigen3-dev
sudo apt-get install -y git
sudo apt-get install -y wget
sudo apt-get install -y gfortran
sudo apt-get install -y g++
sudo apt-get install -y mpich
sudo apt-get install -y libmpich-dev
sudo apt-get install -y libhdf5-serial-dev
sudo apt-get install -y libhdf5-mpich-dev
sudo apt-get install -y hdf5-tools
sudo apt-get install -y imagemagick
sudo apt-get install -y cmake
sudo apt-get install -y libeigen3-dev
sudo apt-get install -y libnetcdf-dev
sudo apt-get install -y libtbb-dev
sudo apt-get install -y libgles2-mesa-dev

# install conda, creates new python enviroment and activates it
cd ~

wget -O Miniforge3.sh "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3.sh -b -p "${HOME}/conda"
source "${HOME}/conda/etc/profile.d/conda.sh"
source "${HOME}/conda/etc/profile.d/mamba.sh"
mamba create --name openmc-dagmc python=3.10
mamba activate openmc-dagmc

# install python dependancies
mamba install -y -c conda-forge numpy cython


# install openmc with dagmc embree and double down
# packages are compiled in this install script using all available CPU cores.


sudo apt-get --yes update
sudo apt-get --yes upgrade

export PREFIX=$HOME/opt/openmc-embree/
mkdir -p $PREFIX

# installs embree
cd $PREFIX
mkdir embree
cd embree
git clone --shallow-submodules --single-branch --branch v3.12.2 --depth 1 https://github.com/embree/embree.git
mkdir build
mkdir install
cd build
cmake $PREFIX/embree/embree -DCMAKE_INSTALL_PREFIX=$PREFIX/embree/install \
                            -DCMAKE_BUILD_TYPE=Release \
                            -DEMBREE_ISPC_SUPPORT=OFF \
                            -DEMBREE_TUTORIALS=OFF \
                            -DEMBREE_TUTORIALS_GLFW=OFF
cmake --build . --parallel 32
cmake --install .

# install moab and pymoab
cd $PREFIX
mkdir MOAB
cd MOAB
git clone --single-branch -b 5.5.1 --depth 1 https://bitbucket.org/fathomteam/moab/
mkdir build
mkdir install 
cd build
cmake $PREFIX/MOAB/moab -DCMAKE_INSTALL_PREFIX=$PREFIX/MOAB/install \
                        -DCMAKE_BUILD_TYPE=Release \
                        -DENABLE_PYMOAB=ON \
                        -DENABLE_HDF5=ON \
                        -DENABLE_BLASLAPACK=OFF \
                        -DENABLE_FORTRAN=OFF \
                        -DENABLE_METIS=ON \
                        -DENABLE_MPI=ON \
                        -DENABLE_NETCDF=ON \
                        -DENABLE_PARMETIS=ON \
                        -DENABLE_PNETCDF=OFF

cmake --build . --parallel 32
cmake --install .


# add to new dirs to the path
echo 'export PREFIX="$HOME/opt/openmc-embree/"' >> $PREFIX/setenv.sh
echo 'export PATH="$PREFIX/MOAB/install/bin:$PATH"'  >> $PREFIX/setenv.sh
echo 'export LD_LIBRARY_PATH="$PREFIX/MOAB/install/lib:$LD_LIBRARY_PATH"'  >>  $PREFIX/setenv.sh
echo 'export PYTHONPATH="$PREFIX/MOAB/install/local/lib/python3.10/dist-packages/:$PYTHONPATH"'  >>  $PREFIX/setenv.sh
source $PREFIX/setenv.sh

# install Double-Down
cd $PREFIX
mkdir double-down
cd double-down
git clone --shallow-submodules --single-branch --branch v1.1.0 --depth 1 https://github.com/pshriwise/double-down.git
cd double-down
mkdir build
mkdir install 
cd build
cmake $PREFIX/double-down/double-down -DCMAKE_INSTALL_PREFIX=$PREFIX/double-down/install \
                                      -DCMAKE_BUILD_TYPE=Release \
                                      -DMOAB_DIR=$PREFIX/MOAB/install \
                                      -DEMBREE_DIR=$PREFIX/embree/install
cmake --build . --parallel 32
cmake --install .

# DAGMC version develop install from source
cd $PREFIX
mkdir DAGMC
cd DAGMC
git clone --single-branch --branch v3.2.3 --depth 1 https://github.com/svalinn/DAGMC.git
mkdir build
mkdir install
cd build
# it's suspicious that we need to specify libpthread.so...
cmake $PREFIX/DAGMC/DAGMC -DCMAKE_INSTALL_PREFIX=$PREFIX/DAGMC/install \
                          -DCMAKE_BUILD_TYPE=Release \
                          -DBUILD_TALLY=ON \
                          -DBUILD_TESTS=OFF \
                          -DBUILD_EXE=OFF \
                          -DBUILD_BUILD_OBB=OFF \
                          -DMOAB_DIR=$PREFIX/MOAB/install \
                          -DDOUBLE_DOWN=ON \
                          -DDOUBLE_DOWN_DIR=$PREFIX/double-down/install \
                          -DOpenMP_pthread_LIBRARY=/lib/x86_64-linux-gnu/libpthread.so.0 \
                          -DBUILD_STATIC_EXE=OFF \
                          -DBUILD_STATIC_LIBS=OFF
cmake --build . --parallel 32
cmake --install .

# add to new dirs to the path
echo 'export PATH="$PREFIX/DAGMC/install/bin:$PATH"'  >> $PREFIX/setenv.sh
echo 'export LD_LIBRARY_PATH="$PREFIX/DAGMC/install/lib:$LD_LIBRARY_PATH"'  >>  $PREFIX/setenv.sh
source $PREFIX/setenv.sh

# installs OpenMC
cd $PREFIX
mkdir openmc
cd openmc
git clone --single-branch --branch develop --depth 1 https://github.com/openmc-dev/openmc.git
mkdir build
mkdir install
cd build
cmake $PREFIX/openmc/openmc -DCMAKE_INSTALL_PREFIX=$PREFIX/openmc/install \
                            -DCMAKE_BUILD_TYPE=Release \
                            -DOPENMC_USE_DAGMC=ON \
                            -DDAGMC_ROOT=$PREFIX/DAGMC/install \
                            -DOPENMC_USE_MPI=ON \
                            -DHDF5_PREFER_PARALLEL=ON \
                            -DCPP20=ON \
                            -DBUILD_TESTING=OFF \
                            -DXTENSOR_USE_TBB=OFF \
                            -DXTENSOR_USE_OPENMP=ON \
                            -DXTENSOR_USE_XSIMD=OFF

cmake --build . --parallel 32
cmake --install .
cd $PREFIX/openmc/openmc
python -m pip install . --prefix=$PREFIX/openmc/install

echo 'export PATH="$PREFIX/openmc/install/bin:$PATH"'  >> $PREFIX/setenv.sh
echo 'export PYTHONPATH="$PREFIX/openmc/install/local/lib/python3.10/dist-packages/:$PYTHONPATH"'  >>  $PREFIX/setenv.sh
# install WMP nuclear data
RUN wget https://github.com/mit-crpg/WMP_Library/releases/download/v1.1/WMP_Library_v1.1.tar.gz
tar -xf WMP_Library_v1.1.tar.gz -C

# installs TENDL and ENDF nuclear data. Performed after openmc install as
# openmc is needed to write the cross_Sections.xml file
pip install openmc_data_downloader 
openmc_data_downloader -d nuclear_data -l ENDFB-7.1-NNDC TENDL-2019 -p neutron photon -e all -i H3 --no-overwrite
