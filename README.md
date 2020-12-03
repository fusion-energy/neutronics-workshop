
[![CircleCI](https://circleci.com/gh/ukaea/openmc_workshop.svg?style=svg)](https://circleci.com/gh/ukaea/openmc_workshop)
![dockerhub-publish](https://github.com/ukaea/openmc_workshop/workflows/dockerhub-publish/badge.svg)


# Fusion Neutronics workshop with OpenMC
A selection of resources for learning OpenMC with particular focus on
simulations relevant to fusion energy.

There are a few 
[slides](https://slides.com/openmc_workshop/neutronics_workshop) that introduce
the workshop and show the expected outputs of each task.

The use of OpenMC for neutronics analysis requires several software packages
and nuclear data. These have all been installed inside a Docker container.

<p align="center"><a href="https://www.youtube.com/embed/KdltE2Au_3c
" target="_blank"><img src="https://user-images.githubusercontent.com/8583900/101077155-54def400-359c-11eb-9d48-e0ace62aea40.png" height="400" /></a></p>

# History

The OpenMC workshop was created by and is maintained by Jonathan Shimwell
largely as a hobby project. John Billingsley has also made lots of great
contributions and
[others](https://github.com/ukaea/openmc_workshop/graphs/contributors) have
also also helped. The repository was originally made to teach university
students via workshops but also became useful for placement students.

The repository has benefitted greatly from user feedback. Please feel free to
raise Github issues if you spot anything that needs fixing. Contributions are
also welcome from as pull requests to the develop branch. 

The resource has proven most useful as it is one of the few open source and
accessable fusion neutronics training resources.

## Docker Container Installation

1. Install Docker CE for
[Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/),
[Mac OS](https://store.docker.com/editions/community/docker-ce-desktop-mac), or
[Windows](https://hub.docker.com/editions/community/docker-ce-desktop-windows),
including the part where you enable docker use as a non-root user.

2. Pull the docker image from the store by typing the following command in a
terminal window, or Windows users might prefer PowerShell.

    ```docker pull ukaea/openmcworkshop```

3. Now that you have the docker image you can enable graphics linking between
your os and docker, and then run the docker container by typing the following
commands in a terminal window.

    ```docker run -p 8888:8888 ukaea/openmcworkshop /bin/bash -c "jupyter notebook --notebook-dir=/tasks --ip='*' --port=8888 --no-browser --allow-root"```

4. A URL should be displayed in the terminal and can now be opened in the
internet browser of your choice

## Core workshop tasks

- [Task 1 - Cross section plotting - 25 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_1)
- [Task 2 - Building and visualizing the model geometry - 25 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_2)
- [Task 3 - Visualizing neutron tracks - 20 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_3)
- [Task 4 - Finding neutron interactions with mesh tallies - 15 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_4)
- [Task 5 - Finding the neutron and photon spectra - 15 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_5)
- [Task 6 - Finding the tritium production - 15 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_6)
- [Task 7 - Finding the neutron damage and stochastic volume calculation - 15 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_7)

## Optional workshop tasks

- [Task 8 - Techniques for sampling parameter space - 25 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_8)
- [Task 9 - Optimize a breeder blanket for tritium production - 25 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_9)
- [Task 10 - Using CAD geometry - 30 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_10)
- [Task 11 - Options for making materials - 20 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_11)
- [Task 12 - Unstructured mesh on CAD geometry- 20 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_12)

&ensp;
