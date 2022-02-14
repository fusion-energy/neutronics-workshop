# This Dockerfile creates an enviroment / dependancies needed to run the
# neutronics-workshop.

# This Dockerfile can be build locally or a prebuild image can be downloaded

# To download the prebuild image
# docker pull ghcr.io/fusion-energy/neutronics-workshop
# docker pull ghcr.io/fusion-energy/neutronics-workshop:embree
# docker pull ghcr.io/fusion-energy/neutronics-workshop:embree-avx

# To build this Dockerfile into a docker image:
# docker build -t neutronics-workshop .


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

#  docker build -t neutronics-workshop --build-arg compile_cores=7 --build-arg build_double_down=OFF .
#  docker build -t neutronics-workshop:embree --build-arg compile_cores=7 --build-arg build_double_down=ON --build-arg include_avx=true .
#  docker build -t neutronics-workshop:embree-avx --build-arg compile_cores=7 --build-arg build_double_down=ON --build-arg include_avx=false .

# for local testing I tend to use this build command
# docker build -t neutronics-workshop --build-arg compile_cores=14 --build-arg build_double_down=ON .
# and then run with this command
# docker run -p 8888:8888 neutronics-workshop

# This can't be done currently as the base images uses conda installs for moab / dagmc which don't compile with OpenMC
FROM ghcr.io/openmc-data-storage/miniconda3_4.9.2_endfb-7.1_nndc_tendl_2019:latest as dependencies

ARG compile_cores=1
ARG include_avx=true
ARG build_double_down=OFF

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
                          # libeigen3-dev required for DAGMC
                          libeigen3-dev \
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
                          libgles2-mesa-dev && \
                          apt-get autoremove && \
                          apt-get clean


# installing cadquery and jupyter
RUN conda install jupyter -y && \
    conda install -c conda-forge -c python python=3.8 && \
    conda install -c conda-forge -c cadquery cadquery=2.1
# cadquery master dose not appear to show the .solid in the notebook


# Python libraries used in the workshop
RUN pip install cmake\
# new version of cmake needed for openmc compile
                plotly \
                tqdm \
                # noisyopt \
                scikit-optimize \
                scikit-opt \
                # inference-tools \
                adaptive \
                vtk \
                itkwidgets \
                nest_asyncio \
                pytest \
                pytest-cov \
                holoviews \
                ipywidgets \
# cython is needed for moab
                cython \
                itkwidgets \
                nest_asyncio \
                ipywidgets \
                jupyter-cadquery \
                matplotlib

# needed for openmc
RUN pip install --upgrade numpy


# Clone and install Embree
# embree from conda is not supported yet
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
            then cmake .. -DCMAKE_INSTALL_PREFIX=.. \
                        -DEMBREE_ISPC_SUPPORT=OFF \
                        -DEMBREE_MAX_ISA=NONE \
                        -DEMBREE_ISA_SSE42=ON ; \
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
    git clone  --single-branch --branch 5.3.0 --depth 1 https://bitbucket.org/fathomteam/moab.git && \
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
    python setup.py install
    # the following rm command appears to remove libraries that are need to use
    # pymoab so this has been commented out for now
    # rm -rf /MOAB/moab /MOAB/build

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
    git clone --single-branch --branch develop https://github.com/svalinn/DAGMC.git && \
    # git clone --single-branch --branch develop --depth 1 https://github.com/svalinn/DAGMC.git && \
    cd DAGMC && \
    # this commit is from this PR https://github.com/svalinn/DAGMC/pull/786
    git checkout fbd0cdbad100a0fd8d80de42321e69d09fdd67f4 && \
    cd .. && \
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

# install WMP nuclear data
RUN wget https://github.com/mit-crpg/WMP_Library/releases/download/v1.1/WMP_Library_v1.1.tar.gz && \
    tar -xf WMP_Library_v1.1.tar.gz -C /  && \
    rm WMP_Library_v1.1.tar.gz


# installs OpenMc from source
RUN cd /opt && \
    # git clone --single-branch --branch model_lib_fix --depth 1 https://github.com/fusion-energy/openmc.git && \
    # git clone --single-branch --branch develop https://github.com/openmc-dev/openmc.git && \
    git clone --single-branch --branch v0.13.0 --depth 1 https://github.com/openmc-dev/openmc.git && \
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

# installs TENDL and ENDF nuclear data. Performed after openmc install as
# openmc is needed to write the cross_Sections.xml file
RUN pip install openmc_data_downloader && \
    openmc_data_downloader -d nuclear_data -l ENDFB-7.1-NNDC TENDL-2019 -p neutron photon -e all -i H3 --no-overwrite


ENV OPENMC_CROSS_SECTIONS=/nuclear_data/cross_sections.xml


# python packages from the neutronics workflow
RUN pip install neutronics_material_maker \
                openmc-plasma-source \
                remove_dagmc_tags \
                paramak \
                brep_to_h5m \
                brep_part_finder \
                openmc-dagmc-wrapper \
                openmc-tally-unit-converter \
                regular_mesh_plotter \
                spectrum_plotter \
                dagmc_bounding_box \
                openmc_source_plotter \
                openmc_mesh_tally_to_vtk \
                cad_to_h5m \
                stl_to_h5m

# an older version of openmc is need to provide an older executable
# this particular exectuable allows an inital_source.h5 to be written
# a specific openmc executable can be called using model.run(openmc_exec=path)
RUN conda create --name openmc_version_0_11_0 python=3.8
RUN conda install -c conda-forge openmc=0.11.0 -n openmc_version_0_11_0

# these two from statements can be switched when building locally
FROM dependencies as final
# FROM ghcr.io/fusion-energy/neutronics-workshop:dependencies as final

# Copy over the local repository files
COPY tasks tasks/
COPY tests tests/

WORKDIR /tasks

#this sets the port, gcr looks for this varible
ENV PORT 8888

# could switch to --ip='*'
CMD ["jupyter", "lab", "--notebook-dir=/tasks", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]
