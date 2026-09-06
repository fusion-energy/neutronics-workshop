# Install & nuclear data

Two independent things to set up: (1) the Python packages (OpenMC + ecosystem), (2) the nuclear data files (cross sections + depletion chain). OpenMC will fail loudly with a clear error if data is missing.

## Installing OpenMC + ecosystem via pip

The workshop pins an extra-index URL that serves pre-built `openmc` wheels **with DAGMC support** already compiled in, plus the surrounding fusion-neutronics packages:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install --extra-index-url https://shimwell.github.io/wheels \
    openmc \
    cad_to_dagmc \
    paramak \
    cadquery \
    openmc_data \
    openmc_data_downloader \
    openmc-plasma-source \
    openmc_source_plotter \
    openmc_depletion_plotter \
    openmc_regular_mesh_plotter \
    "neutronics_material_maker[density]"
```

The full list lives in `requirements.txt` at the repo root. The `--extra-index-url` must be kept — without it, pip will either install a CPU-only OpenMC without DAGMC, or fail to resolve `openmc` at all on some platforms.

### Alternative: conda

```bash
mamba env create -f environment.yml
mamba activate neutronics-workshop
```

The conda-forge `openmc` builds also include DAGMC on Linux/macOS.

### From source

See `install_scripts/compile_install_ubuntu_22.04.sh` — only needed if you want a newer-than-wheel OpenMC, embree-accelerated DAGMC, or custom build flags.

## Nuclear data — three options

OpenMC needs a `cross_sections.xml` that points at HDF5 cross-section files. Depletion additionally needs a `chain_file` (decay + branching data). Pick one of:

### Option A — direct download from openmc.org/data (simplest)

The OpenMC project hosts pre-built HDF5 tarballs:

```bash
mkdir -p ~/nuclear_data && cd ~/nuclear_data

# ENDF/B-VIII.0 neutron + photon library (~2 GB)
wget -q -O - https://anl.box.com/shared/static/uhbxlrx7hvxqw27psymfbhi7bx7s6u6a.xz | tar -xJ
mv endfb-viii.0-hdf5/* .

# Or browse https://openmc.org/data/ for other libraries (TENDL, JEFF, ENDF/B-VII.1)
```

Then:

```python
openmc.config['cross_sections'] = '~/nuclear_data/cross_sections.xml'
```

### Option B — `openmc_data` package (recommended for depletion)

Provides **scripted downloads** for both cross sections and chain files, with branching-ratio options:

```bash
pip install openmc_data

# depletion chain (ENDF/B-VIII.0 with SFR branching ratios) — required for depletion
download_chain -l endf -r b8.0 -b SFR -d ~/nuclear_data -f chain-endf-b8.0.xml

# full NNDC library (neutron transport data)
download_nndc -d ~/nuclear_data -r b8.0
```

Available helpers vary by `openmc_data` version; `download_chain` and `download_endf_chain` are the two used by this workshop (see `postBuild` and the depletion tasks). For the current full list, run `pip show -f openmc_data | grep bin/` or check the upstream repo.

### Option C — `openmc_data_downloader` (incremental / selective)

Downloads only the isotopes you need, which is useful if your material list is small and you want to avoid the full ~2 GB:

```bash
pip install openmc_data_downloader

# all elements relevant to a concrete shielded room
openmc_data_downloader -d ~/nuclear_data \
    -l ENDFB-8.0-NNDC \
    -p neutron photon \
    -e H C O N Na Mg Al Si K Ca Fe \
    --no-overwrite
```

## Telling OpenMC where the data lives

Three equivalent methods, in order of preference:

```python
# 1. In-script (explicit, survives shell restart)
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'
openmc.config['chain_file']     = Path.home() / 'nuclear_data' / 'chain-endf-b8.0.xml'

# 2. Environment variables (picked up automatically by OpenMC)
# export OPENMC_CROSS_SECTIONS=~/nuclear_data/cross_sections.xml
# export OPENMC_CHAIN_FILE=~/nuclear_data/chain-endf-b8.0.xml

# 3. openmc.config dict persists across Model objects in one Python session
```

## Verifying the install

```python
import openmc
import openmc.lib                          # importing this loads the compiled shared library
print(openmc.__version__)
print(openmc.config)                       # should show cross_sections path
print('DAGMC enabled:', openmc.lib._dagmc_enabled())
```

For a DAGMC file:

```python
u = openmc.DAGMCUniverse(filename='dagmc.h5m')
print(u.material_names)                    # should list the material tags
```

## Common install failures

- **`OSError: libopenmc.so: cannot open shared object file`** on `import openmc.lib` — the wheel didn't install cleanly. Re-install with `--force-reinstall --no-cache-dir --extra-index-url https://shimwell.github.io/wheels openmc`.
- **`Cross section <nuclide> not found in library`** — either the library doesn't contain that nuclide (use `openmc_data_downloader` to fetch it) or `cross_sections.xml` points at a library that excludes it. ENDF/B-VIII.0 covers most fusion-relevant isotopes; TENDL-2019 has broader coverage for activation products.
- **Depletion error `no chain file set`** — set `openmc.config['chain_file']` before calling `mat.deplete(...)` or creating a `CoupledOperator`.
