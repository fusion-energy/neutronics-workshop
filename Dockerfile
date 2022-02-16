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


RUN conda install conda-forge embree

RUN conda install maob
RUN conda install double-down
RUN conda install dagmc

ENV PATH=$PATH:/DAGMC/bin
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/DAGMC/lib

# install WMP nuclear data
RUN wget https://github.com/mit-crpg/WMP_Library/releases/download/v1.1/WMP_Library_v1.1.tar.gz && \
    tar -xf WMP_Library_v1.1.tar.gz -C /  && \
    rm WMP_Library_v1.1.tar.gz

RUN conda install openmc

# installs TENDL and ENDF nuclear data. Performed after openmc install as
# openmc is needed to write the cross_Sections.xml file
RUN pip install openmc_data_downloader && \
    openmc_data_downloader -d nuclear_data -l ENDFB-7.1-NNDC TENDL-2019 -p neutron photon -e all -i H3 --no-overwrite


ENV OPENMC_CROSS_SECTIONS=/nuclear_data/cross_sections.xml

RUN conda install -c fusion-energy -c cadquery -c conda-forge paramak

# python packages from the neutronics workflow
RUN pip install neutronics_material_maker \
                openmc-plasma-source \
                remove_dagmc_tags \
                openmc-dagmc-wrapper \
                openmc-tally-unit-converter \
                regular_mesh_plotter \
                spectrum_plotter \
                openmc_source_plotter \
                openmc_mesh_tally_to_vtk \

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
