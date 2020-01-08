
""" test_script.py: run all the examples in the openmc workshop and check each example produces the expected results.
    The example scripts open up various plots, some of which pause / block the running of this test suite.
    The running of the tests can be manually resumed by closing matplotlib and eog windows when they pop up
    run with
    pytest test_scripts.py
"""

from pathlib import Path 
import os
import pytest
import unittest

cwd = os.getcwd()

class test_task_1(unittest.TestCase):
    def test_task_1_part_1(self):

        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_1'))
        output_filename = '1_example_isotope_plot.html'
        os.system('rm '+output_filename)
        os.system('python 1_example_isotope_plot.py')
        assert Path(output_filename).exists() == True
        os.system('rm '+output_filename)


    # def test_task_1_part_2(self): #  this test is slow so it has been commented out for the time being

    #     os.chdir(Path(cwd))
    #     os.chdir(Path('tasks/task_1'))
    #     output_filename = '2_example_element_plot_16.html'
    #     os.system('rm '+output_filename)
    #     os.system('python 2_example_element_plot.py')
    #     assert Path(output_filename).exists() == True
    #     os.system('rm '+output_filename)


    def test_task_1_part_3(self):
        
        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_1'))
        output_filename = '3_example_material_plot.html'
        os.system('rm '+output_filename)
        os.system('python 3_example_material_plot.py')
        assert Path(output_filename).exists() == True
        os.system('rm '+output_filename)


class test_task_2(unittest.TestCase):
    
    def test_task_2_part_1(self): #  This test launches matplotlib that pauses the running of the script
    
        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_2'))
        output_filenames = ['xz_sphere.png', 'xy_sphere.png', 'yz_sphere.png']
        for output_filename in output_filenames:
            os.system('rm '+output_filename)
        os.system('python 1_example_geometry_viewer_2d.py')
        for output_filename in output_filenames:
            assert Path(output_filename).exists() == True
            os.system('rm '+output_filename)


    def test_task_2_part_1_optional(self): #  This test launches eog that pauses the running of the script

        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_2'))
        output_filename = 'plot.png'
        os.system('rm '+output_filename)
        os.system('python 2_example_geometry_viewer_2d_xml_version.py')
        assert Path(output_filename).exists() == True
        os.system('rm '+output_filename)


    def test_task_2_part_3(self): #  This test launches matplotlib that pauses the running of the script

        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_2'))
        output_filenames = ['xz_tokamak.png', 'xy_tokamak.png', 'yz_tokamak.png']
        for output_filename in output_filenames:
            os.system('rm '+output_filename)
        os.system('python 3_example_geometry_viewer_2d_tokamak.py')
        for output_filename in output_filenames:
            assert Path(output_filename).exists() == True
            os.system('rm '+output_filename)


    def test_task_2_part_4(self):

        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_2'))
        output_filename = 'plot_3d_tokamak.vti'
        os.system('rm '+output_filename)
        os.system('python 4_example_geometry_viewer_3d_tokamak.py')
        assert Path(output_filename).exists() == True
        os.system('rm '+output_filename)



class test_task_3(unittest.TestCase):
    def test_task_3_part_1(self):

        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_3'))
        output_filename = 'particle_energy_histogram.html'
        os.system('rm '+output_filename)
        os.system('python 1_plot_neutron_birth_energy.py')
        assert Path(output_filename).exists() == True
        os.system('rm '+output_filename)
    
    
    def test_task_3_part_2(self):

        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_3'))
        output_filename = 'particle_direction.html'
        os.system('rm '+output_filename)
        os.system('python 2_plot_neutron_birth_direction.py')
        assert Path(output_filename).exists() == True
        os.system('rm '+output_filename)
    

    def test_task_3_part_3(self):

        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_3'))
        output_filename = 'particle_location.html'
        os.system('rm '+output_filename)
        os.system('python 3_plot_neutron_birth_location.py')
        assert Path(output_filename).exists() == True
        os.system('rm '+output_filename)
    

    def test_task_3_part_4(self):

        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_3'))
        output_filename = 'plasma_particle_direction.html'
        os.system('rm '+output_filename)
        os.system('python 4_plot_neutron_birth_direction_plasma.py')
        assert Path(output_filename).exists() == True
        os.system('rm '+output_filename)
 

    def test_task_3_part_5(self):

        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_3'))
        output_filename = 'plasma_particle_location.html'
        os.system('rm '+output_filename)
        os.system('python 5_plot_neutron_birth_location_plasma.py')
        assert Path(output_filename).exists() == True
        os.system('rm '+output_filename)
        

    def test_task_3_part_6(self):

        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_3'))
        output_filenames = ['plot_3d.h5', 'plot_3d.vti', 'track_1_1_4.h5', 'track_1_1_4.pvtp', 'track_1_1_4_0.vtp']
        for output_filename in output_filenames:
            os.system('rm '+output_filename)
        os.system('python 6_example_neutron_tracks.py')
        for output_filename in output_filenames:
            assert Path(output_filename).exists() == True
            os.system('rm '+output_filename)
        


class test_task_4(unittest.TestCase):   # this test currently fails until the output has been sorted
    def test_task_4_part_1(self):

        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_3'))
        output_filenames = ['universe_plot.png', 'flux_plot.png']
        for output_filename in output_filenames:
            os.system('rm '+output_filename)
        os.system('python 1_example_neutron_flux.py')
        for output_filename in output_filenames:
            assert Path(output_filename).exists() == True
            os.system('rm '+output_filename)

    def test_task_4_part_2(self):

        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_4'))
        output_filename = 'tally_on_mesh.vtk'
        os.system('rm '+output_filename)
        os.system('python 2_example_neutron_flux_tokamak.py')
        assert Path(output_filename).exists() == True
        os.system('rm '+output_filename)
        


class test_task_5(unittest.TestCase):
    def test_task_5_part_1(self):
 
        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_5'))
        output_filename = 'tokamak_spectra.html'
        os.system('rm '+output_filename)
        os.system('python 1_example_neutron_spectra_tokamak.py')
        assert Path(output_filename).exists() == True
        os.system('rm '+output_filename)
      

    def test_task_5_part_2(self):

        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_5'))
        output_filename = 'tokamak_photon_spectra.html'
        os.system('rm '+output_filename)
        os.system('python 2_example_photon_spectra_tokamak.py')
        assert Path(output_filename).exists() == True
        os.system('rm '+output_filename)
   


class test_task_6(unittest.TestCase):
    def test_task_6_part_1(self):

        os.chdir(Path(cwd))
        os.chdir(Path('tasks/task_6'))
        output_filename = 'tbr_study.html'
        os.system('rm '+output_filename)
        os.system('python 2_example_tritium_production_study.py')
        assert Path(output_filename).exists() == True
        os.system('rm '+output_filename)
        os.chdir(Path(cwd))

