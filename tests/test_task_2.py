
"""
This is how to regression test a notebook, however the random monte carlo
simulations don't produce the same outputs. This could be suitable for some
tasks
"""

# import importlib_resources
# from tasks import task_2
# from pytest_notebook.nb_regression import NBRegressionFixture
# fixture = NBRegressionFixture(exec_timeout=50)
# fixture.diff_color_words = False
# fixture.coverage=True

# def test_notebook(nb_regression):
#     with importlib_resources.path(task_2, "1_simple_csg_geometry.ipynb") as path:
#         nb_regression.check(str(path))
        
# def test_notebook_2(nb_regression):
#     with importlib_resources.path(task_2, "2_intermediate_csg_geometry.ipynb") as path:
#         nb_regression.check(str(path))


import unittest

# from the notebook
import openmc
import matplotlib.pyplot as plt

class test_task_2_notebook_1(unittest.TestCase):


    def test_part_1(self):
        """missing plt.show() from the last three lines"""

        # example surfaces
        inner_sphere_surface = openmc.Sphere(r=500)
        outer_sphere_surface = openmc.Sphere(r=600)

        # above (+) inner_sphere_surface and below (-) outer_sphere_surface
        blanket_region = +inner_sphere_surface & -outer_sphere_surface  

        # example cell
        blanket_cell = openmc.Cell(region=blanket_region)

        # makes a universe to cotain all the cells
        universe = openmc.Universe(cells=[blanket_cell])  

        # shows the plots, as the geometry is symmetrical the plots look the same
        color_assignment = {blanket_cell: 'blue'}
        universe.plot(width=(1200, 1200), basis='xz', colors=color_assignment)
        universe.plot(width=(1200, 1200), basis='xy', colors=color_assignment)
        universe.plot(width=(1200, 1200), basis='yz', colors=color_assignment)

    def test_part_2(self):
        # example surfaces
        inner_sphere_surface = openmc.Sphere(r=480)
        middle_sphere_surface = openmc.Sphere(r=500) # note the extra surface
        outer_sphere_surface = openmc.Sphere(r=600)

        # above (+) middle_sphere_surface and below (-) outer_sphere_surface
        blanket_region = +middle_sphere_surface & -outer_sphere_surface
        # above (+) inner_sphere_surface and below (-) middle_sphere_surface
        firstwall_region = +inner_sphere_surface & -middle_sphere_surface

        # now we have two cells
        blanket_cell = openmc.Cell(region=blanket_region)
        firstwall_cell = openmc.Cell(region=firstwall_region)

        # there are now two cells in the list
        universe = openmc.Universe(cells=[blanket_cell, firstwall_cell])  

        # shows the plots, which still look the same for all directions
        color_assignment = {blanket_cell: 'blue', firstwall_cell: 'red'}
        universe.plot(width=(1200, 1200), basis='xz', colors=color_assignment)
        universe.plot(width=(1200, 1200), basis='xy', colors=color_assignment)
        universe.plot(width=(1200, 1200), basis='yz', colors=color_assignment)

    def test_part_3(self):
        # surfaces
        inner_sphere_surface = openmc.Sphere(r=480)
        middle_sphere_surface = openmc.Sphere(r=500)
        outer_sphere_surface = openmc.Sphere(r=600, boundary_type='vacuum') # note the extra keyword

        # regions
        blanket_region = +middle_sphere_surface & -outer_sphere_surface
        firstwall_region = +inner_sphere_surface & -middle_sphere_surface
        inner_vessel_region = -inner_sphere_surface # this is the void region

        # cells
        blanket_cell = openmc.Cell(region=blanket_region)
        firstwall_cell = openmc.Cell(region=firstwall_region)
        inner_vessel_cell = openmc.Cell(region=inner_vessel_region) # here as the cell is th new void cell

        universe = openmc.Universe(cells=[blanket_cell, firstwall_cell, inner_vessel_cell])  

        # note the new color scheme is based on materials not cells
        color_assignment = {blanket_cell: 'blue', firstwall_cell: 'red', inner_vessel_cell:'grey'}
        # note the additional argument color_by, normally this defaults to 'cell'
        universe.plot(width=(1200, 1200), basis='xz', colors=color_assignment)
        universe.plot(width=(1200, 1200), basis='xy', colors=color_assignment)
        universe.plot(width=(1200, 1200), basis='yz', colors=color_assignment)

    def test_part_4(self):
        inner_sphere_surface = openmc.Sphere(r=480)
        middle_sphere_surface = openmc.Sphere(r=500)
        outer_sphere_surface = openmc.Sphere(r=600)

        blanket_region = +middle_sphere_surface & -outer_sphere_surface
        firstwall_region = +inner_sphere_surface & -middle_sphere_surface
        inner_vessel_region = -inner_sphere_surface # this is the void region, it will not have a material

        # This makes a minimal material 
        lithium_mat = openmc.Material(name='lithium')
        lithium_mat.set_density('g/cm3', 2)
        lithium_mat.add_element('Li', 1.0)

        # This makes another minimal material 
        tungsten_mat = openmc.Material(name='tungsten')
        tungsten_mat.set_density('g/cm3', 19)
        tungsten_mat.add_element('W', 1.0)

        blanket_cell = openmc.Cell(region=blanket_region)
        blanket_cell.fill = lithium_mat  # this assigns a material to a cell

        firstwall_cell = openmc.Cell(region=firstwall_region)
        firstwall_cell.fill = tungsten_mat  # this assigns a material to a cell

        inner_vessel_cell = openmc.Cell(region=inner_vessel_region)
        # note there is no material assignment here as the cell a void cell

        universe = openmc.Universe(cells=[blanket_cell, firstwall_cell, inner_vessel_cell])  

        # note the new color scheme is based on materials not cells
        color_assignment = {lithium_mat: 'green', tungsten_mat: 'yellow'}

        # note the additional argument color_by, normally this defaults to 'cell'
        universe.plot(width=(1200, 1200), basis='xz', color_by='material', colors=color_assignment)
        universe.plot(width=(1200, 1200), basis='xy', color_by='material', colors=color_assignment)
        universe.plot(width=(1200, 1200), basis='yz', color_by='material', colors=color_assignment)

class test_task_2_notebook_2(unittest.TestCase):

    def test_part_1(self):

        # surfaces
        central_column_surface = openmc.ZCylinder(r=100) # note the new surface type
        inner_sphere_surface = openmc.Sphere(r=480)
        middle_sphere_surface = openmc.Sphere(r=500) 
        outer_sphere_surface = openmc.Sphere(r=600, boundary_type='vacuum')

        # regions
        # the center column region is cut at the top and bottom using the -outer_sphere_surface
        central_column_region = -central_column_surface & -outer_sphere_surface
        firstwall_region = -middle_sphere_surface & +inner_sphere_surface & +central_column_surface
        blanket_region = +middle_sphere_surface & -outer_sphere_surface & +central_column_surface
        inner_vessel_region = +central_column_surface & -inner_sphere_surface

        # cells
        firstwall_cell = openmc.Cell(region=firstwall_region)
        central_column_cell = openmc.Cell(region=central_column_region)
        blanket_cell = openmc.Cell(region=blanket_region)
        inner_vessel_cell = openmc.Cell(region=inner_vessel_region)

        universe = openmc.Universe(cells=[central_column_cell, firstwall_cell,
                                        blanket_cell, inner_vessel_cell])

        # VISULISATION
        color_assignment = {blanket_cell: 'blue', firstwall_cell: 'red',
                            inner_vessel_cell:'grey', central_column_cell:'purple'}
        universe.plot(width=(1200, 1200), basis='xz', colors=color_assignment)
        universe.plot(width=(1200, 1200), basis='xy', colors=color_assignment)
        universe.plot(width=(1200, 1200), basis='yz', colors=color_assignment)

    def test_part_2(self):

        # surfaces
        central_column_surface = openmc.ZCylinder(r=100) # note the new surface type
        inner_sphere_surface = openmc.Sphere(r=480)
        middle_sphere_surface = openmc.Sphere(r=500) 
        outer_sphere_surface = openmc.Sphere(r=600, boundary_type='vacuum')

        # regions, this time defined using boolean operators
        # There are 3 opperators | OR, & AND, ~ NOT

        central_column_region = -central_column_surface & -outer_sphere_surface

        # the inner_vessel_region is defined using the logical NOT operator ~
        inner_vessel_region = -inner_sphere_surface & ~central_column_region

        # the firstwall_region is defined as below the middle surface and not in two other regions
        firstwall_region = -middle_sphere_surface & ~inner_vessel_region & ~central_column_region

        # the blanket_region is defined as between two surfaces and not the center_column_region
        blanket_region = +middle_sphere_surface & -outer_sphere_surface & ~central_column_region


        # cells defined in the same way
        firstwall_cell = openmc.Cell(region=firstwall_region)
        central_column_cell = openmc.Cell(region=central_column_region)
        blanket_cell = openmc.Cell(region=blanket_region)
        inner_vessel_cell = openmc.Cell(region=inner_vessel_region)

        universe = openmc.Universe(cells=[central_column_cell, firstwall_cell,
                                        blanket_cell, inner_vessel_cell])

        # VISULISATION
        color_assignment = {blanket_cell: 'blue', firstwall_cell: 'red',
                            inner_vessel_cell:'grey', central_column_cell:'purple'}
        universe.plot(width=(1200, 1200), basis='xz', colors=color_assignment)
        universe.plot(width=(1200, 1200), basis='xy', colors=color_assignment)
        universe.plot(width=(1200, 1200), basis='yz', colors=color_assignment)
