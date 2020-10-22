
sudo apt-get --yes update && sudo apt-get --yes upgrade
sudo apt-get update

sudo apt-get install -y wget bzip2

# Anaconda

cd ~
wget https://repo.anaconda.com/miniconda/Miniconda3-py37_4.8.3-Linux-x86_64.sh
bash Miniconda3-py37_4.8.3-Linux-x86_64.sh -b

# append ~/miniconda3/bin to path
PATH=$PATH:~/miniconda3/bin
echo 'export PATH=$PATH:~/miniconda3/bin' >> ~/.bashrc

# don't know whether need to activate something?

conda install -c conda-forge -c cadquery cadquery=2
conda install gxx_linux-64

sudo apt-get update
sudo apt-get install -y libgl1-mesa-dev 
sudo apt-get install -y libglu1-mesa-dev
sudo apt-get install -y freeglut3-dev
sudo apt-get install -y libosmesa6
sudo apt-get install -y libosmesa6-dev
sudo apt-get install -y libgles2-mesa-dev

# the following commands are needed for pymoab installation
sudo apt-get --yes install mpich
sudo apt-get --yes install libmpich-dev
sudo apt-get --yes install libhdf5-serial-dev
sudo apt-get --yes install libhdf5-mpich-dev
sudo apt-get --yes install libblas-dev
sudo apt-get --yes install liblapack-dev

# needed to allow NETCDF on MOAB which helps with tet meshes in OpenMC
sudo apt-get --yes install libnetcdf-dev
# sudo apt-get --yes install libnetcdf13
# eigen3 needed for DAGMC
sudo apt-get --yes install libeigen3-dev


sudo apt-get -y install git

# dependancies used in the workshop
sudo apt-get --yes install imagemagick
sudo apt-get --yes install hdf5-tools
sudo apt-get --yes install wget


# needed for occ faceter
sudo apt --yes install libhdf5-dev build-essential gfortran autoconf libtool liblapack-dev
sudo apt --yes install libcgal-dev libtbb-dev
sudo apt-get update
# for add-apt-repository
sudo apt-get --yes install software-properties-common
# for occ
sudo add-apt-repository --yes ppa:freecad-maintainers/freecad-stable
sudo apt update

# ENV DEBIAN_FRONTEND=noninteractive
# think this translates to:
# export DEBIAN_FRONTEND=noninteractive

sudo apt-get install --yes libocct*-dev occt*
sudo apt-get install --yes cmake libcgal-dev libtbb-dev

# needed for ppp
sudo add-apt-repository --yes ppa:freecad-maintainers/freecad-stable
sudo apt update
sudo apt-get install --yes freecad
sudo apt-get install --yes libtbb2 libocct-foundation-7.3  libocct-data-exchange-7.3  libocct-modeling-data-7.3 libocct-modeling-algorithms-7.3  libocct-ocaf-7.3

pip install --upgrade numpy
pip install h5py
pip install cython
pip install cmake
sudo apt-get --yes install cmake

# LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/hdf5/serial:$LD_LIBRARY_PATH
echo 'export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/hdf5/serial:$LD_LIBRARY_PATH' >> ~/.bashrc

wget https://github.com/ukaea/parallel-preprocessor/releases/download/dev/parallel-preprocessor-0.3-dev_ubuntu-18.04.deb
dpkg -i parallel-preprocessor-0.3-dev_ubuntu-18.04.deb


# MOAB variables
MOAB_BRANCH='Version5.1.0'
MOAB_REPO='https://bitbucket.org/fathomteam/moab/'
MOAB_INSTALL_DIR=$HOME/MOAB

# MOAB install
cd $HOME
mkdir MOAB
cd MOAB
git clone -b $MOAB_BRANCH $MOAB_REPO
mkdir build
cd build
cmake ../moab -DENABLE_HDF5=ON -DBUILD_SHARED_LIBS=ON -DCMAKE_INSTALL_PREFIX=$MOAB_INSTALL_DIR -DENABLE_PYMOAB=ON
make -j
make -j install

cmake ../moab -DBUILD_SHARED_LIBS=OFF
make -j install

cd pymoab
bash install.sh
python setup.py install
# rm -rf $HOME/MOAB/moab $HOME/MOAB/build   # might be wrong

LD_LIBRARY_PATH=$MOAB_INSTALL_DIR/lib:$LD_LIBRARY_PATH
echo 'export PATH=$PATH:~/MOAB/bin' >> ~/.bashrc

# occ faceter
git clone https://github.com/makeclean/occ_faceter.git
cd occ_faceter
mkdir build
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=..
make -j
make install

PATH=$PATH:$HOME/occ_faceter/bin


# DAGMC Variables
DAGMC_INSTALL_DIR=$HOME/DAGMC/

# DAGMC Install
cd $HOME
mkdir DAGMC
DAGMC
git clone -b develop https://github.com/svalinn/dagmc
mkdir build
cd build
cmake ../dagmc -DBUILD_TALLY=ON -DCMAKE_INSTALL_PREFIX=$DAGMC_INSTALL_DIR -DMOAB_DIR=$MOAB_INSTALL_DIR -DBUILD_STATIC_LIBS=OFF -DBUILD_STATIC_EXE=OFF
make -j install
# rm -rf $HOME/DAGMC/dagmc $HOME/DAGMC/build

LD_LIBRARY_PATH=$DAGMC_INSTALL_DIR/lib:$LD_LIBRARY_PATH
echo 'export PATH=$PATH:~/DAGMC/bin' >> ~/.bashrc


# OpenMC Install, this must be installed to /opt/openmc, `parametric_plasma_source` python module has this path hard-coded
cd /opt
sudo git clone --recurse-submodules https://github.com/openmc-dev/openmc.git
cd /opt/openmc
sudo chmod 777 -R openmc
sudo git checkout develop
sudo mkdir build
sudo chmod 777 build
cd build
cmake -Ddagmc=ON -DDAGMC_ROOT=$DAGMC_INSTALL_DIR ..
# cmake -Ddagmc=ON -Ddebug=on -DDAGMC_ROOT=$DAGMC_INSTALL_DIR ..
sudo make -j
sudo make -j install
cd /opt/openmc/
cd /opt
sudo chmod 777 -R openmc
cd /opt/openmc/
pip install -e .
# setup.py can be used instead but it doesn't appear to install to conda enviroments
# sudo python3 setup.py develop --user


# install NJOY2016
cd ~
git clone https://github.com/njoy/NJOY2016 #/opt/NJOY2016
cd NJOY2016
mkdir build
cd build
cmake -Dstatic=on .. && make 2>/dev/null
sudo make install


# Nuclear data install
cd ~
git clone https://github.com/openmc-dev/data.git
cd data
python3 convert_fendl.py
python3 convert_tendl.py
python3 convert_nndc71.py


OPENMC_CROSS_SECTIONS_NNDC=~/data/nndc-b7.1-hdf5/cross_sections.xml
echo 'export OPENMC_CROSS_SECTIONS_NNDC=~/data/nndc-b7.1-hdf5/cross_sections.xml' >> ~/.bashrc
OPENMC_CROSS_SECTIONS_TENDL=~/data/tendl-2017-hdf5/cross_sections.xml
echo 'export OPENMC_CROSS_SECTIONS_TENDL=~/data/tendl-2019-hdf5/cross_sections.xml' >> ~/.bashrc
OPENMC_CROSS_SECTIONS_FENDL=~/data/fendl-3.1d-hdf5/cross_sections.xml
echo 'export OPENMC_CROSS_SECTIONS_FENDL=~/data/fendl-3.1d-hdf5/cross_sections.xml' >> ~/.bashrc

OPENMC_CROSS_SECTIONS=~/data/tendl-2017-hdf5/cross_sections.xml
echo 'export OPENMC_CROSS_SECTIONS=~/data/tendl-2019-hdf5/cross_sections.xml' >> ~/.bashrc


