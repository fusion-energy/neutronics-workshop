
sudo apt-get --yes update && sudo apt-get --yes upgrade 
sudo apt-get update

sudo apt-get install --yes wget

# Miniconda

# wget https://repo.anaconda.com/miniconda/Miniconda3-py37_4.8.3-Linux-x86_64.sh
# bash Miniconda3-py37_4.8.3-Linux-x86_64.sh
# conda init
# conda create -y --name cq
# conda activate cq
# conda clean --all
# conda install -c conda-forge -c python python=3.7.8
# conda clean --all
# conda install -c conda-forge -c cadquery cadquery=2

sudo apt-get --yes update && sudo apt-get --yes upgrade
sudo apt-get update

sudo apt-get --yes install gfortran g++ cmake libhdf5-dev
sudo apt-get --yes install python3 python3-pip python3-dev python3-tk
sudo apt-get --yes install imagemagick hdf5-tools paraview eog libsilo-dev git
sudo apt-get --yes install dpkg libxkbfile1 -f libblas-dev liblapack-dev
sudo apt-get --yes install libeigen3-dev libnetcdf-dev libnetcdf13

sudo apt remove -y cmake 
pip3 install cmake

pip3 install numpy pandas six h5py Matplotlib uncertainties lxml scipy cython vtk pytest
pip3 install codecov pytest-cov pylint plotly tqdm pyside2 ghalton==0.6.1 cython
# pip3 install neutronics_material_maker

cd ~
git clone https://github.com/njoy/NJOY2016
cd NJOY2016
mkdir build
cd build
cmake -Dstatic=on .. && make 2>/dev/null
sudo make install

MOAB_INSTALL_DIR=$HOME/MOAB
echo 'export MOAB_INSTALL_DIR=$HOME/MOAB' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=$MOAB_INSTALL_DIR/lib:$LD_LIBRARY_PATH' >> ~/.bashrc

cd ~
mkdir MOAB
cd MOAB
git clone -b develop https://bitbucket.org/fathomteam/moab/
mkdir build
cd build
# this installs without netcdf but with pymoab
#cmake ../moab -DENABLE_HDF5=ON -DBUILD_SHARED_LIBS=ON -DCMAKE_INSTALL_PREFIX=$MOAB_INSTALL_DIR -DENABLE_PYMOAB=ON
# this installs with netcdf but without pymoab
cmake ../moab -DENABLE_HDF5=ON -DENABLE_MPI=off -DENABLE_NETCDF=ON -DBUILD_SHARED_LIBS=ON -DCMAKE_INSTALL_PREFIX=$MOAB_INSTALL_DIR
make -j2 
make -j install
# this 2nd build is required which is a shame
# this is to be used if you want pymoab
# cmake ../moab -DBUILD_SHARED_LIBS=OFF
# otherwise if you want netcdf
cmake ../moab -DBUILD_SHARED_LIBS=OFF
make -j install

LD_LIBRARY_PATH=$MOAB_INSTALL_DIR/lib:$LD_LIBRARY_PATH
echo 'export PATH=$PATH:~/MOAB/bin' >> ~/.bashrc

# Download build_embree.sh script
# Add to $HOME folder
# sudo chmod +x build_embree.sh
# MOAB_DIR=~/MOAB OPENMC_INSTALL_DIR=~ ./build_embree.sh

# check LD_LIBRARY_PATH for dagmc and things