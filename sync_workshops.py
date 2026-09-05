#!/usr/bin/env python3
"""Sync or validate workshop folders against source task notebooks.

Each workshop task is copied into its own subfolder (e.g. ``task_01/``) inside
the workshop directory. The subfolder holds the notebook (named after the
folder, e.g. ``task_01/task_01.ipynb``) together with any extra data files the
notebook needs (DAGMC ``.h5m`` files, meshes, CAD ``.step`` files, ...).

Giving every task its own folder keeps the run-time outputs of one task (for
example ``statepoint.h5`` and ``summary.h5``) from overwriting those of another.

Each task is defined as a tuple of::

    (folder_name, source_notebook, [extra_source_files])

Paths are relative to the ``tasks`` directory. The notebook is written into
``<workshop>/<folder_name>/<folder_name>.ipynb`` and each extra file is copied
into the same folder keeping its original basename.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import shutil

import nbformat

WORKSHOPS = {
    'half-day-university-workshop': [
        ('task_01', 'task_01_cross_sections/1_isotope_xs_plot.ipynb', []),
        ('task_02', 'task_01_cross_sections/2_element_xs_plot.ipynb', []),
        ('task_03', 'task_01_cross_sections/3_material_xs_plot.ipynb', []),
        ('task_04', 'task_02_making_materials/1_example_materials_from_isotopes.ipynb', []),
        ('task_05', 'task_02_making_materials/2_example_materials_from_elements.ipynb', []),
        ('task_06', 'task_03_making_CSG_geometry/1_simple_csg_geometry.ipynb', []),
        ('task_07', 'task_04_make_sources/1_point_source_plots.ipynb', []),
        ('task_08', 'task_04_make_sources/2_ring_source.ipynb', []),
        ('task_09', 'task_04_make_sources/3_plasma_source_plots.ipynb', []),
        ('task_10', 'task_05_CSG_cell_tally_TBR/1_example_tritium_production.ipynb', []),
        ('task_11', 'task_06_CSG_cell_tally_DPA/1_find_dpa.ipynb', []),
        ('task_12', 'task_07_CSG_cell_tally_spectra/2_example_neutron_spectra_on_cell.ipynb', []),
        ('task_13', 'task_07_CSG_cell_tally_spectra/4_example_photon_spectra.ipynb', []),
        ('task_14', 'task_08_CSG_mesh_tally/1_example_2d_regular_mesh_tallies.ipynb', []),
        ('task_15', 'task_14_variance_reduction/2_shielded_room_single_ww.ipynb', []),
        ('task_16', 'task_14_variance_reduction/3_sphere_iterative_per_run_ww.ipynb', []),
        ('task_17', 'task_10_activation_transmutation_depletion/5_full_pulse_schedule.ipynb', []),
        ('task_18', 'task_21_design_task/1_optimal_design.ipynb', []),
    ],
    'half-day-conference-workshop': [
        ('task_01', 'task_02_making_materials/1_example_materials_from_isotopes.ipynb', []),
        ('task_02', 'task_01_cross_sections/3_material_xs_plot.ipynb', []),
        ('task_03', 'task_03_making_CSG_geometry/1_simple_csg_geometry.ipynb', []),
        ('task_04', 'task_04_make_sources/1_point_source_plots.ipynb', []),
        ('task_05', 'task_04_make_sources/2_ring_source.ipynb', []),
        ('task_06', 'task_05_CSG_cell_tally_TBR/1_example_tritium_production.ipynb', []),
        ('task_07', 'task_07_CSG_cell_tally_spectra/2_example_neutron_spectra_on_cell.ipynb', []),
        ('task_08', 'task_09_CSG_instantaneous_dose_tallies/3_biological_cell_dose_from_neutrons.ipynb', []),
        ('task_09', 'task_09_CSG_instantaneous_dose_tallies/5_biological_mesh_dose_from_neutrons.ipynb', []),
        ('task_10', 'task_14_variance_reduction/5_shielded_room_fw_cadis.ipynb', []),
        ('task_11', 'task_16_converting_CAD_geometry_to_DAGMC/2_converting_cad_in_memory.ipynb', []),
        ('task_12', 'task_17_using_DAGMC_models_in_openmc/1_cad_model_simulation_minimal.ipynb',
         ['task_17_using_DAGMC_models_in_openmc/dagmc.h5m']),
        ('task_13', 'task_18_CAD_mesh_fast_flux/1_simulate_fast_neutron_flux_on_cad.ipynb',
         ['task_18_CAD_mesh_fast_flux/dagmc_for_um.h5m', 'task_18_CAD_mesh_fast_flux/dagmc.vtk']),
        ('task_14', 'task_10_activation_transmutation_depletion/1_depletion_with_flux_spectra.ipynb', []),
        ('task_15', 'task_10_activation_transmutation_depletion/3_example_transmutation_isotope_build_up.ipynb', []),
        ('task_16', 'task_11_CSG_shut_down_dose_tallies/4_D1S_regularmesh_shutdown_dose_rate.ipynb', []),
    ],
    'full-day-workshop': [
        ('task_01', 'task_02_making_materials/1_example_materials_from_isotopes.ipynb', []),
        ('task_02', 'task_02_making_materials/2_example_materials_from_elements.ipynb', []),
        ('task_03', 'task_01_cross_sections/1_isotope_xs_plot.ipynb', []),
        ('task_04', 'task_01_cross_sections/2_element_xs_plot.ipynb', []),
        ('task_05', 'task_01_cross_sections/3_material_xs_plot.ipynb', []),
        ('task_06', 'task_03_making_CSG_geometry/1_simple_csg_geometry.ipynb', []),
        ('task_07', 'task_03_making_CSG_geometry/2_intermediate_csg_geometry.ipynb', []),
        ('task_08', 'task_03_making_CSG_geometry/3_viewing_the_geometry_as_vtk.ipynb', []),
        ('task_09', 'task_04_make_sources/1_point_source_plots.ipynb', []),
        ('task_10', 'task_04_make_sources/2_ring_source.ipynb', []),
        ('task_11', 'task_04_make_sources/4_neutron_tracks.ipynb', []),
        ('task_12', 'task_04_make_sources/5_gamma_source_example.ipynb', []),
        ('task_13', 'task_05_CSG_cell_tally_TBR/1_example_tritium_production.ipynb', []),
        ('task_14', 'task_07_CSG_cell_tally_spectra/2_example_neutron_spectra_on_cell.ipynb', []),
        ('task_15', 'task_09_CSG_instantaneous_dose_tallies/3_biological_cell_dose_from_neutrons.ipynb', []),
        ('task_16', 'task_09_CSG_instantaneous_dose_tallies/5_biological_mesh_dose_from_neutrons.ipynb', []),
        ('task_17', 'task_14_variance_reduction/5_shielded_room_fw_cadis.ipynb', []),
        ('task_18', 'task_16_converting_CAD_geometry_to_DAGMC/1_converting_cad_files.ipynb',
         ['task_16_converting_CAD_geometry_to_DAGMC/step_cad_file_for_conversion.step']),
        ('task_19', 'task_16_converting_CAD_geometry_to_DAGMC/2_converting_cad_in_memory.ipynb', []),
        ('task_20', 'task_17_using_DAGMC_models_in_openmc/1_cad_model_simulation_minimal.ipynb',
         ['task_17_using_DAGMC_models_in_openmc/dagmc.h5m']),
        ('task_21', 'task_18_CAD_mesh_fast_flux/1_simulate_fast_neutron_flux_on_cad.ipynb',
         ['task_18_CAD_mesh_fast_flux/dagmc_for_um.h5m', 'task_18_CAD_mesh_fast_flux/dagmc.vtk']),
        ('task_22', 'task_10_activation_transmutation_depletion/1_depletion_with_flux_spectra.ipynb', []),
        ('task_23', 'task_10_activation_transmutation_depletion/3_example_transmutation_isotope_build_up.ipynb', []),
        ('task_24', 'task_11_CSG_shut_down_dose_tallies/4_D1S_regularmesh_shutdown_dose_rate.ipynb', []),
    ],
}


ROOT = Path(__file__).resolve().parent
TASKS_DIR = ROOT / 'tasks'


def normalize_notebook_notebook(nb):
    for cell in nb.get('cells', []):
        if cell.get('cell_type') == 'code':
            cell['outputs'] = []
            cell['execution_count'] = None
    return nb


def read_normalized_notebook(path: Path) -> str:
    nb = nbformat.read(path, as_version=4)
    nb = normalize_notebook_notebook(nb)
    return nbformat.writes(nb, version=4)


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(8192), b''):
            digest.update(chunk)
    return digest.hexdigest()


def sync_workshops() -> None:
    for workshop_name, tasks in WORKSHOPS.items():
        workshop_dir = TASKS_DIR / workshop_name
        workshop_dir.mkdir(parents=True, exist_ok=True)
        print(f'\nSyncing {workshop_name}...')

        for folder, notebook_rel, extra_files in tasks:
            task_dir = workshop_dir / folder
            task_dir.mkdir(parents=True, exist_ok=True)

            source = TASKS_DIR / notebook_rel
            if not source.exists():
                print(f'  ⚠️  MISSING SOURCE: {notebook_rel}')
                continue

            notebook = nbformat.read(source, as_version=4)
            notebook = normalize_notebook_notebook(notebook)
            nbformat.write(notebook, task_dir / f'{folder}.ipynb')
            print(f'  ✓ {folder}/{folder}.ipynb')

            for extra_rel in extra_files:
                extra_source = TASKS_DIR / extra_rel
                if not extra_source.exists():
                    print(f'  ⚠️  MISSING SOURCE: {extra_rel}')
                    continue
                shutil.copy2(extra_source, task_dir / Path(extra_rel).name)
                print(f'  ✓ {folder}/{Path(extra_rel).name}')

        print(f'  Completed {workshop_name}')


def check_workshops() -> bool:
    all_good = True

    for workshop_name, tasks in WORKSHOPS.items():
        workshop_dir = TASKS_DIR / workshop_name
        print(f'\nChecking {workshop_name}...')

        if not workshop_dir.exists():
            print(f'  ❌ MISSING WORKSHOP DIRECTORY: {workshop_name}')
            all_good = False
            continue

        for folder, notebook_rel, extra_files in tasks:
            task_dir = workshop_dir / folder
            source = TASKS_DIR / notebook_rel
            target = task_dir / f'{folder}.ipynb'

            if not source.exists():
                print(f'  ❌ MISSING SOURCE: {notebook_rel}')
                all_good = False
            elif not target.exists():
                print(f'  ❌ MISSING WORKSHOP FILE: {folder}/{folder}.ipynb')
                all_good = False
            elif read_normalized_notebook(source) != read_normalized_notebook(target):
                print(f'  ❌ OUT OF DATE: {folder}/{folder}.ipynb')
                all_good = False
            else:
                print(f'  ✓ {folder}/{folder}.ipynb')

            for extra_rel in extra_files:
                extra_source = TASKS_DIR / extra_rel
                extra_target = task_dir / Path(extra_rel).name
                label = f'{folder}/{Path(extra_rel).name}'

                if not extra_source.exists():
                    print(f'  ❌ MISSING SOURCE: {extra_rel}')
                    all_good = False
                elif not extra_target.exists():
                    print(f'  ❌ MISSING WORKSHOP FILE: {label}')
                    all_good = False
                elif file_hash(extra_source) != file_hash(extra_target):
                    print(f'  ❌ OUT OF DATE: {label}')
                    all_good = False
                else:
                    print(f'  ✓ {label}')

    return all_good


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Sync or validate workshop folders against source task notebooks.',
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check whether workshop folders are up to date and return non-zero on mismatch.',
    )
    parser.add_argument(
        '--sync',
        action='store_true',
        help='Synchronize workshop folders from source notebooks.',
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.check:
        print('Checking workshop folders for updates...')
        good = check_workshops()
        if good:
            print('\nAll workshop notebooks are up to date!')
            return 0
        print('\nWorkshop folders are not in sync with source tasks.')
        return 1

    if args.sync:
        print('Synchronizing workshop folders from source tasks...')
        sync_workshops()
        print('\nSync complete.')
        return 0

    print('No action specified. Use --check or --sync.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
