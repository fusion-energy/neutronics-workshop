# build with the following command, replace the 7 cores with the number of
# cores you would like to use
# docker build -t fusion-energy/neutronics-workshop --build-arg compile_cores=7 .

# run with the following command
# docker run -p 8888:8888 fusion-energy/neutronics-workshop

# test with the folowing command
# docker run --rm fusion-energy/neutronics-workshop pytest ../tests

FROM continuumio/miniconda3:4.9.2

ARG compile_cores=1

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
    conda install -c conda-forge -c python python=3.7.8 && \
    conda install -c conda-forge -c cadquery cadquery=2
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
                neutronics_material_maker \
                pytest \
                pytest-cov \
                # holoviews \
                ipywidgets \
# cython is needed for moab
                cython \
                paramak \
                openmc_data_downloader \
                itkwidgets \
                nest_asyncio \
                ipywidgets

# svalinn-tools should be added but it is not working with python 3 at the moment

# needed for openmc
RUN pip install --upgrade numpy



# Clone and install Embree
RUN mkdir embree && \
    cd embree && \
    git clone --single-branch --branch v3.12.2 --depth 1 https://github.com/embree/embree.git && \
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
    git clone  --single-branch --branch 5.2.1 --depth 1 https://bitbucket.org/fathomteam/moab.git && \
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
RUN mkdir double-down && \
    cd double-down && \
    git clone --single-branch --branch main --depth 1 https://github.com/pshriwise/double-down.git && \
    # cd double-down && \
    mkdir build && \
    cd build && \
    cmake ../double-down -DMOAB_DIR=/MOAB \
                         -DCMAKE_INSTALL_PREFIX=/double-down \
                         -DEMBREE_DIR=/embree && \
    make -j"$compile_cores" && \
    make -j"$compile_cores" install && \
    rm -rf /double-down/build /double-down/double-down 


# DAGMC version 3.2.0 install from source
RUN mkdir DAGMC && \
    cd DAGMC && \
    git clone --single-branch --branch 3.2.0 --depth 1 https://github.com/svalinn/DAGMC.git && \
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

ENV PATH=$PATH:/DAGMC/bin    
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/DAGMC/lib


# installs OpenMc from source
RUN cd /opt && \
    git clone --single-branch --branch develop --depth 1 https://github.com/openmc-dev/openmc.git && \
    # git clone --single-branch --branch v0.12.1 --depth 1 https://github.com/openmc-dev/openmc.git && \
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


# install nuclear data
RUN wget https://github.com/mit-crpg/WMP_Library/releases/download/v1.1/WMP_Library_v1.1.tar.gz && \
    tar -xf WMP_Library_v1.1.tar.gz -C /  && \
    rm WMP_Library_v1.1.tar.gz

RUN git clone --single-branch --branch master --depth 1 https://github.com/openmc-dev/data.git && \
    openmc_data_downloader -l ENDFB-7.1-NNDC TENDL-2019 -d cross_section_data -p neutron photon -e all

ENV OPENMC_CROSS_SECTIONS=/cross_section_data/cross_sections.xml

# download and compile parametric-plasma-source
RUN git clone --single-branch --branch develop --depth 1 https://github.com/open-radiation-sources/parametric-plasma-source.git && \
    cd parametric-plasma-source && \
    mkdir build && \
    cd build && \
    cmake .. -DOPENMC_DIR=/opt/openmc && \
    make && \
    cd .. && \
    pip install .

ENV PYTHONPATH="${PYTHONPATH}:/parametric-plasma-source/build"

# Copy over the local repository files
COPY tests tests/
COPY tasks tasks/

WORKDIR /tasks

#this sets the port, gcr looks for this varible
ENV PORT 8888

# could switch to --ip='*'
CMD ["jupyter", "notebook", "--notebook-dir=/tasks", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]
