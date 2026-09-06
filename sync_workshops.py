#!/usr/bin/env python3
"""Sync or validate workshop folders against the source task scripts.

Each workshop task is copied into its own subfolder (e.g. ``task_01/``) inside
the workshop directory. The subfolder holds the task script (named after the
folder, e.g. ``task_01/task_01.py``) together with any extra data files the
task needs (DAGMC ``.h5m`` files, meshes, CAD ``.step`` files, ...).

Giving every task its own folder keeps the run-time outputs of one task (for
example ``statepoint.h5`` and ``summary.h5``) from overwriting those of another.

Each task is defined as a tuple of::

    (folder_name, source_script, [extra_source_files])

Paths are relative to the ``tasks`` directory. The script is written into
``<workshop>/<folder_name>/<folder_name>.py`` and each extra file is copied
into the same folder keeping its original basename.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import shutil

WORKSHOPS = {
    'half-day-university-workshop': [
        ('task_01', 'task_01_cross_sections/1_isotope_xs_plot.py', []),
        ('task_02', 'task_01_cross_sections/2_element_xs_plot.py', []),
        ('task_03', 'task_01_cross_sections/3_material_xs_plot.py', []),
        ('task_04', 'task_02_making_materials/1_example_materials_from_isotopes.py', []),
        ('task_05', 'task_02_making_materials/2_example_materials_from_elements.py', []),
        ('task_06', 'task_03_making_CSG_geometry/1_simple_csg_geometry.py', []),
        ('task_07', 'task_04_make_sources/1_point_source_plots.py', []),
        ('task_08', 'task_04_make_sources/2_ring_source.py', []),
        ('task_09', 'task_04_make_sources/3_plasma_source_plots.py', []),
        ('task_10', 'task_05_CSG_cell_tally_TBR/1_example_tritium_production.py', []),
        ('task_11', 'task_06_CSG_cell_tally_DPA/1_find_dpa.py', []),
        ('task_12', 'task_07_CSG_cell_tally_spectra/2_example_neutron_spectra_on_cell.py', []),
        ('task_13', 'task_07_CSG_cell_tally_spectra/4_example_photon_spectra.py', []),
        ('task_14', 'task_08_CSG_mesh_tally/1_example_2d_regular_mesh_tallies.py', []),
        ('task_15', 'task_14_variance_reduction/2_shielded_room_single_ww.py', []),
        ('task_16', 'task_14_variance_reduction/3_sphere_iterative_per_run_ww.py', []),
        ('task_17', 'task_10_activation_transmutation_depletion/5_full_pulse_schedule.py', []),
        ('task_18', 'task_21_design_task/1_optimal_design.py', []),
    ],
    'half-day-conference-workshop': [
        ('task_01', 'task_02_making_materials/1_example_materials_from_isotopes.py', []),
        ('task_02', 'task_01_cross_sections/3_material_xs_plot.py', []),
        ('task_03', 'task_03_making_CSG_geometry/1_simple_csg_geometry.py', []),
        ('task_04', 'task_04_make_sources/1_point_source_plots.py', []),
        ('task_05', 'task_04_make_sources/2_ring_source.py', []),
        ('task_06', 'task_05_CSG_cell_tally_TBR/1_example_tritium_production.py', []),
        ('task_07', 'task_07_CSG_cell_tally_spectra/2_example_neutron_spectra_on_cell.py', []),
        ('task_08', 'task_09_CSG_instantaneous_dose_tallies/3_biological_cell_dose_from_neutrons.py', []),
        ('task_09', 'task_09_CSG_instantaneous_dose_tallies/5_biological_mesh_dose_from_neutrons.py', []),
        ('task_10', 'task_14_variance_reduction/5_shielded_room_fw_cadis.py', []),
        ('task_11', 'task_16_converting_CAD_geometry_to_DAGMC/2_converting_cad_in_memory.py', []),
        ('task_12', 'task_17_using_DAGMC_models_in_openmc/1_cad_model_simulation_minimal.py',
         ['task_17_using_DAGMC_models_in_openmc/dagmc.h5m']),
        ('task_13', 'task_18_CAD_mesh_fast_flux/1_simulate_fast_neutron_flux_on_cad.py',
         ['task_18_CAD_mesh_fast_flux/dagmc_for_um.h5m', 'task_18_CAD_mesh_fast_flux/dagmc.vtk']),
        ('task_14', 'task_10_activation_transmutation_depletion/1_depletion_with_flux_spectra.py', []),
        ('task_15', 'task_10_activation_transmutation_depletion/3_example_transmutation_isotope_build_up.py', []),
        ('task_16', 'task_11_CSG_shut_down_dose_tallies/4_D1S_regularmesh_shutdown_dose_rate.py', []),
    ],
    'full-day-workshop': [
        ('task_01', 'task_02_making_materials/1_example_materials_from_isotopes.py', []),
        ('task_02', 'task_02_making_materials/2_example_materials_from_elements.py', []),
        ('task_03', 'task_01_cross_sections/1_isotope_xs_plot.py', []),
        ('task_04', 'task_01_cross_sections/2_element_xs_plot.py', []),
        ('task_05', 'task_01_cross_sections/3_material_xs_plot.py', []),
        ('task_06', 'task_03_making_CSG_geometry/1_simple_csg_geometry.py', []),
        ('task_07', 'task_03_making_CSG_geometry/2_intermediate_csg_geometry.py', []),
        ('task_08', 'task_03_making_CSG_geometry/3_viewing_the_geometry_as_vtk.py', []),
        ('task_09', 'task_04_make_sources/1_point_source_plots.py', []),
        ('task_10', 'task_04_make_sources/2_ring_source.py', []),
        ('task_11', 'task_04_make_sources/4_neutron_tracks.py', []),
        ('task_12', 'task_04_make_sources/5_gamma_source_example.py', []),
        ('task_13', 'task_05_CSG_cell_tally_TBR/1_example_tritium_production.py', []),
        ('task_14', 'task_07_CSG_cell_tally_spectra/2_example_neutron_spectra_on_cell.py', []),
        ('task_15', 'task_09_CSG_instantaneous_dose_tallies/3_biological_cell_dose_from_neutrons.py', []),
        ('task_16', 'task_09_CSG_instantaneous_dose_tallies/5_biological_mesh_dose_from_neutrons.py', []),
        ('task_17', 'task_14_variance_reduction/5_shielded_room_fw_cadis.py', []),
        ('task_18', 'task_16_converting_CAD_geometry_to_DAGMC/1_converting_cad_files.py',
         ['task_16_converting_CAD_geometry_to_DAGMC/step_cad_file_for_conversion.step']),
        ('task_19', 'task_16_converting_CAD_geometry_to_DAGMC/2_converting_cad_in_memory.py', []),
        ('task_20', 'task_17_using_DAGMC_models_in_openmc/1_cad_model_simulation_minimal.py',
         ['task_17_using_DAGMC_models_in_openmc/dagmc.h5m']),
        ('task_21', 'task_18_CAD_mesh_fast_flux/1_simulate_fast_neutron_flux_on_cad.py',
         ['task_18_CAD_mesh_fast_flux/dagmc_for_um.h5m', 'task_18_CAD_mesh_fast_flux/dagmc.vtk']),
        ('task_22', 'task_10_activation_transmutation_depletion/1_depletion_with_flux_spectra.py', []),
        ('task_23', 'task_10_activation_transmutation_depletion/3_example_transmutation_isotope_build_up.py', []),
        ('task_24', 'task_11_CSG_shut_down_dose_tallies/4_D1S_regularmesh_shutdown_dose_rate.py', []),
    ],
}


ROOT = Path(__file__).resolve().parent
TASKS_DIR = ROOT / 'tasks'


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

        for folder, script_rel, extra_files in tasks:
            task_dir = workshop_dir / folder
            task_dir.mkdir(parents=True, exist_ok=True)

            source = TASKS_DIR / script_rel
            if not source.exists():
                print(f'  ⚠️  MISSING SOURCE: {script_rel}')
                continue

            shutil.copy2(source, task_dir / f'{folder}.py')
            print(f'  ✓ {folder}/{folder}.py')

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

        for folder, script_rel, extra_files in tasks:
            task_dir = workshop_dir / folder
            source = TASKS_DIR / script_rel
            target = task_dir / f'{folder}.py'

            if not source.exists():
                print(f'  ❌ MISSING SOURCE: {script_rel}')
                all_good = False
            elif not target.exists():
                print(f'  ❌ MISSING WORKSHOP FILE: {folder}/{folder}.py')
                all_good = False
            elif file_hash(source) != file_hash(target):
                print(f'  ❌ OUT OF DATE: {folder}/{folder}.py')
                all_good = False
            else:
                print(f'  ✓ {folder}/{folder}.py')

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
        description='Sync or validate workshop folders against the source task scripts.',
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check whether workshop folders are up to date and return non-zero on mismatch.',
    )
    parser.add_argument(
        '--sync',
        action='store_true',
        help='Synchronize workshop folders from the source task scripts.',
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.check:
        print('Checking workshop folders for updates...')
        good = check_workshops()
        if good:
            print('\nAll workshop tasks are up to date!')
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
