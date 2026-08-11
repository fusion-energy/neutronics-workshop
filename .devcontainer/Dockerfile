# This Dockerfile creates an enviroment / dependencies needed to run the
# neutronics-workshop.

# This Dockerfile can be build locally or a prebuild image can be downloaded

# To download the prebuild image
# docker pull ghcr.io/fusion-energy/neutronics-workshop

# To build this Dockerfile into a docker image:
# docker build -t ghcr.io/fusion-energy/neutronics-workshop -f .devcontainer/Dockerfile .

# to launch the docker image run with this command
# docker run -p 8888:8888 ghcr.io/fusion-energy/neutronics-workshop

# to push to github container repository, generate an access token
# https://github.com/settings/tokens

# login to ghcr
# echo ghp_yourgithubtoken | docker login ghcr.io -u yourgithubusername --password-stdin

# push the docker image to ghcr 
# docker push ghcr.io/fusion-energy/neutronics-workshop

FROM mcr.microsoft.com/devcontainers/base:bookworm AS dependencies

RUN apt-get --allow-releaseinfo-change update
RUN apt-get --yes update && apt-get --yes upgrade

# perhaps libnetcdf13 is needed for unstructured meshes in openmc
# RUN apt-get --yes install libnetcdf13

                          # eigen3 needed for DAGMC
RUN apt-get --yes install libeigen3-dev \
                          git \
                          wget \
                          mpich \
                          libmpich-dev \
                          libhdf5-serial-dev \
                          libhdf5-mpich-dev \
                          hdf5-tools \
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
                          libxinerama-dev \
                          # needed for pyvista
                          xvfb \
                          libgl1-mesa-glx \
                          libgl1-mesa-dri \
                          libosmesa6-dev \
                          libgl1-mesa-dev

RUN apt-get --yes install python3-pip python3-venv

# Enabling a venv within Docker is needed to avoid system wide installs
# https://pythonspeed.com/articles/activate-virtualenv-dockerfile/
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --upgrade pip

COPY requirements.txt requirements.txt


# python packages from the neutronics workflow
RUN pip install -r requirements.txt



ENV DISPLAY=:99
ENV PORT=8888

# default username for mybinder
ARG NB_USER=jovyan
ARG NB_UID=1000
ENV USER=${NB_USER}
ENV NB_UID=${NB_UID}
ENV HOME=/home/${NB_USER}

# Create the user and set up home directory
RUN if ! id -u ${NB_UID} > /dev/null 2>&1; then \
        useradd --uid ${NB_UID} -m ${NB_USER}; \
    fi && \
    mkdir -p ${HOME} && \
    chown -R ${NB_UID}:${NB_UID} ${HOME} && \
    echo "${NB_USER}:x:${NB_UID}:${NB_UID}:${NB_USER},,,:${HOME}:/bin/bash" >> /etc/passwd

RUN mkdir -p ${HOME}/tasks && \
    chown -R ${NB_UID}:${NB_UID} ${HOME}/tasks && \
    chmod -R u+rwx ${HOME}/tasks


COPY postBuild postBuild
RUN python postBuild

WORKDIR ${HOME}/tasks

RUN echo ${HOME}


# Copy over the local repository files
COPY tasks ${HOME}/tasks/

RUN chown -R ${NB_UID}:${NB_UID} /root
RUN chown -R ${NB_UID}:${NB_UID} ${HOME}/tasks

USER ${NB_USER}

# could switch to --ip='*'
CMD ["jupyter", "lab", "--notebook-dir=/home/jovyan/tasks", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]
