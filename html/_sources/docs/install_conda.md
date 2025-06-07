# Install with Conda

It is also possible to install all the dependencies with Conda in a new environment.

Please note this method uses the latest stable Conda release of OpenMC. **Some of the tasks require the development version of OpenMC**. The PIP or Docker method make use of this newer development version of OpenMC.

This installation option supports Linux and has been tested most on Ubuntu

First install Miniconda or Anaconda, or Miniforge

- [Miniforge](https://github.com/conda-forge/miniforge) 
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- [Anaconda](https://www.anaconda.com)

Once you have a version of Conda installed then proceed with cloning or [download](https://github.com/fusion-energy/neutronics-workshop/archive/refs/heads/main.zip) the repository.

```bash
sudo apt-get install git
git clone https://github.com/fusion-energy/neutronics-workshop.git
cd neutronics-workshop
```

Then create the environment with Conda.

```bash
conda env create --name neutronicsworkshop --file=environment.yml
```

Then activate the environment with  
```bash
conda activate neutronicsworkshop
```

The download the nuclear data. This will create a ```nuclear_data``` folder in your home directory and download several Gb of data needed for the simulations
```bash
bash postBuild
```


Then you should be able to run the ```jupyter lab``` command and within Jupyter Lab you can load up the ipynb tasks found in the ```tasks``` folders.

```bash
jupyter lab
```

Then navigate to the task that you want to run in the tasks folder.
