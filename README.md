
[![CircleCI](https://circleci.com/gh/fusion-energy/neutronics-workshop/tree/main.svg?style=svg)](https://circleci.com/gh/fusion-energy/neutronics-workshop/tree/main)

[![docker-publish-release](https://github.com/fusion-energy/neutronics-workshop/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/fusion-energy/neutronics-workshop/actions/workflows/docker-publish.yml)

# Fusion Neutronics workshop
A selection of resources for learning fusion neutronics simulations with a
particular focus on OpenMC with DAGMC and the Paramak

There are a few 
[slides](https://slides.com/neutronics-workshop/neutronics_workshop) that introduce
the workshop and show the expected outputs of each task.

The use of OpenMC for neutronics analysis requires several software packages
and nuclear data. These have all been installed inside a Docker container.
The video below gives a brief explainer of what to exspect in the workshop and
some motivation for learning neutronics.

<p align="center"><a href="https://youtu.be/gcZo7ZPtPr8" target="_blank"><img src="https://user-images.githubusercontent.com/8583900/101077155-54def400-359c-11eb-9d48-e0ace62aea40.png" height="400" /></a></p>



# History

The neutronics workshop was created by and is maintained by Jonathan Shimwell
largely as a hobby project. John Billingsley has also made lots of great
contributions and
[others](https://github.com/fusion-energy/neutronics-workshop/graphs/contributors) have
also also helped. The repository was originally made to teach university
students via workshops but also became useful for placement students.

The repository has benefited greatly from user feedback. Please feel free to
raise Github issues if you spot anything that needs fixing. Contributions are
also welcome as pull requests to the develop branch. 

The resource has proven most useful as it is one of the few open source and
accessible fusion neutronics training resources.



## Installation

There are video tutorials for this section which accompany the step by step
instructions below.
- Ubuntu installation video :point_right: <p align="center"><a href="https://youtu.be/PqIb5MZKyGA" target="_blank"><img src="https://user-images.githubusercontent.com/8583900/114008054-c9cb7e80-9859-11eb-8e07-32e95c600667.png" height="70" /></a></p>
- Windows installation video :point_right: <p align="center"><a href="https://youtu.be/WltgKuTNxmE" target="_blank"><img src="https://user-images.githubusercontent.com/8583900/114008108-d3ed7d00-9859-11eb-8bb5-0c19ce775015.png" height="70" /></a></p>
- Mac installation video :point_right: <p align="center"><a href="https://www.youtube.com/watch?v=wPk3BenK-Qk" target="_blank"><img src="https://user-images.githubusercontent.com/8583900/114172031-05834880-992d-11eb-8277-5a6cda2b5e12.png" height="70" /></a></p>

1. Install Docker CE for
[Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/),
[Mac OS](https://store.docker.com/editions/community/docker-ce-desktop-mac), or
[Windows](https://hub.docker.com/editions/community/docker-ce-desktop-windows),
including the part where you enable docker use as a non-root user. 


2. Pull the docker image from the store by typing the following command in a
terminal window, or Windows users might prefer PowerShell.

    ```docker pull ghcr.io/fusion-energy/neutronics-workshop```

3. Now that you have the docker image you can enable graphics linking between
your os and docker, and then run the docker container by typing the following
commands in a terminal window.

    ```docker run -p 8888:8888 ghcr.io/fusion-energy/neutronics-workshop```

4. A URL should be displayed in the terminal and can now be opened in the
internet browser of your choice. Select and open the URL at the end of the terminal print out (highlighted below)

<p align="center"><img src="https://user-images.githubusercontent.com/8583900/114006504-6725b300-9858-11eb-905f-b7b2f26a0113.png" height="200" /></p>

5. Some tasks require the use of Paraview to view the 3D meshes produced.
Parview can be download from [here](https://www.paraview.org/download/).
    <details>
      <summary><b>Expand</b> - Ubuntu terminal commands for Paraview install</summary>
        <pre><code class="language-html">
        sudo apt update && sudo apt-get install paraview
        </code></pre>
    </details>

6. Some tasks require the use of CAD software to view the 3D geometry produced.
FreeCAD is one option for this and can be downloaded [here](https://www.freecadweb.org/downloads.php).
    <details>
        <summary><b>Expand</b> - Ubuntu terminal commands for FreeCAD install</summary>
            <pre><code class="language-html">
            sudo apt update && sudo apt-get install freecad
            </code></pre>
    </details>

## Workshop tasks

The task videos are all avaialbe on a nice [Gather Town](https://gather.town/app/QnHxhg6bPf8KQdii/openmc-workshop) 
map which is great for working through the workshop with collegues.

| Tasks | Keywords | Video(s) |
|-|-|-|
| [Task 1 - Cross sections](https://github.com/fusion-energy/neutronics-workshop/tree/main/tasks/task_01_cross_sections) | Nuclear data, cross-sections, MT numbers, Doppler | [link1](https://youtu.be/eBZ2lY_2v7I)  [link2](https://youtu.be/ELZNeIdSuMY) [link3](https://youtu.be/ec5BLLL6Q_g) [link4](https://youtu.be/mkl1mVnTO6g) |
| [Task 2 - Materials](https://github.com/fusion-energy/neutronics-workshop/tree/main/tasks/task_02_making_materials) | Materials, Neutronics Material Maker, Mixed materials | [link](https://youtu.be/-NGnY-1TWCA) |
| [Task 3 - CSG geometry](https://github.com/fusion-energy/neutronics-workshop/tree/main/tasks/task_03_making_CSG_geometry) | CSG geometry, Geometry visualisation | [link](https://youtu.be/Ovr7oYukYRw) |
| [Task 4 - Sources](https://github.com/fusion-energy/neutronics-workshop/tree/main/tasks/task_04_make_sources) | Neutron point sources, Gamma sources, Plasma sources, Neutron track visualisation | [link](https://youtu.be/j9dT1Viqcu4) |
| [Task 5 - TBR](https://github.com/fusion-energy/neutronics-workshop/tree/main/tasks/task_05_CSG_cell_tally_TBR) | Tritium Breeding Ratio, Cell tallies, Simulations | [link](https://youtu.be/Vc7Qy7QW4o8) |
| [Task 6 - DPA](https://github.com/fusion-energy/neutronics-workshop/tree/main/tasks/task_06_CSG_cell_tally_DPA) | Displacements Per Atom, Cell tallies, Simulations, Volume calculations | [link](https://youtu.be/VLn59FSc4GA) |
| [Task 7 - Neutron and photon spectra](https://github.com/fusion-energy/neutronics-workshop/tree/main/tasks/task_07_CSG_cell_tally_spectra) | Neutron Spectra, Photon Spectra, Cell tallies, Energy group structures, Flux, Current | [link](https://youtu.be/qHqAuqMLYPA) |
| [Task 8 - Mesh tallies](https://github.com/fusion-energy/neutronics-workshop/tree/main/tasks/task_08_CSG_mesh_tally) | Mesh tallies, Structured meshes | [link](https://youtu.be/KYIsDjip1nQ) |
| [Task 9 - Dose](https://github.com/fusion-energy/neutronics-workshop/tree/main/tasks/task_09_CSG_surface_tally_dose) | Dose, Cell tallies, Dose coefficients |  |
| [Task 10 - Making CAD geometry](https://github.com/fusion-energy/neutronics-workshop/tree/main/tasks/task_10_making_CAD_geometry) | Parametric CAD geometry, Paramak, Geometry visualisation | [link](https://www.youtube.com/watch?v=Bn_TcJSOvaA) |
| [Task 11 - CAD Cell tallies](https://github.com/fusion-energy/neutronics-workshop/tree/main/tasks/task_11_CAD_mesh_tally_heat) | CAD-based neutronics, Cell tallies, DAGMC, Heating |  |
| [Task 12 - CAD Mesh tallies](https://github.com/fusion-energy/neutronics-workshop/tree/main/tasks/task_12_CAD_cell_tally_fast_flux) | CAD-based neutronics, Mesh tallies, Paramak, DAGMC, Fast flux |  |
| [Task 13 - Techniques for sampling parameter space](https://github.com/fusion-energy/neutronics-workshop/tree/main/tasks/task_13_parameter_study_sampling) | Sampling, Interpolation, Multi-dimensional parameter studies |  |
| [Task 14 - Parameter study optimisation](https://github.com/fusion-energy/neutronics-workshop/tree/main/tasks/task_14_parameter_study_optimisation) | Data science machine learning approaches |  |
