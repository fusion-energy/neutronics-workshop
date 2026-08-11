"""Tests that check the workshop dependencies are installed and that OpenMC can
run a simulation.

These tests deliberately need very little nuclear data so that they can be run
on operating systems where the whole workshop can not be run. The OpenMC wheels
for Windows and Mac OS don't include DAGMC so the CAD based tasks can't be run
there, but the CSG based parts of OpenMC still work.
"""

import importlib
import os
from pathlib import Path

import pytest

# packages from requirements.txt that the tasks import
PACKAGES = [
    "openmc",
    "cadquery",
    "paramak",
    "pyvista",
    "neutronics_material_maker",
    "openmc_source_plotter",
    "openmc_depletion_plotter",
    "openmc_data_downloader",
    "openmc_regular_mesh_plotter",
    "openmc_plasma_source",
    "cad_to_dagmc",
    "dagmc_h5m_file_inspector",
    "dagmc_geometry_slice_plotter",
]


def find_cross_sections():
    """Returns the path to a cross_sections.xml file or None if not found"""

    from_env = os.environ.get("OPENMC_CROSS_SECTIONS")
    candidates = [Path.home() / "nuclear_data" / "cross_sections.xml"]
    if from_env:
        candidates.insert(0, Path(from_env))

    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


@pytest.mark.parametrize("package", PACKAGES)
def test_package_imports(package):
    """Checks each of the packages used by the tasks can be imported"""

    importlib.import_module(package)


def test_openmc_version():
    """Checks OpenMC reports a version number"""

    import openmc

    assert openmc.__version__


def test_minimal_simulation(tmp_path):
    """Runs a small fixed source simulation of a lithium sphere and checks that
    tritium is produced. This checks the OpenMC transport code itself runs and
    not just the Python API."""

    import openmc

    cross_sections = find_cross_sections()
    if cross_sections is None:
        pytest.skip("no cross_sections.xml found, run the postBuild script")
    openmc.config["cross_sections"] = cross_sections

    breeder = openmc.Material()
    breeder.add_nuclide("Li6", 1)
    breeder.set_density("g/cm3", 2.0)

    sphere = openmc.Sphere(r=100, boundary_type="vacuum")
    cell = openmc.Cell(region=-sphere, fill=breeder)

    source = openmc.IndependentSource()
    source.space = openmc.stats.Point((0, 0, 0))
    source.energy = openmc.stats.Discrete([14e6], [1.0])

    settings = openmc.Settings()
    settings.run_mode = "fixed source"
    settings.batches = 2
    settings.particles = 500
    settings.source = source

    tally = openmc.Tally(name="tbr")
    tally.scores = ["H3-production"]

    model = openmc.Model(
        geometry=openmc.Geometry([cell]),
        materials=openmc.Materials([breeder]),
        settings=settings,
        tallies=openmc.Tallies([tally]),
    )

    statepoint_filename = model.run(cwd=tmp_path)

    with openmc.StatePoint(statepoint_filename) as statepoint:
        tbr = statepoint.get_tally(name="tbr").mean.flatten()[0]

    assert tbr > 0
