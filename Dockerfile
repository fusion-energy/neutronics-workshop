# build with the following command
# sudo docker build -t workshop_jupyter .

# run with the following command
# docker run -p 8888:8888 workshop_jupyter

# test with the folowing command
# sudo docker run --rm workshop_jupyter pytest ../tests

FROM jupyter/minimal-notebook

# this is required to install programs on the base image
USER root

RUN apt-get --yes update && apt-get --yes upgrade

# required pacakges identified from openmc travis.yml
RUN apt-get --yes install mpich
RUN apt-get --yes install libmpich-dev
RUN apt-get --yes install libhdf5-serial-dev
RUN apt-get --yes install libhdf5-mpich-dev
RUN apt-get --yes install libblas-dev
RUN apt-get --yes install liblapack-dev

# needed to allow NETCDF on MOAB which helps with tet meshes in OpenMC
RUN apt-get --yes install libnetcdf-dev
# RUN apt-get --yes install libnetcdf13
# eigen3 needed for DAGMC
RUN apt-get --yes install libeigen3-dev


RUN apt-get -y install sudo #  needed as the install NJOY script has a sudo make install command
RUN apt-get -y install git


# dependancies used in the workshop
RUN apt-get --yes install imagemagick
RUN apt-get --yes install hdf5-tools
RUN apt-get --yes install wget

USER $NB_USER

RUN pip install cmake
RUN pip install pytest


# MOAB Variables
ENV MOAB_INSTALL_DIR=$HOME/MOAB/


# DAGMC Variables
ENV DAGMC_INSTALL_DIR=$HOME/DAGMC/

# MOAB Install
RUN cd $HOME && \
    mkdir MOAB && \
    cd MOAB && \
    git clone  --single-branch --branch Version5.1.0 https://bitbucket.org/fathomteam/moab/  && \
    mkdir build && cd build && \
    cmake ../moab -DENABLE_HDF5=ON -DENABLE_MPI=off -DENABLE_NETCDF=ON -DBUILD_SHARED_LIBS=ON -DCMAKE_INSTALL_PREFIX=$MOAB_INSTALL_DIR && \
    make -j8 &&  \
    make -j8 install  && \
    cmake ../moab -DBUILD_SHARED_LIBS=OFF && \
    make -j8 install && \
    rm -rf $HOME/MOAB/moab $HOME/MOAB/build

# DAGMC Install
RUN cd $HOME && \
    mkdir DAGMC && cd DAGMC && \
    git clone --single-branch --branch develop https://github.com/svalinn/dagmc && \
    mkdir build && \
    cd build && \
    cmake ../dagmc -DBUILD_TALLY=ON -DCMAKE_INSTALL_PREFIX=$DAGMC_INSTALL_DIR -DMOAB_DIR=$MOAB_INSTALL_DIR && \
    make -j8 install && \
    rm -rf $HOME/DAGMC/dagmc $HOME/DAGMC/build


# check if this is still neeeded
RUN pip install --upgrade numpy

# /opt folder is owned by root
USER root

# installs OpenMc from source
RUN cd /opt && \
    git clone --single-branch --branch develop https://github.com/openmc-dev/openmc.git && \
    cd openmc && \
    mkdir build && \
    cd build && \
    cmake -Ddagmc=ON -DDAGMC_ROOT=$DAGMC_INSTALL_DIR -DHDF5_PREFER_PARALLEL=OFF ..  && \
    make -j8 && \
    make install && \ 
    cd /opt/openmc/ && \
    pip install .

# Clone and install NJOY2016
RUN git clone https://github.com/njoy/NJOY2016 && \
    cd NJOY2016 && \
    mkdir build && \
    cd build && \
    cmake -Dstatic=on .. && \
    make 2>/dev/null && \
    sudo make install

ENV OPENMC_CROSS_SECTIONS=$HOME/nndc_hdf5/cross_sections.xml
ENV LD_LIBRARY_PATH=$HOME/MOAB/lib:$HOME/DAGMC/lib
ENV PATH=$PATH:$HOME/NJOY2016/build



# install endf nuclear data

# clone data repository
RUN git clone https://github.com/openmc-dev/data.git

# run script that converts ACE data to hdf5 data
RUN python3 data/convert_nndc71.py --cleanup && \
    rm -rf nndc-b7.1-endf  && \
    rm -rf nndc-b7.1-ace/  && \
    rm -rf nndc-b7.1-download

RUN wget https://github.com/mit-crpg/WMP_Library/releases/download/v1.1/WMP_Library_v1.1.tar.gz
RUN tar -xf WMP_Library_v1.1.tar.gz -C /
# Python libraries used in the workshop
RUN pip install plotly
RUN pip install tqdm
RUN pip install ghalton==0.6.1
RUN pip install noisyopt
RUN pip install scikit-optimize
RUN pip install inference-tools
RUN pip install adaptive
RUN pip install vtk
RUN pip install itkwidgets
RUN pip install nest_asyncio
RUN pip install neutronics_material_maker
RUN pip install parametric-plasma-source


ENV OPENMC_CROSS_SECTIONS=/nndc-b7.1-hdf5/cross_sections.xml
USER $NB_USER


# Copy over the tasks
COPY tasks tasks/

RUN echo copying over test files

COPY tests tests/


USER root
RUN ln -s /home/jovyan/nndc-b7.1-hdf5 /nndc-b7.1-hdf5

WORKDIR tasks
