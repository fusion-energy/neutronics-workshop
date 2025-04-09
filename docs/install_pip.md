# Install with pip

To install with pip first create a python 3.11 environment, then activate the
environment and install all the required packages.

This installation option supports Linux and has been tested most on Ubuntu

Currently just python 3.11 is supported, in the future other versions will be supported


```bash
python3.11 -m venv .neutronicsworkshop
```

Activate the virtual environmmet
```bash
source .neutronicsworkshop/bin/activate
```

Then install the dependencies
```bash
python3.11 -m pip install -r https://raw.githubusercontent.com/fusion-energy/neutronics-workshop/refs/heads/main/requirements.txt
```

Then you should be able to run the ```jupyterlab``` command and within Jupyter Lab you can load up the ipynb tasks found in the ```tasks``` folders.

```bash
jupyterlab
```

Then navigate to the task that you want to run in the tasks folder.
