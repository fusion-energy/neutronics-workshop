
# build with the following command
# sudo docker build -f Dockerfile_openmc -t openmcworkshop/openmc

FROM ubuntu:18.04

# Python and OpenMC installation

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

#Install unzip
RUN apt-get update
RUN apt-get install -y unzip

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

# Python Prerequisites Optional (Required)
RUN pip3 install cython
RUN pip3 install vtk
RUN apt-get install --yes libsilo-dev
RUN pip3 install pytest
RUN pip3 install codecov
RUN pip3 install pytest-cov
RUN pip3 install pylint

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


# installs OpenMc from source 
RUN cd opt && \
    git clone https://github.com/openmc-dev/openmc.git && \  
    cd openmc && \
    git checkout develop && \
    mkdir build && cd build && \
    cmake .. && \
#    cmake -Ddebug=on .. && \
    make && \
    make install

#this python install method allows openmc source code changes to be trialed
RUN cd /opt/openmc && python3 setup.py develop
#this alternative install method makes changing source code and testing is a little harder 
#RUN cd /opt/openmc && pip3 install .

RUN git clone https://github.com/openmc-dev/plotter.git
RUN echo 'export PATH=$PATH:/plotter/' >> ~/.bashrc

RUN echo 'alias python="python3"' >> ~/.bashrc


RUN apt-get --yes update && apt-get --yes upgrade

RUN apt-get -y install locales
RUN locale-gen en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'


RUN apt-get --yes update && apt-get --yes upgrade

# Python installation
RUN apt-get install -y python3-pip
RUN apt-get install -y python3-dev
RUN apt-get install -y python3-setuptools
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get install -y ipython3
RUN apt-get update
RUN apt-get install -y python3-tk


# required pacakges identified from openmc travis.yml
RUN apt-get --yes install mpich
RUN apt-get --yes install libmpich-dev
RUN apt-get --yes install libhdf5-serial-dev
RUN apt-get --yes install libhdf5-mpich-dev
RUN apt-get --yes install libblas-dev
RUN apt-get --yes install liblapack-dev

RUN apt-get -y install sudo #  needed as the install NJOY script has a sudo make install command
RUN apt-get -y install git
RUN apt-get -y install cmake

#RUN rm /usr/bin/python
RUN ln -s /usr/bin/python3 /usr/bin/python

# global enviromental varibles set in th travis.yml
ENV HOME=/root
ENV MPI_DIR=/usr
ENV HDF5_ROOT=/usr
#ENV OMP_NUM_THREADS=2 #commented out for users with more than 2 threads
ENV OPENMC_CROSS_SECTIONS=$HOME/nndc_hdf5/cross_sections.xml
ENV OPENMC_ENDF_DATA=$HOME/endf-b-vii.1
ENV LD_LIBRARY_PATH=$HOME/MOAB/lib:$HOME/DAGMC/lib
ENV PATH=$PATH:$HOME/NJOY2016/build
ENV COVERALLS_PARALLEL=true
ENV NUMPY_EXPERIMENTAL_ARRAY_FUNCTION=0

#these are used in the travis install scripts to decide what to install
ENV OMP=y
ENV MPI=n
ENV PHDF5=n
ENV DAGMC=y

# installs OpenMc from source
RUN cd /opt && \
    git clone https://github.com/openmc-dev/openmc.git && \
    cd openmc && \
    git checkout develop

# pip install is used in some of the travis scripts but pip3 is installed, this alias makes pip and pip3 the same
RUN ln -s /usr/bin/pip3 /usr/bin/pip

# newer CMake version allows us to set libraries, includes of the
# imported DAGMC target in CMake
RUN apt remove -y cmake
RUN pip install cmake==3.12.0
RUN apt install wget

# these travis scripts include NJOY, DAGMC, MOAB

RUN cd /opt/openmc && \
   ./tools/ci/travis-install.sh

# this script downloads the nndc (ENDF) nuclear data which is done in a later docker image
# RUN cd /opt/openmc && \
   #./tools/ci/travis-before-script.sh 

# this script perform tests
# RUN cd /opt/openmc && \
 #    ./tools/ci/travis-script.sh

RUN git clone https://github.com/openmc-dev/plotter.git


# dependancies for the occ_faceter
RUN apt-get --yes update && apt-get --yes upgrade
RUN apt-get --yes install libcgal-dev
RUN apt-get --yes install software-properties-common
RUN add-apt-repository ppa:freecad-maintainers/freecad-stable
RUN apt-get --yes install libocc*dev
RUN apt-get --yes install occ*
RUN apt-get --yes install libtbb-dev

# install the occ_faceter, this currently uses a branch that could be merged
RUN git clone https://github.com/makeclean/occ_faceter.git && \
    cd occ_faceter && \
    mkdir build && cd build && \
    cmake .. -DCMAKE_INSTALL_PREFIX=.. && \
    make && \
    make install


# there can be only one
RUN echo 'alias python="python3"' >> ~/.bashrc

RUN echo 'export PATH=$PATH:~/MOAB/bin' >> ~/.bashrc
RUN echo 'export PATH=$PATH:/plotter/' >> ~/.bashrc
RUN echo 'export PATH=$PATH:~/DAGMC/bin' >> ~/.bashrc
RUN echo 'export PATH=$PATH:/occ_faceter/bin/' >> ~/.bashrc

# install endf nuclear data

# clone data repository
RUN git clone https://github.com/openmc-dev/data.git

# run script that converts ACE data to hdf5 data
RUN python3 data/convert_nndc71.py --cleanup

ENV OPENMC_CROSS_SECTIONS=/nndc-b7.1-hdf5/cross_sections.xml

# Python libraries used in the workshop
RUN pip3 install plotly
RUN pip3 install tqdm
RUN pip3 install ghalton==0.6.1
RUN pip3 install noisyopt
RUN pip3 install scikit-optimize
RUN pip3 install inference-tools
RUN pip3 install neutronics_material_maker
RUN pip3 install adaptive

# dependancies used in the workshop
RUN apt-get --yes install imagemagick
RUN apt-get --yes install hdf5-tools
RUN apt-get --yes install paraview
RUN apt-get --yes install eog
RUN apt-get --yes install wget
RUN apt-get --yes install firefox

# dependancies for vscode
RUN apt-get --yes install libnotify4
RUN apt-get --yes install libnss3
RUN apt-get --yes install libxkbfile1
RUN apt-get --yes install dpkg
RUN apt-get --yes install libsecret-1-0
RUN apt-get --yes install libasound2

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
RUN apt-get -y update
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:freecad-maintainers/freecad-stable
RUN apt-get update 
RUN apt-get --yes install freecad 
RUN ln -s /usr/lib/freecad/Mod /usr/lib/freecad-python3/Mod

RUN rm /usr/bin/python
RUN cp /usr/bin/python3 /usr/bin/python


RUN git clone https://github.com/makeclean/parametric-plasma-source.git

# Compile parametric plasma source
RUN cd /parametric-plasma-source/parametric_plasma_source && bash compile.sh

RUN git clone https://github.com/ukaea/openmc_workshop

WORKDIR /openmc_workshop