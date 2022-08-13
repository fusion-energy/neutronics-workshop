apt-get --allow-releaseinfo-change update
apt-get update -y
apt-get upgrade -y
conda config --add channels conda-forge
conda config --set channel_priority strict
conda install mamba -y
mamba install gxx -y
mamba install cmake -y
mamba install make -y
mamba install binutils -y
mamba install -c conda-forge dagmc=3.2.2 -y


# git clone --single-branch --branch develop --depth 1 https://github.com/openmc-dev/openmc.git
cd openmc
mkdir build
cd build
cmake -DOPENMC_USE_DAGMC=ON ..
make -j2
make -j2 install
cd ..
pip install .
pip install openmc_data_downloader
openmc_data_downloader -l TENDL-2019 -e H C O Na Mg Al Si K Ca Fe