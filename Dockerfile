# build with the following command
# sudo docker build -f Dockerfile_workshop_jupyter -t openmcworkshop/workshop_jupyter . --no-cache
# docker run -p 8888:8888 openmcworkshop/workshop_jupyter


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
RUN apt-get --yes install libnetcdf13


RUN apt-get -y install sudo #  needed as the install NJOY script has a sudo make install command
RUN apt-get -y install git

# dependancies for the occ_faceter
RUN apt-get --yes update && apt-get --yes upgrade
RUN apt-get --yes install libcgal-dev
RUN apt-get --yes install software-properties-common
RUN add-apt-repository ppa:freecad-maintainers/freecad-stable
RUN apt-get --yes install libocc*dev
RUN apt-get --yes install occ*
RUN apt-get --yes install libtbb-dev

# dependancies used in the workshop
RUN apt-get --yes install imagemagick
RUN apt-get --yes install hdf5-tools
RUN apt-get --yes install wget

USER $NB_USER

RUN pip install cmake==3.12.0

#RUN git clone https://github.com/ukaea/openmc_workshop


#ENV DAGMC_DIR=$HOME/DAGMC/
# MOAB Variables
ENV MOAB_BRANCH='Version5.1.0'
ENV MOAB_REPO='https://bitbucket.org/fathomteam/moab/'
ENV MOAB_INSTALL_DIR=$HOME/MOAB/

# DAGMC Variables
ENV DAGMC_BRANCH='develop'
ENV DAGMC_REPO='https://github.com/svalinn/dagmc'
ENV DAGMC_INSTALL_DIR=$HOME/DAGMC/

# MOAB Install
RUN cd $HOME && \
    mkdir MOAB && \
    cd MOAB && \
    git clone -b $MOAB_BRANCH $MOAB_REPO  && \
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
    git clone -b $DAGMC_BRANCH $DAGMC_REPO && \
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
RUN cd /opt &&  git clone https://github.com/openmc-dev/openmc.git
RUN cd /opt/openmc && git checkout develop
RUN cd /opt/openmc && mkdir build
RUN cd /opt/openmc/build && cmake -Ddagmc=ON -DDAGMC_ROOT=$DAGMC_INSTALL_DIR -DHDF5_PREFER_PARALLEL=OFF ..
RUN cd /opt/openmc/build && make -j8 
RUN cd /opt/openmc/build && make install 

RUN cd /opt/openmc/ && python setup.py install


# Clone and install NJOY2016
RUN git clone https://github.com/njoy/NJOY2016
RUN cd NJOY2016 && mkdir build
RUN cd NJOY2016/build/ && cmake -Dstatic=on .. 
RUN cd NJOY2016/build/ && make 2>/dev/null
RUN cd NJOY2016/build/ && sudo make install

ENV OPENMC_CROSS_SECTIONS=$HOME/nndc_hdf5/cross_sections.xml
ENV LD_LIBRARY_PATH=$HOME/MOAB/lib:$HOME/DAGMC/lib
ENV PATH=$PATH:$HOME/NJOY2016/build



# install endf nuclear data

# clone data repository
RUN git clone https://github.com/openmc-dev/data.git

# run script that converts ACE data to hdf5 data
RUN python3 data/convert_nndc71.py --cleanup

# Python libraries used in the workshop
RUN pip install plotly
RUN pip install tqdm
RUN pip install ghalton==0.6.1
RUN pip install noisyopt
RUN pip install scikit-optimize
RUN pip install inference-tools
RUN pip install neutronics_material_maker
RUN pip install adaptive



ENV OPENMC_CROSS_SECTIONS=/nndc-b7.1-hdf5/cross_sections.xml
USER $NB_USER
RUN git clone https://github.com/ukaea/openmc_workshop
RUN cd openmc_workshop && git checkout develop

USER root
RUN ln -s /home/jovyan/nndc-b7.1-hdf5 /nndc-b7.1-hdf5

WORKDIR openmc_workshop
