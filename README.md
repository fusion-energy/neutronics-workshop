
[![CircleCI](https://circleci.com/gh/ukaea/openmc_workshop.svg?style=svg)](https://circleci.com/gh/ukaea/openmc_workshop) Task 3 and Task 10  are currently failing the automated tests.

# Fusion Neutronics workshop with OpenMC
A selection of resources for learning OpenMC with particular focus on simulations relevant to fusion energy.

There are a few [slides](https://slides.com/openmc_workshop/neutronics_workshop) that introduce the workshop and show the expected outputs of each task.

The use of OpenMC for neutronics analysis requires several software packages and nuclear data. These have been installed inside a Docker container.

The majority of the workshop can also be completed using Binder notebooks or Google Colab Notebooks which do not require and installation and can be run online. Links are provided in the readme files for each task. Note - not all tasks can be completed in Colab as it lacks some required dependencies.

## Docker Container Installation

### Ubuntu (Recommended)

1. Install Docker CE for [Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/), [Mac OS](https://store.docker.com/editions/community/docker-ce-desktop-mac), or [Windows](https://hub.docker.com/editions/community/docker-ce-desktop-windows), including the part where you enable docker use as a non-root user.

2. Pull the docker image from the store by typing the following command in a terminal window, or Windows user might prefer PowerShell.

    ```docker pull openmcworkshop/workshop_jupyter```

3. Now that you have the docker image you can enable graphics linking between your os and docker, and then run the docker container by typing the following commands in a terminal window.

    ```docker run -p 8888:8888 openmcworkshop/workshop_jupyter```


**IMPORTANT:** Any changes you make to scripts in the docker container will be lost when you exit the container. Make sure you copy any files you want to keep into the ```my_openmc_workshop``` folder before exiting the container. **Note:** The output files created by the task scripts are automatically copied to this folder.

## Core workshop tasks

- [Task 1 - Cross section plotting - 25 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_1)
- [Task 2 - Building and visualizing the model geometry - 25 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_2)
- [Task 3 - Visualizing neutron tracks - 20 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_3)
- [Task 4 - Finding neutron interactions with mesh tallies - 15 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_4)
- [Task 5 - Finding the neutron and photon spectra - 15 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_5)
- [Task 6 - Finding the tritium production - 15 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_6)
- [Task 7 - Finding the neutron damage and stochastic volume calculation - 15 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_7)

## Optional workshop tasks

- [Task 8 - Survey breeder blanket designs for tritium production - 25 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_8)
- [Task 9 - Optimize a breeder blanket for tritium production - 25 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_9)
- [Task 10 - Using CAD geometry - 30 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_10)
- [Task 11 - Options for making materials - 20 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_11)
- [Task 12 - Unstructured mesh on CAD geometry- 20 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_12)

&ensp;
