# Install with pip

## Install with pip on Linux

This installation option supports Linux.

You will need Python installed which comes pre installed on most Linux distributions.

````{admonition} WSL2 / minimal Linux users — extra system dependencies
:class: tip, dropdown

Most desktop Linux distributions already include the system libraries needed to run the simulations and graphics. However minimal environments such as WSL2 images may be missing some of them. If you hit missing library errors, install them with:

```bash
sudo apt-get install --yes git wget mpich libmpich12 libhdf5-310 libhdf5-mpich-310 hdf5-tools libnetcdf22 libtbb12 libglfw3 libglx0 libgl1 libglut3.12 libosmesa6 libgles2 libxft2 libxcursor1 libxinerama1 xvfb
```
````

In addition to install with pip you will need pip installed.
```
sudo apt-get --yes install python3-pip
```

I would also recommend installing python3-venv so that the dependencies can be installed into a virtual environment.
```
sudo apt-get --yes install python3-venv
```

Then proceed with cloning or [download](https://github.com/fusion-energy/neutronics-workshop/archive/refs/heads/main.zip) the repository.

```bash
sudo apt-get install git
git clone --depth 1 --branch main https://github.com/fusion-energy/neutronics-workshop.git
cd neutronics-workshop
```

You should then be able to make a virtual environment.
```bash
python3 -m venv .neutronicsworkshop
```

Activate the virtual environment
```bash
source .neutronicsworkshop/bin/activate
```

Then install the Python dependencies.

```bash
python3 -m pip install -r requirements.txt
```

The download the nuclear data. This will create a ```nuclear_data``` folder in your home directory and download several Gb of data needed for the simulations.

```bash
bash postBuild
```

Then you should be able to run the ```jupyter lab``` command and within Jupyter Lab you can load up the ipynb tasks found in the ```tasks``` folders.

```bash
jupyter lab
```

Then navigate to the task that you want to run in the tasks folder.


## Install with pip on Mac OS

This installation option supports Mac OS.

You will need Python 3 installed. The easiest way to get an up to date version is with [Homebrew](https://brew.sh).
```
brew install python
```

Alternatively, running ```python3``` in a terminal on a fresh Mac will prompt you to install the Xcode Command Line Tools, which also provide Python 3.

Unlike Linux, pip and venv come bundled with Python 3 on Mac OS, so no additional packages are needed.

Then proceed with cloning or [download](https://github.com/fusion-energy/neutronics-workshop/archive/refs/heads/main.zip) the repository. Git is included with the Xcode Command Line Tools, or can be installed with ```brew install git```.

```bash
git clone --depth 1 --branch main https://github.com/fusion-energy/neutronics-workshop.git
cd neutronics-workshop
```

You should then be able to make a virtual environment.
```bash
python3 -m venv .neutronicsworkshop
```

Activate the virtual environment
```bash
source .neutronicsworkshop/bin/activate
```

Then install the Python dependencies.

```bash
python3 -m pip install -r requirements.txt
```

The download the nuclear data. This will create a ```nuclear_data``` folder in your home directory and download several Gb of data needed for the simulations.

```bash
zsh postBuild
```

Then you should be able to run the ```jupyter lab``` command and within Jupyter Lab you can load up the ipynb tasks found in the ```tasks``` folders.

```bash
jupyter lab
```

Then navigate to the task that you want to run in the tasks folder.


## Install with pip on Windows

This installation option supports 64-bit Windows.

You will need **Python 3.12 or newer** installed, as the Windows ```openmc``` wheels are
only built for Python 3.12, 3.13 and 3.14. The easiest way to get it is from the
[python.org downloads page](https://www.python.org/downloads/windows/) or the Microsoft
Store. Make sure you tick *Add Python to PATH* in the installer.

pip and venv come bundled with Python 3 on Windows, so no additional packages are needed.

Then proceed with cloning or [download](https://github.com/fusion-energy/neutronics-workshop/archive/refs/heads/main.zip) the repository. Git for Windows can be installed from [git-scm.com](https://git-scm.com/download/win).

```powershell
git clone --depth 1 --branch main https://github.com/fusion-energy/neutronics-workshop.git
cd neutronics-workshop
```

You should then be able to make a virtual environment.
```powershell
py -3 -m venv .neutronicsworkshop
```

Activate the virtual environment. The remaining commands assume PowerShell.
```powershell
.neutronicsworkshop\Scripts\Activate.ps1
```

````{note}
If PowerShell blocks the activation script with an execution policy error, allow signed
local scripts for the current user with
```Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser``` and try again.
From the classic Command Prompt use ```.neutronicsworkshop\Scripts\activate.bat``` instead.
````

Then install the Python dependencies.

```powershell
python -m pip install -r requirements.txt
```

Then download the nuclear data. The ```postBuild``` script is written for bash, so run the
PowerShell equivalent below instead. This will create a ```nuclear_data``` folder in your
home directory and download several Gb of data needed for the simulations.

```powershell
$data = "$env:USERPROFILE\nuclear_data"
New-Item -ItemType Directory -Force -Path $data | Out-Null

# hiding the progress bar makes the large downloads much faster in Windows PowerShell
$ProgressPreference = 'SilentlyContinue'

# Download and extract the ENDF/b 8.0 chain file with the SFR branching ratios
download_chain -l endf -r b8.0 -b SFR -d $data -f chain-endf-b8.0.xml

# Download and extract the ENDF/b 8.0 cross section files
Invoke-WebRequest -Uri "https://anl.box.com/shared/static/uhbxlrx7hvxqw27psymfbhi7bx7s6u6a.xz" -OutFile "$data\endfb-viii.0-hdf5.tar.xz"
tar -C $data -xJf "$data\endfb-viii.0-hdf5.tar.xz"
Move-Item -Path "$data\endfb-viii.0-hdf5\*" -Destination $data -Force

# Download and extract the WMP Library
Invoke-WebRequest -Uri "https://github.com/mit-crpg/WMP_Library/releases/download/v1.1/WMP_Library_v1.1.tar.gz" -OutFile "$data\WMP_Library_v1.1.tar.gz"
tar -xzf "$data\WMP_Library_v1.1.tar.gz" -C $data
```

````{note}
```tar``` is included with Windows 10 (build 17063) and newer, so no extra download is
needed. The cross section archive is several Gb so the extraction step can take a while.
````

Then you should be able to run the ```jupyter lab``` command and within Jupyter Lab you can load up the ipynb tasks found in the ```tasks``` folders.

```powershell
jupyter lab
```

Then navigate to the task that you want to run in the tasks folder.
