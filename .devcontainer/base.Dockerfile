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
# docker build -t neutronics-workshop:base --build-arg compile_cores=14 -f .devcontainer/base.Dockerfile .
# and then run with this command
# docker run -it neutronics-workshop:base

# FROM mcr.microsoft.com/vscode/devcontainers/miniconda:0-3 as dependencies
# FROM mcr.microsoft.com/vscode/devcontainers/python:0-3.10-bullseye as dependencies
FROM mcr.microsoft.com/devcontainers/base:bookworm as dependencies

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
                          libxft2 \
                          # needed for gmsh
                          libxcursor-dev \
                          # needed for gmsh
                          libxinerama-dev 
                    
RUN apt-get --yes install python3-pip python3-venv


# Enabling a venv within Docker is needed to avoid system wide installs
# https://pythonspeed.com/articles/activate-virtualenv-dockerfile/
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --upgrade pip

# python packages from the neutronics workflow
RUN pip install neutronics_material_maker[density] \
                stl_to_h5m \
                remove_dagmc_tags \
                openmc-dagmc-wrapper \
                openmc-tally-unit-converter \
                regular_mesh_plotter \
                spectrum_plotter \
                openmc_source_plotter \
                openmc_depletion_plotter \
                "openmc_data_downloader>=0.6.0" \
                "openmc_data>=0.2.2" \
                openmc_plot \
                dagmc_geometry_slice_plotter \
                "cad_to_dagmc>=0.5.0" \
                paramak \
                # 6.5.3-5 nbconvert is needed to avoid an error and that requires trixie debian OS
                # https://salsa.debian.org/python-team/packages/nbconvert/-/tags
                # https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1068349
                lxml[html_clean]

# openmc-plasma-source needs main branch to work with openmc develop, currently unreleased
RUN pip install git+https://github.com/fusion-energy/openmc-plasma-source

RUN pip install git+https://github.com/CadQuery/cadquery.git@bc82cb04c59668a1369d9ce648361c8786bbd1c8 --no-deps
RUN pip install cadquery-ocp==7.7.1 "multimethod>=1.7<2.0" nlopt typish casadi path ezdxf nptyping==2.0.1

# Python libraries used in the workshop
RUN pip install cmake\
# new version of cmake needed for openmc compile
                plotly \
                "vtk==9.2.5"  \
                itkwidgets \
                pytest \
                # holoviews \
                ipywidgets \
# cython is needed for moab and openmc, specific version tagged to avoid build errors
                "cython<3.0" \
                # nest_asyncio \
                jupyterlab \
                jupyter-cadquery \
                gmsh

# needed for openmc
RUN pip install --upgrade numpy


ARG compile_cores=2
ARG include_avx=false
ARG build_double_down=OFF

# Clone and install Embree
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
    # newer versions of moab (5.4.0, 5.4.1) don't produce an importable pymoab package!
    # TODO try moab 5.5.0
    git clone  --single-branch --branch 5.3.1 --depth 1 https://bitbucket.org/fathomteam/moab.git && \
    mkdir build && \
    cd build && \
    cmake ../moab -DENABLE_HDF5=ON \
                  -DENABLE_NETCDF=ON \
                  -DENABLE_FORTRAN=OFF \
                  -DENABLE_BLASLAPACK=OFF \
                  -DBUILD_SHARED_LIBS=ON \
                  -DENABLE_PYMOAB=ON \
                  -DCMAKE_INSTALL_PREFIX=/MOAB && \
    mkdir -p MOAB/lib/pymoab/lib/python3.11/site-packages && \
    PYTHONPATH=/MOAB/lib/pymoab/lib/python3.11/site-packages:${PYTHONPATH} make -j && \
    PYTHONPATH=/MOAB/lib/pymoab/lib/python3.11/site-packages:${PYTHONPATH} make install -j

ENV PYTHONPATH="/MOAB/lib/python3.11/site-packages/pymoab-5.3.1-py3.11-linux-x86_64.egg/"

RUN python -c "import pymoab"

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
# switch back to tagged version when 0.13.3 is released as develop depletion is used
# git clone --single-branch --branch v0.13.3 --depth 1 https://github.com/openmc-dev/openmc.git && \
RUN git clone --single-branch --branch develop --depth 1 https://github.com/openmc-dev/openmc.git && \
    cd openmc && \
    mkdir build && \
    cd build && \
    cmake -DOPENMC_USE_DAGMC=ON \
          -DDAGMC_ROOT=/DAGMC \
          -DHDF5_PREFER_PARALLEL=OFF .. && \
    make -j"$compile_cores" && \
    make -j"$compile_cores" install && \
    cd /openmc/ && \
    pip install .

# Installs ENDF with TENDL where ENDF cross sections are not available.
# Performed after openmc install as openmc is needed to write the cross_Sections.xml file
RUN openmc_data_downloader -d nuclear_data -l ENDFB-8.0-NNDC TENDL-2019 -p neutron photon -e all -i H3 --no-overwrite
RUN download_endf_chain -d nuclear_data -r b8.0

# install WMP nuclear data
RUN wget https://github.com/mit-crpg/WMP_Library/releases/download/v1.1/WMP_Library_v1.1.tar.gz && \
    tar -xf WMP_Library_v1.1.tar.gz -C /  && \
    rm WMP_Library_v1.1.tar.gz

ENV OPENMC_CROSS_SECTIONS=/nuclear_data/cross_sections.xml
ENV OPENMC_CHAIN_FILE=/nuclear_data/chain-endf-b8.0.xml
