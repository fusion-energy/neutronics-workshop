
[![CircleCI](https://circleci.com/gh/ukaea/openmc_workshop.svg?style=svg)](https://circleci.com/gh/ukaea/openmc_workshop)
[![dockerhub-publish](https://github.com/ukaea/openmc_workshop/workflows/dockerhub-publish/badge.svg)](https://github.com/ukaea/openmc_workshop/actions?query=workflow%3Adockerhub-publish)


# Fusion Neutronics workshop with OpenMC
A selection of resources for learning OpenMC with particular focus on
simulations relevant to fusion energy.

There are a few 
[slides](https://slides.com/openmc_workshop/neutronics_workshop) that introduce
the workshop and show the expected outputs of each task.

The use of OpenMC for neutronics analysis requires several software packages
and nuclear data. These have all been installed inside a Docker container.

<p align="center"><a href="https://youtu.be/gcZo7ZPtPr8" target="_blank"><img src="https://user-images.githubusercontent.com/8583900/101077155-54def400-359c-11eb-9d48-e0ace62aea40.png" height="400" /></a></p>

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
internet browser of your choice. Select and open the URL at the end of the terminal print out (highlighted below)

![url_to_select](https://user-images.githubusercontent.com/8583900/103912503-4a65cc00-50ff-11eb-87db-ebe26a313fd6.png)

5. Some tasks require the use of Paraview to view the 3D meshes produced.
Parview can be download from [here](https://www.paraview.org/download/)
    <details>
      <summary>Ubuntu terminal commands for Paraview install</summary>
        <pre><code class="language-html">
        sudo apt update && sudo apt-get install paraview
        </code></pre>
    </details>

6. Some tasks require the use of CAD software to view the 3D geometry produced.
FreeCAD is one option for this and can be downloaded [here](https://www.freecadweb.org/downloads.php)
    <details>
        <summary>Ubuntu terminal commands for FreeCAD install</summary>
            <pre><code class="language-html">
            sudo apt update && sudo apt-get install freecad
            </code></pre>
    </details>

## Workshop tasks

| **Task**                                            | **Keywords**                                                                                               |
|-----------------------------------------------------|------------------------------------------------------------------------------------------------------------|
| [Task 1 - Cross section plotting](https://github.com/ukaea/openmc_workshop/tree/main/tasks/task_01_cross_sections)                   | Nuclear data, cross-sections, MT numbers, Doppler broadening                                               |
| [Task 2 - Options for making materials](https://github.com/ukaea/openmc_workshop/tree/main/tasks/task_02_making_materials)             | Materials, Neutronics Material Maker, Mixed materials                                                      |
| [Task 3 - Building and visualising CSG geometry](https://github.com/ukaea/openmc_workshop/tree/main/tasks/task_03_making_CSG_geometry)    | CSG geometry, Geometry visualisation                                                                       |
| [Task 4 - Making neutron sources](https://github.com/ukaea/openmc_workshop/tree/main/tasks/task_04_make_sources)                   | Neutron point sources, Gamma sources, Plasma sources, Neutron track visualisation                            |
| [Task 5 - TBR](https://github.com/ukaea/openmc_workshop/tree/main/tasks/task_05_CSG_cell_tally_TBR)                                      | Tritium Breeding Ratio, Cell tallies, Simulations                                                                             |
| [Task 6 - DPA](https://github.com/ukaea/openmc_workshop/tree/main/tasks/task_06_CSG_cell_tally_DPA)                                      | Displacements Per Atom, Cell tallies, Simulations, Volume calculations                                                        |
| [Task 7 - Finding the neutron and photon spectra](https://github.com/ukaea/openmc_workshop/tree/main/tasks/task_07_CSG_cell_tally_spectra)   | Neutron Spectra, Photon Spectra, Cell tallies, Energy group structures, Flux, Current                            |
| [Task 8 - Mesh tallies](https://github.com/ukaea/openmc_workshop/tree/main/tasks/task_08_CSG_mesh_tally)                             | Mesh tallies, Structured meshes                                                                           |
| [Task 9 - Dose](https://github.com/ukaea/openmc_workshop/tree/main/tasks/task_09_CSG_surface_tally_dose)                                     | Dose, Cell tallies, Dose coefficients                                                                                               |
| [Task 10 - Making CAD geometry](https://github.com/ukaea/openmc_workshop/tree/main/tasks/task_10_making_CAD_geometry)                     | Parametric CAD geometry, Paramak, Geometry visualisation                                                              |
| [Task 11 - CAD simulations - Heating](https://github.com/ukaea/openmc_workshop/tree/main/tasks/task_11_CAD_mesh_tally_heat)               | CAD-based neutronics, DAGMC, Heating, Unstructured meshes                                                                |
| [Task 12 - CAD simulations - Fast flux](https://github.com/ukaea/openmc_workshop/tree/main/tasks/task_12_CAD_cell_tally_fast_flux)             | CAD-based neutronics, Paramak, DAGMC, Fast flux, Cell tallies                                              |
| [Task 13 - Techniques for sampling parameter space](https://github.com/ukaea/openmc_workshop/tree/main/tasks/task_13_parameter_study_sampling) | Sampling, Interpolation, Multi-dimensional parameter stidues                                                                                    |
| [Task 14 - Parameter study optimisation](https://github.com/ukaea/openmc_workshop/tree/main/tasks/task_14_parameter_study_optimisation)            | Data science machine learning approaches                                                                                               |

&ensp;
