# Install with pip

## Install with pip on Linux

This installation option supports Linux.

You will need Python installed which comes pre installed on most Linux distributions.

````{admonition} Minimal Linux installs — extra system dependencies
:class: tip, dropdown

Most desktop Linux distributions already include the system libraries needed to run the simulations and graphics. However minimal environments such as container or server images may be missing some of them. If you hit missing library errors, install them with:

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


## Install with pip on Windows (native)

This installation option supports 64-bit Windows and runs everything directly in Windows,
with no Linux layer involved. If you would rather run the Linux version of the workshop
inside Windows then see *Install with pip on Windows (WSL2)* below.

You will need Python 3 installed. The easiest way to get an up to date version is from the
[python.org downloads page](https://www.python.org/downloads/windows/) or the Microsoft
Store. Make sure you tick *Add Python to PATH* in the installer.

Unlike Linux, pip and venv come bundled with Python 3 on Windows, so no additional packages are needed.

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

Then you should be able to run the ```jupyter lab``` command and within Jupyter Lab you can load up the ipynb tasks found in the ```tasks``` folders.

```powershell
jupyter lab
```

Then navigate to the task that you want to run in the tasks folder.


## Install with pip on Windows (WSL2)

This installation option also supports 64-bit Windows, but runs the Linux version of the
workshop inside Windows using the Windows Subsystem for Linux.

First install WSL2 by opening PowerShell **as Administrator** and running the following,
then reboot when prompted. This installs Ubuntu by default.

```powershell
wsl --install
```

Once rebooted, open the *Ubuntu* app from the Start menu and set your Linux username and
password when prompted. Everything from here on is typed into that Ubuntu terminal rather
than into PowerShell.

WSL2 images are minimal, so unlike a desktop Linux install they are missing several of the
system libraries needed to run the simulations and graphics. Install them with:

```bash
sudo apt-get update
sudo apt-get install --yes git wget mpich libmpich12 libhdf5-310 libhdf5-mpich-310 hdf5-tools libnetcdf22 libtbb12 libglfw3 libglx0 libgl1 libglut3.12 libosmesa6 libgles2 libxft2 libxcursor1 libxinerama1 xvfb
```

Then follow the *Install with pip on Linux* instructions above, starting from the
```python3-pip``` step.

````{note}
Keep the repository inside the Linux file system, for example under ```~/```, rather than
under ```/mnt/c/```. Working across the Windows file system boundary makes the simulations
noticeably slower.
````

When you run ```jupyter lab``` in the Ubuntu terminal it will print a
```http://localhost:8888/...``` URL with a token. Open that URL in your normal Windows web
browser.
