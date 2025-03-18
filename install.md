
# Local Installation

There are several ways to run the neutronics-workshop tasks including Conda, Docker and Codespaces.

## Install with pip

To install with pip first create a python 3.11 environment, then activate the
environment and install all the required packages. Currently just python 3.11
is supported, in the future other versions will be supported



```bash
python3.11 -m venv .neutronicsworkshop
```

Activate the virtual environmmet
```bash
source .neutronicsworkshop/bin/activate
```

Then install the dependancies
```bash
python3.11 -m pip install -r requirements.txt 
```

Then you should be able to run the ```jupyterlab``` command and within Jupyter Lab you can load up the ipynb tasks found in the ```tasks``` folders.

```bash
jupyterlab
```

## Install with Conda

It is also possible to install all the dependencies with Conda / Mamba in a new environment.

First install Miniconda or Anaconda, or Miniforge

- [Miniforge](https://github.com/conda-forge/miniforge) recommended as it includes Mamba 
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- [Anaconda](https://www.anaconda.com)

Once you have a version of Mamba or Conda installed then proceed with cloning the repository.
```bash
sudo apt-get install git
git clone https://github.com/fusion-energy/neutronics-workshop.git
```

Then create the environment with Conda. If you have Mamba installed you could substitute mamba in for conda in the following command.

```bash
conda env create --name neutronicsworkshop --file=environment.yml
```

The download the nuclear data. This will create a ```nuclear_data``` folder in your home directory and download several Gb of data needed for the simulations
```bash
bash postBuild
```

Then activate the environment with  
```bash
conda activate neutronicsworkshop
```

Then you should be able to run the ```jupyterlab``` command and within Jupyter Lab you can load up the ipynb tasks found in the ```tasks``` folders.

```bash
jupyterlab
```


## Install with Docker

There are video tutorials for this section which accompany the step by step
instructions below.
- Ubuntu installation video :point_right: <p align="center"><a href="https://youtu.be/qJLmt_dAaC0" target="_blank"><img src="https://user-images.githubusercontent.com/8583900/114008054-c9cb7e80-9859-11eb-8e07-32e95c600667.png" height="70" /></a></p>
- Windows installation video :point_right: <p align="center"><a href="https://youtu.be/1MUYgjEQeIA" target="_blank"><img src="https://user-images.githubusercontent.com/8583900/114008108-d3ed7d00-9859-11eb-8bb5-0c19ce775015.png" height="70" /></a></p>
- Mac installation video :point_right: <p align="center"><a href="https://youtu.be/jUMY-cEILcw" target="_blank"><img src="https://user-images.githubusercontent.com/8583900/114172031-05834880-992d-11eb-8277-5a6cda2b5e12.png" height="70" /></a></p>

1. Install Docker CE for
[Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/),
[Mac OS](https://store.docker.com/editions/community/docker-ce-desktop-mac), or
[Windows](https://hub.docker.com/editions/community/docker-ce-desktop-windows),
including the part where you enable docker use as a non-root user. 

2. Pull the docker image from the store by typing the following command in a
terminal window, or Windows users might prefer PowerShell.

    ```docker pull ghcr.io/fusion-energy/neutronics-workshop```

    <details>
      <summary><b>Expand</b> - Having permission denied errors?</summary>
        <pre><code class="language-html">
        If you are running the command from Linux or Ubuntu terminal and getting permission denied messages back.
        Try running the same command with with elevated user permissions by adding sudo at the front.
        sudo docker pull ghcr.io/fusion-energy/neutronics-workshop
        Then enter your password when prompted.
        </code></pre>
    </details>

3. Now that you have the docker image you can enable graphics linking between
your os and docker, and then run the docker container by typing the following
commands in a terminal window.

    ```docker run -p 8888:8888 ghcr.io/fusion-energy/neutronics-workshop```

    <details>
      <summary><b>Expand</b> - Having permission denied errors?</summary>
        <pre><code class="language-html">
        If you are running the command from Linux or Ubuntu terminal and getting permission denied messages back.
        Try running the same command with elevated user permissions by adding sudo at the front.
        sudo docker run -p 8888:8888 ghcr.io/fusion-energy/neutronics-workshop
        Then enter your password when prompted.
        </code></pre>
    </details>

4. A URL should be displayed in the terminal and can now be opened in the
internet browser of your choice. Select and open the URL at the end of the terminal printout (highlighted below)

<p align="center"><img src="https://user-images.githubusercontent.com/8583900/144759522-5306e61e-e30d-45e0-bb1a-ea8360e8c6da.png" width="70%" /></p>

To check the tasks run try opening the first task in the half day workshop folder and running the Jupyter Lab code (either click on the triangular run button or click on the first code cell and press shift and enter to execute that cell).

# Optional Packages for Local Installation

This is not required for the half day workshop but some of the more advanced tasks do require Paraview and or FreeCAD.

1. Some tasks require the use of Paraview to view the 3D meshes produced.
Parview can be downloaded from [here](https://www.paraview.org/download/).
    <details>
      <summary><b>Expand</b> - Ubuntu terminal commands for Paraview install</summary>
        <pre><code class="language-html">
        sudo apt update && sudo apt-get install paraview
        </code></pre>
    </details>

2. Some tasks require the use of CAD software to view the 3D geometry produced.
FreeCAD is one option for this and can be downloaded [here](https://www.freecadweb.org/downloads.php).
    <details>
        <summary><b>Expand</b> - Ubuntu terminal commands for FreeCAD install</summary>
            <pre><code class="language-html">
            sudo apt update && sudo apt-get install freecad
            </code></pre>
    </details>


# Run in the cloud

The repository is also ready for deployment on GitHub Codespaces which allows
users to launch the containerized environment on more powerful cloud computers
without installing anything locally.

- To get started sign up to codespaces :point_right: [codespaces](https://github.com/features/codespaces)

- Then follow :point_right: [this link](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=386229912) to config a compute instance :point_right: <p align="center"><a href="https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=386229912" target="_blank"><img src="https://user-images.githubusercontent.com/8583900/179179958-cc7f0700-6df5-47e9-a10f-67a9c1e556c6.png" height="150" /></a></p>

- VS Code will then launch in the browser, once loaded you must select the conda python interpreter to enable the correct Python environment.


# Build the book

To create the jupyter book ensure you have the required environment then build with Jupyter book.

```bash
jupyter-book build tasks
```
