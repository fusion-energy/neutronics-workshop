# build with the following command, replace the 50 cores with however many you would like to use
# docker build -t ukaea/openmcworkshop --build-arg compile_cores=50 .

# run with the following command
# docker run -p 8888:8888 ukaea/openmcworkshop /bin/bash -c "jupyter notebook --notebook-dir=/tasks --ip='*' --port=8888 --no-browser --allow-root"

# test with the folowing command
# docker run --rm ukaea/openmcworkshop pytest ../tests

FROM continuumio/miniconda3

RUN apt-get --yes update && apt-get --yes upgrade

# required pacakges identified from openmc travis.yml
RUN apt-get --yes install mpich libmpich-dev libhdf5-serial-dev \
                          libhdf5-mpich-dev

# needed to allow NETCDF on MOAB which helps with tet meshes in OpenMC
RUN apt-get --yes install libnetcdf-dev
# RUN apt-get --yes install libnetcdf13

# eigen3 needed for DAGMC
RUN apt-get --yes install libeigen3-dev

# sudo is needed during the NJOY install
RUN apt-get -y install sudo 
RUN apt-get -y install git

# dependancies used in the workshop
RUN apt-get --yes install hdf5-tools
RUN apt-get --yes install wget

# installing cadquery and jupyter
RUN conda install jupyter -y
RUN conda install -c conda-forge -c python python=3.7.8
RUN conda install -c conda-forge -c cadquery cadquery=2
# cadquery master don't appear to show the .solid in the notebook

# new version needed for openmc compile
RUN pip install cmake

# Python libraries used in the workshop
RUN pip install plotly tqdm ghalton==0.6.1 noisyopt scikit-optimize \
                inference-tools adaptive vtk itkwidgets nest_asyncio \
                neutronics_material_maker parametric-plasma-source pytest \
                pytest-cov holoviews ipywidgets

RUN git clone --single-branch --branch develop https://github.com/openmc-dev/openmc.git
RUN git clone https://github.com/njoy/NJOY2016

RUN mkdir DAGMC && \
    cd DAGMC && \
    git clone --single-branch --branch develop https://github.com/svalinn/dagmc

RUN mkdir MOAB && \
    cd MOAB && \
    git clone  --single-branch --branch develop https://bitbucket.org/fathomteam/moab/


# needed for openmc
RUN pip install --upgrade numpy

RUN git clone --single-branch --branch master https://github.com/embree/embree
RUN git clone https://github.com/pshriwise/double-down

# needed for moab
RUN pip install cython

# Install dependencies from Debian package manager
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y \
        wget git gfortran g++ cmake \
        mpich libmpich-dev libhdf5-serial-dev libhdf5-mpich-dev \
        imagemagick && \
    apt-get autoremove

# install addition packages required for DAGMC
RUN apt-get --yes install libeigen3-dev && \
    apt-get --yes install libnetcdf-dev && \
    apt-get --yes install libtbb-dev && \
    apt-get --yes install libglfw3-dev 

# needed for CadQuery functionality
RUN apt-get install -y libgl1-mesa-glx libgl1-mesa-dev libglu1-mesa-dev \
                       freeglut3-dev libosmesa6 libosmesa6-dev \
                       libgles2-mesa-dev && \
                       apt-get clean

RUN git clone  --single-branch --branch develop https://github.com/ukaea/paramak.git && \
    cd paramak && \
    python setup.py install

# RUN pip install paramak

ARG compile_cores=2

# Clone and install Embree
RUN echo git clone --single-branch --branch master https://github.com/embree/embree  && \
    cd embree && \
    mkdir build && \
    cd build && \
    cmake .. -DCMAKE_INSTALL_PREFIX=.. \
             -DEMBREE_ISPC_SUPPORT=OFF && \
    make -j"$compile_cores" && \
    make -j"$compile_cores" install

# Clone and install MOAB
RUN echo git clone  --single-branch --branch develop https://bitbucket.org/fathomteam/moab/ && \
    cd MOAB && \
    mkdir build && \
    cd build && \
    cmake ../moab -DENABLE_HDF5=ON \
        -DENABLE_NETCDF=ON \
        -DENABLE_BLASLAPACK=OFF \
        -DBUILD_SHARED_LIBS=OFF \
        -DENABLE_FORTRAN=OFF \
        -DCMAKE_INSTALL_PREFIX=/MOAB && \
    make -j"$compile_cores" &&  \
    make -j"$compile_cores" install && \
    cmake ../moab -DBUILD_SHARED_LIBS=ON \
        -DENABLE_HDF5=ON \
        -DENABLE_PYMOAB=ON \
        -DENABLE_BLASLAPACK=OFF \
        -DENABLE_FORTRAN=OFF \
        -DCMAKE_INSTALL_PREFIX=/MOAB && \
    make -j"$compile_cores" install && \
    cd pymoab && \
    bash install.sh && \
    python setup.py install


# Clone and install Double-Down
RUN echo git clone https://github.com/pshriwise/double-down && \
    cd double-down && \
    mkdir build && \
    cd build && \
    cmake .. -DCMAKE_INSTALL_PREFIX=.. \
        -DMOAB_DIR=/MOAB \
        -DEMBREE_DIR=/embree/lib/cmake/embree-3.12.1 && \
    make -j"$compile_cores" && \
    make -j"$compile_cores" install


# DAGMC install
# ENV DAGMC_INSTALL_DIR=$HOME/DAGMC/
RUN echo installing dagmc && \
    cd DAGMC && \
    # mkdir DAGMC && cd DAGMC && \
    # git clone --single-branch --branch develop https://github.com/svalinn/dagmc && \
    mkdir build && \
    cd build && \
    cmake ../dagmc -DBUILD_TALLY=ON \
        -DCMAKE_INSTALL_PREFIX=/DAGMC \
        -DMOAB_DIR=/MOAB && \
    make -j"$compile_cores" install && \
    rm -rf /DAGMC/dagmc /DAGMC/build


# installs OpenMc from source
RUN cd /opt && \
    git clone --single-branch --branch develop https://github.com/openmc-dev/openmc.git && \
    cd openmc && \
    mkdir build && \
    cd build && \
    cmake -Doptimize=on -Ddagmc=ON -DDAGMC_ROOT=$DAGMC_INSTALL_DIR -DHDF5_PREFER_PARALLEL=OFF ..  && \
    make -j"$compile_cores" && \
    make -j"$compile_cores" install && \ 
    cd /opt/openmc/ && \
    pip install .

# Clone and install NJOY2016
RUN echo installing NJOY2016 && \
    # git clone https://github.com/njoy/NJOY2016 && \
    cd NJOY2016 && \
    mkdir build && \
    cd build && \
    cmake -Dstatic=on .. && \
    make 2>/dev/null && \
    sudo make install

ENV LD_LIBRARY_PATH=$HOME/MOAB/lib:$HOME/DAGMC/lib
ENV PATH=$PATH:$HOME/NJOY2016/build


# install nuclear data
RUN git clone https://github.com/openmc-dev/data.git
RUN python3 data/convert_nndc71.py --cleanup && \
    rm -rf nndc-b7.1-endf  && \
    rm -rf nndc-b7.1-ace/  && \
    rm -rf nndc-b7.1-download

RUN wget https://github.com/mit-crpg/WMP_Library/releases/download/v1.1/WMP_Library_v1.1.tar.gz
RUN tar -xf WMP_Library_v1.1.tar.gz -C /


ENV OPENMC_CROSS_SECTIONS=/nndc-b7.1-hdf5/cross_sections.xml


# Copy over the local repository files
COPY tests tests/
COPY tasks tasks/

WORKDIR tasks
