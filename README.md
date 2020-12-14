
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

- [Task 1 - Cross section plotting](insert_link)
- [Task 2 - Options for making materials](insert_link)
- [Task 3 - Building and visualising CSG geometry](insert_link)
- [Task 4 - Making neutron sources](insert_link)
- [Task 5 - TBR](insert_link)
- [Task 6 - DPA](insert_link)
- [Task 7 - Finding the neutron and photon spectra](insert_link)
- [Task 8 - Mesh tallies](insert_link)
- [Task 9 - Dose](insert_link)
- [Task 10 - Making CAD geometry](insert_link)
- [Task 11 - CAD simulations, fast flux](insert_link)
- [Task 12 - CAD simulations, mesh tallies, heat](insert_link)
- [Task 13 - Techniques for sampling parameter space](insert_link)
- [Task 14 - Techniques for parameter study optimisation](insert_link)

| **Task**                                     | **Keywords**                                                                                               |
|----------------------------------------------|------------------------------------------------------------------------------------------------------------|
| Task 1                                       | Nuclear data, cross-sections, MT numbers, Doppler broadening                                               |
| Task 2                                       | Materials, Neutronics Material Maker, Mixed materials                                                      |
| Task 3                                       | CSG geometry, Geometry visualisation                                                                       |
| Task 4                                       | Sources, Plasma sources, Parameteric Plasma Source, Neutron track visualisation                            |
| Task 5                                       | TBR, Cell tallies, Simulations                                                                             |
| Task 6                                       | DPA, Cell tallies, Simulations, Volume calculations                                                        |
| Task 7                                       | Neutron Spectra, Photon Spectra, Surface tallies, Energy filters, Flux, Current                            |
| Task 8                                       | Mesh tallies, 2D 3D Regular Mesh                                                                           |
| Task 9                                       | Dose tallies                                                                                               |
| Task 10                                      | CAD geometry, Paramak, Geometry visualisation                                                              |
| Task 11                                      | CAD-based neutronics, Heating, Mesh tallies                                                                |
| Task 12                                      | CAD-based neutronics, Paramak, DAGMC, Fast Flux, Cell tallies                                              |
| Task 13                                      | Sampling, Interpolation                                                                                    |
| Task 14                                      | Optimisation                                                                                               |

&ensp;
