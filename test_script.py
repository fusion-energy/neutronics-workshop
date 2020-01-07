
""" test_script.py: run all the examples in the openmc workshop and check each example produces the exspected results.
    The example scripts open up various plots, some of which pause / block the running of this test suite.
    The running of the tests can be manually resumed by closing matplotlib and eog windows when they pop up
    run with
    pytest test_scripts.py
"""

from pathlib import Path 
import os
import pytest
import unittest

class test_task_1(unittest.TestCase):
    def test_task_1_part_1(self):

        cwd = os.getcwd()
        os.chdir(Path('tasks/task_1'))
        output_filename = '1_example_isotope_plot.html'
        os.system('rm '+output_filename)
        os.system('python 1_example_isotope_plot.py')
        assert Path(output_filename).exists() == True
        os.system('rm '+output_filename)
        os.chdir(Path(cwd))


    # def test_task_1_part_2(self): #  this test is slow so it has been commented out for the time being

    #     cwd = os.getcwd()
    #     os.chdir(Path('tasks/task_1'))
    #     output_filename = '2_example_element_plot_16.html'
    #     os.system('rm '+output_filename)
    #     os.system('python 2_example_element_plot.py')
    #     assert Path(output_filename).exists() == True
    #     os.system('rm '+output_filename)
    #     os.chdir(Path(cwd))


    def test_task_1_part_3(self):
        
        cwd = os.getcwd()
        os.chdir(Path('tasks/task_1'))
        output_filename = '3_example_material_plot.html'
        os.system('rm '+output_filename)
        os.system('python 3_example_material_plot.py')
        assert Path(output_filename).exists() == True
        os.system('rm '+output_filename)
        os.chdir(Path(cwd))


class test_task_2(unittest.TestCase):
    
    def test_task_2_part_1(self): #  This test launches matplotlib that pauses the running of the script
        
        cwd = os.getcwd()
        os.chdir(Path('tasks/task_2'))
        output_filenames = ['xz_sphere.png', 'xy_sphere.png', 'yz_sphere.png']
        os.system('python 1_example_geometry_viewer_2d.py')
        for output_filename in output_filenames:
            assert Path(output_filename).exists() == True
            os.system('rm '+output_filename)
        os.chdir(Path(cwd))


    def test_task_2_part_1_optional(self): #  This test launches eog that pauses the running of the script

        cwd = os.getcwd()
        os.chdir(Path('tasks/task_2'))
        output_filename = 'plot.png'
        os.system('python 2_example_geometry_viewer_2d_xml_version.py')
        assert Path(output_filename).exists() == True
        os.system('rm '+output_filename)
        os.chdir(Path(cwd))


    def test_task_2_part_3(self): #  This test launches matplotlib that pauses the running of the script
        cwd = os.getcwd()
        os.chdir(Path('tasks/task_2'))
        output_filenames = ['xz_tokamak.png', 'xy_tokamak.png', 'yz_tokamak.png']
        os.system('python 3_example_geometry_viewer_2d_tokamak.py')
        for output_filename in output_filenames:
            assert Path(output_filename).exists() == True
            os.system('rm '+output_filename)
        os.chdir(Path(cwd))


    def test_task_2_part_4(self):
        # python 4_example_geometry_viewer_3d_tokamak.py
        # paraview plot_3d_tokamak.vti
        pass



class test_task_3(unittest.TestCase):
    def test_task_3_part_1(self):
        # cd tasks/task_3

        # python 1_plot_neutron_birth_energy.py
        # particle_energy_histogram.html
        pass
    
    def test_task_3_part_2(self):

        # python 2_plot_neutron_birth_direction.py
        # particle_direction.html
        pass

    def test_task_3_part_3(self):
        # python 3_plot_neutron_birth_location.py
        # particle_location.html
        pass

    def test_task_3_part_4(self):
        # python 4_plot_neutron_birth_direction_plasma
        # plasma_particle_location.html
        pass

    def test_task_3_part_5(self):
        # python 5_plot_neutron_birth_location_plasma.py
        # plasma_particle_direction.html
        pass

    def test_task_3_part_6(self):
        # 6_example_neutron_tracks.py
        # plot_3d.h5
        # plot_3d.vti
        # track_1_1_4.h5
        # track_1_1_4.pvtp
        # track_1_1_4_0.vtp
        pass


class test_task_4(unittest.TestCase):
    def test_task_4_part_1(self):
        # cd tasks/task_4

        # python 1_example_neutron_flux
        # tally_on_mesh
        pass

    def test_task_4_part_2(self):
        # python 2_example_neutron_flux_tokamak
        # tally_on_mesh.vtk
        pass



class test_task_5(unittest.TestCase):
    def test_task_5_part_1(self):
        # cd tasks/task_5

        # python 1_example_neutron_spectra_tokamak.py 
        # tokamak_spectra.html
        pass

    def test_task_5_part_2(self):
        # python 2_example_photon_spectra_tokamak.py
        # tokamak_photon_spectra.html
        pass


class test_task_6(unittest.TestCase):
    def test_task_6_part_1(self):
        # cd tasks/task_6
        # python 2_example_tritium_production_study.py
        # tbr_study.html
        pass
