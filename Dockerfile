# build with the following command, replace the 50 cores with however many you would like to use
# docker build -t ukaea/openmcworkshop --build-arg compile_cores=50 .

# run with the following command
# docker run -p 8888:8888 ukaea/openmcworkshop

# test with the folowing command
# docker run --rm ukaea/openmcworkshop pytest ../tests

FROM continuumio/miniconda3

ARG compile_cores=1

RUN apt-get --yes update && apt-get --yes upgrade

# perhaps libnetcdf13 is needed for unstructured meshes in openmc
# RUN apt-get --yes install libnetcdf13

# eigen3 needed for DAGMC
RUN apt-get --yes install libeigen3-dev \
                          sudo  \ 
# sudo is needed during the NJOY install
                          git \
                          libnetcdf-dev \
# libnetcdf-dev is needed to allow NETCDF on MOAB which helps with tet meshes in OpenMC
                          wget

# installing cadquery and jupyter
RUN conda install jupyter -y
RUN conda install -c conda-forge -c python python=3.7.8
RUN conda install -c conda-forge -c cadquery cadquery=2
# cadquery master don't appear to show the .solid in the notebook


# Python libraries used in the workshop
RUN pip install cmake\
# new version of cmake needed for openmc compile
                plotly \
                tqdm \
                noisyopt \
                scikit-optimize \
                scikit-opt \
                inference-tools \
                adaptive \
                vtk \
                itkwidgets \
                nest_asyncio \
                neutronics_material_maker \
                pytest \
                pytest-cov \
                holoviews \
                ipywidgets \
                svalinn-tools \
# cython is needed for moab
                cython \
                paramak

# needed for openmc
RUN pip install --upgrade numpy


# Install dependencies from Debian package manager
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y \
        wget git gfortran g++ \
        mpich libmpich-dev libhdf5-serial-dev libhdf5-mpich-dev \
        hdf5-tools imagemagick cmake && \
    apt-get autoremove  && \
    apt-get clean


# install addition packages required for DAGMC
RUN apt-get --yes install  \
        libeigen3-dev libnetcdf-dev libtbb-dev libglfw3-dev && \
        apt-get autoremove  && \
        apt-get clean


# needed for CadQuery functionality
RUN apt-get install -y libgl1-mesa-glx libgl1-mesa-dev libglu1-mesa-dev \
                       freeglut3-dev libosmesa6 libosmesa6-dev \
                       libgles2-mesa-dev && \
                       apt-get autoremove  && \
                       apt-get clean


# Clone and install Embree
RUN mkdir embree && \
    cd embree && \
    git clone --single-branch --branch master https://github.com/embree/embree.git && \
    mkdir build && \
    cd build && \
    cmake ../embree -DCMAKE_INSTALL_PREFIX=/embree \
                    -DEMBREE_ISPC_SUPPORT=OFF && \
    make -j"$compile_cores" && \
    make -j"$compile_cores" install && \
    rm -rf /embree/build /embree/embree


# Clone and install MOAB
RUN mkdir MOAB && \
    cd MOAB && \
    git clone  --single-branch --branch develop https://bitbucket.org/fathomteam/moab.git && \
    mkdir build && \
    cd build && \
    cmake ../moab -DENABLE_HDF5=ON \
                  -DENABLE_NETCDF=ON \
                  -DENABLE_FORTRAN=OFF \
                  -DENABLE_BLASLAPACK=OFF \
                  -DBUILD_SHARED_LIBS=OFF \
                  -DCMAKE_INSTALL_PREFIX=/MOAB && \
    make -j"$compile_cores" &&  \
    make -j"$compile_cores" install && \
    cmake ../moab -DENABLE_HDF5=ON \
                  -DENABLE_PYMOAB=ON \
                  -DENABLE_FORTRAN=OFF \
                  -DBUILD_SHARED_LIBS=ON \
                  -DENABLE_BLASLAPACK=OFF \
                  -DCMAKE_INSTALL_PREFIX=/MOAB && \
    make -j"$compile_cores" install && \
    cd pymoab && \
    bash install.sh && \
    python setup.py install && \
    rm -rf /MOAB/moab /MOAB/build
    
ENV PATH=$PATH:/MOAB/bin
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/MOAB/lib


# Clone and install Double-Down
RUN git clone --single-branch --branch main https://github.com/pshriwise/double-down.git && \
    cd double-down && \
    mkdir build && \
    cd build && \
    cmake .. -DMOAB_DIR=/MOAB \
             -DCMAKE_INSTALL_PREFIX=.. \
             -DEMBREE_DIR=/embree && \
    make -j"$compile_cores" && \
    make -j"$compile_cores" install


# DAGMC install from source
RUN mkdir DAGMC && \
    cd DAGMC && \
    git clone --single-branch --branch develop https://github.com/svalinn/DAGMC.git && \
    mkdir build && \
    cd build && \
    cmake ../DAGMC -DBUILD_TALLY=ON \
                   -DMOAB_DIR=/MOAB \
                   -DDOUBLE_DOWN=ON \
                   -DBUILD_STATIC_EXE=OFF \
                   -DBUILD_STATIC_LIBS=OFF \
                   -DCMAKE_INSTALL_PREFIX=/DAGMC/ \
                   -DDOUBLE_DOWN_DIR=/double-down && \
    make -j"$compile_cores" install && \
    rm -rf /DAGMC/DAGMC /DAGMC/build
    
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/DAGMC/lib


# installs OpenMc from source
RUN cd /opt && \
    git clone --single-branch --branch develop https://github.com/openmc-dev/openmc.git && \
    cd openmc && \
    mkdir build && \
    cd build && \
    cmake -Doptimize=on \
          -Ddagmc=ON \
          -DDAGMC_ROOT=/DAGMC \
          -DHDF5_PREFER_PARALLEL=off ..  && \
    make -j"$compile_cores" && \
    make -j"$compile_cores" install && \ 
    cd /opt/openmc/ && \
    pip install .

#  NJOY2016 install from source
RUN mkdir njoy && cd njoy && \
    git clone --single-branch --branch master https://github.com/njoy/NJOY2016.git && \
    mkdir build && cd build && \
    cmake -Dstatic=on ../NJOY2016 && \
    make 2>/dev/null && \
    rm -rf /njoy/NJOY2016

ENV PATH=$PATH:/njoy/build


# install nuclear data
RUN wget https://github.com/mit-crpg/WMP_Library/releases/download/v1.1/WMP_Library_v1.1.tar.gz
RUN tar -xf WMP_Library_v1.1.tar.gz -C /

ENV OPENMC_CROSS_SECTIONS=/cross_sections.xml

COPY scripts/delete_nuclear_data_not_used_in_cross_section_xml.py .

RUN git clone https://github.com/openmc-dev/data.git
RUN python data/convert_nndc71.py --cleanup && \
    rm -rf nndc-b7.1-endf  && \
    rm -rf nndc-b7.1-ace/  && \
    rm -rf nndc-b7.1-download && \
    python data/convert_tendl.py --cleanup && \
    rm -rf tendl-2019-ace/ && \
    rm -rf tendl-2019-download && \
    python data/combine_libraries.py -l nndc-b7.1-hdf5/cross_sections.xml tendl-2019-hdf5/cross_sections.xml -o cross_sections.xml && \
    python delete_nuclear_data_not_used_in_cross_section_xml.py


# download and compile parametric-plasma-source
RUN git clone https://github.com/open-radiation-sources/parametric-plasma-source.git && \
    cd parametric-plasma-source && \
    git checkout develop && \
    mkdir build && \
    cd build && \
    cmake .. -DOPENMC_DIR=/opt/openmc && \
    make && \
    pip install -e .


# Copy over the local repository files
COPY tests tests/
COPY tasks tasks/

WORKDIR tasks

#this sets the port, gcr looks for this varible
ENV PORT 8888

# could switch to --ip='*'
CMD ["jupyter", "notebook", "--notebook-dir=/tasks", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]
