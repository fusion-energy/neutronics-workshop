# This dockerfile is used by mybinder.org and other dockerfiles are located in the .devcontainer folder

# Pull your prebuilt image from GHCR
FROM ghcr.io/fusion-energy/neutronics-workshop:latest

# Define arguments for the non-root user (required by MyBinder)
ARG NB_USER=jovyan
ARG NB_UID=1000
ENV USER=${NB_USER}
ENV NB_UID=${NB_UID}
ENV HOME=/home/${NB_USER}

# Create the user and home directory as root, handling existing user cases
RUN if ! id -u ${NB_UID} > /dev/null 2>&1; then \
        useradd --uid ${NB_UID} -m ${NB_USER}; \
    fi && \
    mkdir -p ${HOME} && \
    chown -R ${NB_UID}:${NB_UID} ${HOME}

# Set the working directory
WORKDIR ${HOME}

# Switch to the non-root user
USER ${NB_USER}

# Copy repository contents to the home directory (optional)
COPY . ${HOME}