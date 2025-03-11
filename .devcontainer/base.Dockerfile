# This Dockerfile creates an enviroment / dependencies needed to run the
# neutronics-workshop.

# This Dockerfile can be build locally or a prebuild image can be downloaded

# To download the prebuild image
# docker pull ghcr.io/fusion-energy/neutronics-workshop:base

# To build this Dockerfile into a docker image:
# docker build -t neutronics-workshop:base -f .devcontainer/base.Dockerfile .

# and then run with this command
# docker run -it neutronics-workshop:base

FROM mcr.microsoft.com/devcontainers/base:bookworm AS dependencies

RUN apt-get --allow-releaseinfo-change update
RUN apt-get --yes update && apt-get --yes upgrade

# perhaps libnetcdf13 is needed for unstructured meshes in openmc
# RUN apt-get --yes install libnetcdf13

                          # eigen3 needed for DAGMC
RUN apt-get --yes install libeigen3-dev \
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
                openmc-tally-unit-converter \
                regular_mesh_plotter \
                spectrum_plotter \
                openmc_source_plotter \
                openmc_depletion_plotter \
                "openmc_data_downloader>=0.6.0" \
                retry \
                "openmc_data>=0.2.10" \
                openmc_plot \
                dagmc_geometry_slice_plotter \
                "cad_to_dagmc>=0.8.2" \
                "openmc-plasma-source>=0.3.1" \
                paramak --no-deps \
                mpmath \
                sympy \
                asteval \
                # pyvist \ # TODO add in pyvist but check it doesn't break the vtk/cad vis
                gmsh \
                pint \
                # 6.5.3-5 nbconvert is needed to avoid an error and that requires trixie debian OS
                # https://salsa.debian.org/python-team/packages/nbconvert/-/tags
                # https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1068349
                lxml[html_clean]

RUN pip install git+https://github.com/svalinn/pydagmc@c6621b77428b2ebb04c5cd6b7a8837655ab35800

# Python libraries used in the workshop
RUN pip install plotly \
                # vtk \
                itkwidgets \
                pytest \
                ipywidgets \
                # cython is needed for moab and openmc, specific version tagged to avoid build errors
                "cython<3.0" \
                jupyterlab \
                jupyter-cadquery

# temporary wheels for moab hosted on github repo https://github.com/shimwell/wheels
RUN pip install https://github.com/shimwell/wheels/raw/refs/heads/main/moab/moab-wheels-ubuntu-latest/moab-5.5.1-cp311-cp311-manylinux_2_28_x86_64.whl

# temporary wheels for openmc hosted on github repo https://github.com/shimwell/wheels
RUN pip install https://github.com/shimwell/wheels/raw/refs/heads/main/openmc/openmc-0.15.1.dev0-cp311-cp311-manylinux_2_28_x86_64.whl

# the order of these install appears to matter when it comes to jupyter vtk rendering
RUN pip install cadquery-vtk
RUN pip install git+https://github.com/CadQuery/cadquery.git@7cade87e68f2755fe7a121d797428c7b3d41b1be

RUN apt-get update && apt-get install -y \
    xvfb \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    libosmesa6-dev \
    libgl1-mesa-dev \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*
RUN pip install pyvista panel
RUN pip install pyvista trame-vtk trame ipywidgets itkwidgets

# Path.home is /root
RUN mkdir -p /root/nuclear_data

# Installs ENDF with TENDL where ENDF cross sections are not available.
# Performed after openmc install as openmc is needed to write the cross_Sections.xml file
RUN openmc_data_downloader -d /root/nuclear_data -l ENDFB-8.0-NNDC TENDL-2019 -p neutron photon -e all -i H3 --no-overwrite
RUN download_endf_chain -d /root/nuclear_data -r b8.0

# install WMP nuclear data
RUN wget https://github.com/mit-crpg/WMP_Library/releases/download/v1.1/WMP_Library_v1.1.tar.gz && \
    tar -xf WMP_Library_v1.1.tar.gz -C /root/nuclear_data  && \
    rm WMP_Library_v1.1.tar.gz
