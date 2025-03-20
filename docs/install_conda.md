# Install with Conda

It is also possible to install all the dependencies with Conda in a new environment.

This installation option supports Linux and has been tested most on Ubuntu

First install Miniconda or Anaconda, or Miniforge

- [Miniforge](https://github.com/conda-forge/miniforge) 
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- [Anaconda](https://www.anaconda.com)

Once you have a version of Conda installed then proceed with cloning the repository.

```bash
sudo apt-get install git
git clone https://github.com/fusion-energy/neutronics-workshop.git
```

Then create the environment with Conda.

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

Then navigate to the task that you want to run in the tasks folder.
