# This Dockerfile creates an enviroment / dependancies needed to run the
# neutronics-workshop.

# This Dockerfile can be build locally or a prebuild image can be downloaded

# To download the prebuild image
# docker pull ghcr.io/fusion-energy/neutronics-workshop:base

# To build this Dockerfile into a docker image:
# docker build -t neutronics-workshop:base -f .devcontainer/base.Dockerfile .


# To build this Dockerfile with different options --build-arg can be used
# --build-arg compile_cores=1
#   int
#   number of cores to compile codes with
# --build-arg build_double_down=OFF
#   ON OFF
#   controls if DAGMC is built with double down (ON) or not (OFF). Note that if double down is OFF then Embree is not included
# --build-arg include_avx=true
#   true false
#   controls if the Embree is built to use AVX instruction set (true) or not (false). AVX is not supported by all CPUs 

#  docker build -t neutronics-workshop:base --build-arg compile_cores=7 --build-arg build_double_down=OFF .
#  docker build -t neutronics-workshop:base:embree --build-arg compile_cores=7 --build-arg build_double_down=ON --build-arg include_avx=true .
#  docker build -t neutronics-workshop:base:embree-avx --build-arg compile_cores=7 --build-arg build_double_down=ON --build-arg include_avx=false .

# for local testing I tend to use this build command
# docker build -t neutronics-workshop:base --build-arg compile_cores=14 --build-arg build_double_down=ON .
# and then run with this command
# docker run -it neutronics-workshop:base

FROM mcr.microsoft.com/vscode/devcontainers/miniconda:0-3 as dependencies

RUN apt-get --allow-releaseinfo-change update
RUN apt-get --yes update && apt-get --yes upgrade

# perhaps libnetcdf13 is needed for unstructured meshes in openmc
# RUN apt-get --yes install libnetcdf13

                          # eigen3 needed for DAGMC
RUN apt-get --yes install libeigen3-dev \
                        #   sudo  \
                          # sudo is needed during the NJOY install
                          git \
                          wget \
                          gfortran \
                          g++ \
                          mpich \
                          libmpich-dev \
                          libhdf5-serial-dev \
                          libhdf5-mpich-dev \
                          hdf5-tools \
                          imagemagick \
                          cmake \
                          # libnetcdf-dev is needed to allow NETCDF on MOAB which helps with tet meshes in OpenMC
                          libnetcdf-dev \
                          # libtbb-dev required for DAGMC
                          libtbb-dev \
                          # libglfw3-dev required for DAGMC
                          libglfw3-dev \
                          # needed for CadQuery functionality
                          libgl1-mesa-glx \
                          # needed for CadQuery functionality
                          libgl1-mesa-dev \
                          # needed for CadQuery functionality
                          libglu1-mesa-dev \
                          # needed for CadQuery functionality
                          freeglut3-dev \
                          # needed for CadQuery functionality
                          libosmesa6 \
                          # needed for CadQuery functionality
                          libosmesa6-dev \
                          # needed for CadQuery functionality
                          libgles2-mesa-dev \
                          # needed for Gmsh functionality
                          libxft2


RUN conda install -c conda-forge -c python python=3.8

RUN conda install -c conda-forge mamba
RUN mamba install -c fusion-energy -c cadquery -c conda-forge paramak==0.8.7


# python packages from the neutronics workflow
RUN pip install neutronics_material_maker[density] \
                remove_dagmc_tags \
                openmc-plasma-source \
                openmc-dagmc-wrapper \
                openmc-tally-unit-converter \
                regular_mesh_plotter \
                spectrum_plotter \
                openmc_source_plotter \
                openmc_depletion_plotter \
                openmc_data_downloader \
                openmc_plot \
                dagmc_geometry_slice_plotter

RUN pip install git+https://github.com/fusion-energy/openmc_weight_window_generator.git


# Python libraries used in the workshop
RUN pip install cmake\
# new version of cmake needed for openmc compile
                plotly \
                tqdm \
                scikit-optimize \
                scikit-opt \
                adaptive \
                vtk \
                itkwidgets \
                pytest \
                holoviews \
                ipywidgets \
# cython is needed for moab
                cython \
                nest_asyncio \
                jupyterlab \
                jupyter-cadquery

# needed for openmc
RUN pip install --upgrade numpy


ARG compile_cores=2
ARG include_avx=false
ARG build_double_down=OFF

# Clone and install Embree
# embree from conda is not supported yet
# TODO check if embree3 package on conda is supported
# conda install -c conda-forge embree >> version: 2.17.7
# requested version "3.6.1"
# added following two lines to allow use on AMD CPUs see discussion
# https://openmc.discourse.group/t/dagmc-geometry-open-mc-aborted-unexpectedly/1369/24?u=pshriwise  
RUN if [ "$build_double_down" = "ON" ] ; \
        then git clone --shallow-submodules --single-branch --branch v3.12.2 --depth 1 https://github.com/embree/embree.git ; \
        cd embree ; \
        mkdir build ; \
        cd build ; \
        if [ "$include_avx" = "false" ] ; \
            then cmake .. -DEMBREE_MAX_ISA=NONE \
                          -DEMBREE_ISA_SSE42=ON \
                          -DCMAKE_INSTALL_PREFIX=.. \
                          -DEMBREE_ISPC_SUPPORT=OFF ; \
        fi ; \
        if [ "$include_avx" = "true" ] ; \
            then cmake .. -DCMAKE_INSTALL_PREFIX=.. \
                        -DEMBREE_ISPC_SUPPORT=OFF ; \
        fi ; \
        make -j"$compile_cores" ; \
        make -j"$compile_cores" install ; \
    fi

# Clone and install MOAB
RUN mkdir MOAB && \
    cd MOAB && \
    git clone  --single-branch --branch 5.4.1 --depth 1 https://bitbucket.org/fathomteam/moab.git && \
    mkdir build && \
    cd build && \
    cmake ../moab -DENABLE_HDF5=ON \
                  -DENABLE_NETCDF=ON \
                  -DENABLE_FORTRAN=OFF \
                  -DENABLE_BLASLAPACK=OFF \
                  -DBUILD_SHARED_LIBS=ON \
                  -DENABLE_PYMOAB=ON \
                  -DCMAKE_INSTALL_PREFIX=/MOAB && \
    make -j"$compile_cores" &&  \
    make -j"$compile_cores" install


ENV PATH=$PATH:/MOAB/bin
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/MOAB/lib


# Clone and install Double-Down
RUN if [ "$build_double_down" = "ON" ] ; \
        then git clone --shallow-submodules --single-branch --branch v1.0.0 --depth 1 https://github.com/pshriwise/double-down.git && \
        cd double-down ; \
        mkdir build ; \
        cd build ; \
        cmake .. -DMOAB_DIR=/MOAB \
                 -DCMAKE_INSTALL_PREFIX=.. \
                 -DEMBREE_DIR=/embree ; \
        make -j"$compile_cores" ; \
        make -j"$compile_cores" install ; \
        rm -rf /double-down/build /double-down/double-down ; \
    fi


# DAGMC version develop install from source
RUN mkdir DAGMC && \
    cd DAGMC && \
    git clone --single-branch --branch v3.2.2 --depth 1 https://github.com/svalinn/DAGMC.git && \
    mkdir build && \
    cd build && \
    cmake ../DAGMC -DBUILD_TALLY=ON \
                   -DMOAB_DIR=/MOAB \
                   -DDOUBLE_DOWN=${build_double_down} \
                   -DBUILD_STATIC_EXE=OFF \
                   -DBUILD_STATIC_LIBS=OFF \
                   -DCMAKE_INSTALL_PREFIX=/DAGMC/ \
                   -DDOUBLE_DOWN_DIR=/double-down && \
    make -j"$compile_cores" install && \
    rm -rf /DAGMC/DAGMC /DAGMC/build

ENV PATH=$PATH:/DAGMC/bin
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/DAGMC/lib

# installs OpenMc from source
RUN cd /opt && \
    # switch back to tagged version when 0.13.3 is released as develop depletion is used
    # git clone --single-branch --branch v0.13.3 --depth 1 https://github.com/openmc-dev/openmc.git && \
    git clone --single-branch --branch develop --depth 1 https://github.com/openmc-dev/openmc.git && \
    cd openmc && \
    mkdir build && \
    cd build && \
    cmake -DOPENMC_USE_DAGMC=ON \
          -DDAGMC_ROOT=/DAGMC \
          -DHDF5_PREFER_PARALLEL=OFF .. && \
    make -j"$compile_cores" && \
    make -j"$compile_cores" install && \
    cd /opt/openmc/ && \
    pip install .

# installs TENDL and ENDF nuclear data. Performed after openmc install as
# openmc is needed to write the cross_Sections.xml file
# RUN pip install openmc_data_downloader && \
#     openmc_data_downloader -d nuclear_data -l ENDFB-7.1-NNDC TENDL-2019 -p neutron photon -e all -i H3 --no-overwrite

RUN pip install openmc_data  && \
    mkdir -p /nuclear_data && \
    download_nndc_chain -d nuclear_data -r b8.0 && \
    download_nndc -d nuclear_data -r b8.0

# install WMP nuclear data
RUN wget https://github.com/mit-crpg/WMP_Library/releases/download/v1.1/WMP_Library_v1.1.tar.gz && \
    tar -xf WMP_Library_v1.1.tar.gz -C /  && \
    rm WMP_Library_v1.1.tar.gz

ENV OPENMC_CROSS_SECTIONS=/nuclear_data/cross_sections.xml
ENV OPENMC_CHAIN_FILE=/nuclear_data/cross_sections.xml
