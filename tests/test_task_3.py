import unittest

# from the notebook
import openmc
from tasks.task_3.source_extraction_utils import *  # imports plotting functions

class test_task_3_notebook_1(unittest.TestCase):

    def test_part_1(self):
        # initialises a new source object
        source = openmc.Source()

        # sets the location of the source to x=0 y=0 z=0
        source.space = openmc.stats.Point((0, 0, 0))

        # sets the direction to isotropic
        source.angle = openmc.stats.Isotropic()

        # sets the energy distribution to 100% 14MeV neutrons
        source.energy = openmc.stats.Discrete([14e6], [1])

        create_inital_particles(source)
        plot_energy_from_initial_source(input_filename='initial_source.h5')

    def test_part_2(self):
        source = openmc.Source()
        source.space = openmc.stats.Point((0, 0, 0))
        source.angle = openmc.stats.Isotropic()

        # Documentation on the Watt distribution is here
        # https://docs.openmc.org/en/stable/pythonapi/generated/openmc.data.WattEnergy.html
        source.energy = openmc.stats.Watt(a=988000.0, b=2.249e-06)


        create_inital_particles(source)
        plot_energy_from_initial_source(input_filename='initial_source.h5')

    def test_part_3(self):
        source = openmc.Source()
        source.space = openmc.stats.Point((0, 0, 0))
        source.angle = openmc.stats.Isotropic()

        # Documentation on the Muir distribution is here
        # https://docs.openmc.org/en/stable/pythonapi/generated/openmc.stats.Muir.html
        source.energy = openmc.stats.Muir(e0=14080000.0, m_rat=5.0, kt=20000.0)

        create_inital_particles(source)
        plot_energy_from_initial_source(input_filename='initial_source.h5')

    def test_part_3(self):
        # Creates an isotropic point source with monoenergetic 14MeV neutrons
        source = openmc.Source()
        source.space = openmc.stats.Point((0, 0, 0))
        source.angle = openmc.stats.Isotropic()
        source.energy = openmc.stats.Discrete([14e6], [1])

        create_inital_particles(source)
        # plots the position of neutrons created
        plot_postion_from_initial_source()

    def test_part_4(self):
        # Creates an isotropic point source with monoenergetic 14MeV neutrons
        source = openmc.Source()
        source.space = openmc.stats.Point((0, 0, 0))
        source.angle = openmc.stats.Isotropic()
        source.energy = openmc.stats.Discrete([14e6], [1])

        create_inital_particles(source)
        # plots the initial direction of neutrons created
        plot_direction_from_initial_source()

from random import random
import plotly.graph_objects as go
from parametric_plasma_source import PlasmaSource

class test_task_3_notebook_2(unittest.TestCase):

    def test_part_1_2_3(self):
        my_plasma = PlasmaSource(
            elongation=1.557,
            ion_density_origin=1.09e20,
            ion_density_peaking_factor=1,
            ion_density_pedestal=1.09e20,
            ion_density_separatrix=3e19,
            ion_temperature_origin=45.9,
            ion_temperature_peaking_factor=8.06,
            ion_temperature_pedestal=6.09,
            ion_temperature_separatrix=0.1,
            major_radius=906.0,
            minor_radius=292.258,
            pedestal_radius=0.8 * 292.258,
            plasma_id=1,
            shafranov_shift=44.789,
            triangularity=0.270,
            ion_temperature_beta=6
        )

        # cell 2
        #creates empty lists ready to be populated
        x_locations, y_locations, z_locations, x_directions, y_directions, z_directions, energies = ([] for i in range(7))

        number_of_samples = 500

        for x in range(number_of_samples):
            # randomises the neutron sampler
            sample = my_plasma.sample([random(), random(), random(), random(), random(), random(), random(), random()])
            x_locations.append(sample[0])
            y_locations.append(sample[1])
            z_locations.append(sample[2])
            x_directions.append(sample[3])
            y_directions.append(sample[4])
            z_directions.append(sample[5])
            energies.append(sample[6])

            text = ['Energy = ' + str(i) + ' eV' for i in energies]

        # cell 3
        fig_coords = go.Figure()

        fig_coords.add_trace(go.Scatter3d(
            x=x_locations,
            y=y_locations,
            z=z_locations,
            hovertext=text,
            text=text,
            mode='markers',
            marker={
                'size': 1.5,
                'color': energies
                }
            )
        )

        fig_coords.update_layout(title='Neutron production coordinates, coloured by energy')