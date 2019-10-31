FROM ubuntu:18.04

MAINTAINER Jonathan Shimwell

# This docker image contains all the dependencies required to run OpenMC.
# More details on OpenMC are available on the web page https://openmc.readthedocs.io

# build with
#     sudo docker build -t shimwell/openmc:latest .
# run with
#     docker run --net=host -it --rm -v /tmp/.X11-unix:/tmp/.X11-unix -v $PWD:/openmc_workshop -e DISPLAY=unix$DISPLAY --privileged shimwell/openmc
# if you have no GUI in docker try running this xhost command prior to running the image
#     xhost local:root


RUN apt-get --yes update && apt-get --yes upgrade

RUN apt-get -y install locales
RUN locale-gen en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

# Install Packages Required
RUN apt-get --yes update && apt-get --yes upgrade
RUN apt-get --yes install gfortran 
RUN apt-get --yes install g++ 
RUN apt-get --yes install cmake 
RUN apt-get --yes install libhdf5-dev 
RUN apt-get --yes install git
RUN apt-get update

RUN apt-get install -y python3-pip
RUN apt-get install -y python3-dev
RUN apt-get install -y python3-setuptools
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get install -y ipython3
RUN apt-get update
RUN apt-get install -y python3-tk

#Install Packages Optional
RUN apt-get --yes update
RUN apt-get --yes install imagemagick
RUN apt-get --yes install hdf5-tools
RUN apt-get --yes install paraview
RUN apt-get --yes install eog
RUN apt-get --yes install wget
RUN apt-get --yes install firefox
RUN apt-get --yes install dpkg
RUN apt-get --yes install libxkbfile1

#Install Packages Optional for distributed memory parallel simulations
RUN apt install --yes mpich libmpich-dev
RUN apt install --yes openmpi-bin libopenmpi-dev


RUN apt-get --yes install libblas-dev 
# RUN apt-get --yes install libatlas-dev 
RUN apt-get --yes install liblapack-dev

# Python Prerequisites Required
RUN pip3 install numpy
RUN pip3 install pandas
RUN pip3 install six
RUN pip3 install h5py
RUN pip3 install Matplotlib
RUN pip3 install uncertainties
RUN pip3 install lxml
RUN pip3 install scipy

# Python Prerequisites Optional
RUN pip3 install cython
RUN pip3 install vtk
RUN apt-get install --yes libsilo-dev
RUN pip3 install pytest
RUN pip3 install codecov
RUN pip3 install pytest-cov
RUN pip3 install pylint

# Python libraries used in the workshop
RUN pip3 install plotly
RUN pip3 install tqdm
RUN pip3 install ghalton
RUN pip3 install noisyopt
RUN pip3 install inference-tools

# Pyne requirments
RUN pip3 install tables
RUN pip3 install setuptools
RUN pip3 install prettytable
RUN pip3 install sphinxcontrib_bibtex
RUN pip3 install numpydoc
RUN pip3 install nbconvert
RUN pip3 install nose

# Clone and install NJOY2016
RUN git clone https://github.com/njoy/NJOY2016 /opt/NJOY2016 && \
    cd /opt/NJOY2016 && \
    mkdir build && cd build && \
    cmake -Dstatic=on .. && make 2>/dev/null && make install

RUN rm /usr/bin/python
RUN ln -s /usr/bin/python3 /usr/bin/python

# MOAB Variables
ENV MOAB_BRANCH='Version5.1.0'
ENV MOAB_REPO='https://bitbucket.org/fathomteam/moab/'
ENV MOAB_INSTALL_DIR=$HOME/MOAB/

# DAGMC Variables
ENV DAGMC_BRANCH='develop'
ENV DAGMC_REPO='https://github.com/svalinn/dagmc'
ENV DAGMC_INSTALL_DIR=$HOME/DAGMC/
RUN set -ex

# MOAB Install
RUN cd $HOME
RUN mkdir MOAB && cd MOAB && \
        git clone -b $MOAB_BRANCH $MOAB_REPO && \
        mkdir build && cd build && \
        cmake ../moab -DENABLE_HDF5=ON -DBUILD_SHARED_LIBS=ON -DCMAKE_INSTALL_PREFIX=$MOAB_INSTALL_DIR -DENABLE_PYMOAB=ON && \
        make && make test install && \
        cd pymoab && python3 setup.py install
        # cd .. && \
        # cmake ../moab -DBUILD_SHARED_LIBS=OFF && \
        # make install && \
        # rm -rf $HOME/MOAB/moab
ENV LD_LIBRARY_PATH=$MOAB_INSTALL_DIR/lib:$LD_LIBRARY_PATH

# DAGMC Install
RUN mkdir DAGMC && cd DAGMC && \
        git clone -b $DAGMC_BRANCH $DAGMC_REPO && \
        mkdir build && cd build && \
        cmake ../dagmc -DBUILD_TALLY=ON -DCMAKE_INSTALL_PREFIX=$DAGMC_INSTALL_DIR -DMOAB_DIR=$MOAB_INSTALL_DIR -DBUILD_STATIC_LIBS=OFF && \
        make install && \
        rm -rf $HOME/DAGMC/dagmc
ENV LD_LIBRARY_PATH=$DAGMC_INSTALL_DIR/lib:$LD_LIBRARY_PATH

ENV FC=mpif90
ENV CC=mpicc

# installs OpenMc from source 
# RUN git clone https://github.com/openmc-dev/openmc.git && \  
RUN git clone https://github.com/makeclean/openmc.git && \
    cd openmc && \
#     git checkout develop && \
    git checkout dlopen_source && \
    mkdir build && cd build && \
    cmake -Ddagmc=ON .. && \
#     cmake -Ddagmc=ON -Ddebug=on .. && \
    make && \
    make install

RUN PATH="$PATH:/openmc/build/bin/"
RUN cp /openmc/build/bin/openmc /usr/local/bin

#this python install method allows source code changes to be trialed
RUN cd openmc && python3 setup.py develop 
# #RUN cd openmc && pip3 install .

RUN echo 'alias python="python3"' >> ~/.bashrc

#downloads nuclear data including neutron and photon cross sections from nndc
RUN bash /openmc/tools/ci/download-xs.sh
ENV OPENMC_CROSS_SECTIONS='/root/nndc_hdf5/cross_sections.xml'


#installs VS code which is an IDE (Integrated development environment) for code
RUN wget https://update.code.visualstudio.com/1.34.0/linux-deb-x64/stable
RUN dpkg -i stable 
RUN apt-get --yes install -f
RUN echo 'function coder() { code "$1" --user-data-dir; }' >> ~/.bashrc
#installs python and docker exstentions for syntax highlighting and hinting
RUN code "$1" --user-data-dir  --install-extension ms-python.python
RUN code "$1" --user-data-dir  --install-extension tht13.python
RUN code "$1" --user-data-dir  --install-extension ms-azuretools.vscode-docker
RUN code "$1" --user-data-dir  --install-extension ms-vscode.sublime-keybindings


#installs FreeCAD
RUN apt-get install -y software-properties-common 
RUN add-apt-repository ppa:freecad-maintainers/freecad-stable
RUN apt-get update 
RUN apt-get --yes install freecad 
RUN ln -s /usr/lib/freecad/Mod /usr/lib/freecad-python3/Mod




RUN git clone https://github.com/Shimwell/openmc_workshop.git

WORKDIR /openmc_workshop

# this compiles the parametric plasma source
RUN cd /openmc_workshop/parametric_plasma_source && bash compile.sh
# source_sampling.so is the compiled plasma source so this copies it to various task folders for later use
RUN cp /openmc_workshop/parametric_plasma_source/source_sampling.so /openmc_workshop/tasks/task_3
RUN cp /openmc_workshop/parametric_plasma_source/source_sampling.so /openmc_workshop/tasks/task_4
RUN cp /openmc_workshop/parametric_plasma_source/source_sampling.so /openmc_workshop/tasks/task_5
RUN cp /openmc_workshop/parametric_plasma_source/source_sampling.so /openmc_workshop/tasks/task_6
RUN cp /openmc_workshop/parametric_plasma_source/source_sampling.so /openmc_workshop/tasks/task_7
RUN cp /openmc_workshop/parametric_plasma_source/source_sampling.so /openmc_workshop/tasks/task_8





# this allows different nuclear data to be downloaded, it is not needed for the tutorial
# RUN git clone https://github.com/openmc-dev/data.git 
# # copy over required python scripts to the data repository
# RUN cp openmc/scripts/openmc-get-photon-data data/
# RUN cp openmc/scripts/openmc-ace-to-hdf5 data/

# RUN python3 data/convert_nndc71.py -b

# RUN OPENMC_CROSS_SECTIONS=/nndc_hdf5/cross_sections.xml
# RUN export OPENMC_CROSS_SECTIONS=/nndc_hdf5/cross_sections.xml
# RUN echo 'export OPENMC_CROSS_SECTIONS=/nndc_hdf5/cross_sections.xml' >> ~/.bashrc


# RUN git clone https://github.com/C-bowman/inference_tools.git
# RUN echo 'export PYTHONPATH=$PYTHONPATH:/inference_tools/inference' >> ~/.bashrc
