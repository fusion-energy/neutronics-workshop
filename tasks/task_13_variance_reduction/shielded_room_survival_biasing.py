import openmc
import openmc_geometry_plot  # adds extra plotting functions to openmc.Geometry object
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import LogNorm


air = openmc.Material(name="Air")
air.set_density("g/cc", 0.001205)
air.add_element("N", 0.784431)
air.add_element("O", 0.210748)
air.add_element("Ar", 0.0046)

concrete = openmc.Material(name="concrete")
concrete.set_density("g/cm3", 7.874)
concrete.add_element("Fe", 1)

materials = openmc.Materials([air, concrete])

width_a = 100
width_b = 200
width_c = 500
width_d = 250
width_e = 200
width_f = 200
width_g = 100

depth_a = 100
depth_b = 200
depth_c = 700
depth_d = 600
depth_e = 200
depth_f = 100

height_j = 100
height_k = 500
height_l = 100


xplane_0 = openmc.XPlane(x0=0, boundary_type="vacuum")
xplane_1 = openmc.XPlane(x0=xplane_0.x0 + width_a)
xplane_2 = openmc.XPlane(x0=xplane_1.x0 + width_b)
xplane_3 = openmc.XPlane(x0=xplane_2.x0 + width_c)
xplane_4 = openmc.XPlane(x0=xplane_3.x0 + width_d)
xplane_5 = openmc.XPlane(x0=xplane_4.x0 + width_e)
xplane_6 = openmc.XPlane(x0=xplane_5.x0 + width_f)
xplane_7 = openmc.XPlane(x0=xplane_6.x0 + width_g, boundary_type="vacuum")

yplane_0 = openmc.YPlane(y0=0, boundary_type="vacuum")
yplane_1 = openmc.YPlane(y0=yplane_0.y0 + depth_a)
yplane_2 = openmc.YPlane(y0=yplane_1.y0 + depth_b)
yplane_3 = openmc.YPlane(y0=yplane_2.y0 + depth_c)
yplane_4 = openmc.YPlane(y0=yplane_3.y0 + depth_d)
yplane_5 = openmc.YPlane(y0=yplane_4.y0 + depth_e)
yplane_6 = openmc.YPlane(y0=yplane_5.y0 + depth_f, boundary_type="vacuum")

zplane_1 = openmc.ZPlane(z0=0, boundary_type="vacuum")
zplane_2 = openmc.ZPlane(z0=zplane_1.z0 + height_j)
zplane_3 = openmc.ZPlane(z0=zplane_2.z0 + height_k)
zplane_4 = openmc.ZPlane(z0=zplane_3.z0 + height_l, boundary_type="vacuum")

outside_left_region = +xplane_0 & -xplane_1 & +yplane_1 & -yplane_5 & +zplane_1 & -zplane_4
wall_left_region = +xplane_1 & -xplane_2 & +yplane_2 & -yplane_4 & +zplane_2 & -zplane_3
wall_right_region = +xplane_5 & -xplane_6 & +yplane_2 & -yplane_5 & +zplane_2 & -zplane_3
wall_top_region = +xplane_1 & -xplane_4 & +yplane_4 & -yplane_5 & +zplane_2 & -zplane_3
outside_top_region = +xplane_0 & -xplane_7 & +yplane_5 & -yplane_6 & +zplane_1 & -zplane_4
wall_bottom_region = +xplane_1 & -xplane_6 & +yplane_1 & -yplane_2 & +zplane_2 & -zplane_3
outside_bottom_region = +xplane_0 & -xplane_7 & +yplane_0 & -yplane_1 & +zplane_1 & -zplane_4
wall_middle_region = +xplane_3 & -xplane_4 & +yplane_3 & -yplane_4 & +zplane_2 & -zplane_3
outside_right_region = +xplane_6 & -xplane_7 & +yplane_1 & -yplane_5 & +zplane_1 & -zplane_4

room_region = +xplane_2 & -xplane_3 & +yplane_2 & -yplane_4 & +zplane_2 & -zplane_3
gap_region = +xplane_3 & -xplane_4 & +yplane_2 & -yplane_3 & +zplane_2 & -zplane_3
corridor_region = +xplane_4 & -xplane_5 & +yplane_2 & -yplane_5 & +zplane_2 & -zplane_3

roof_region = +xplane_1 & -xplane_6 & +yplane_1 & -yplane_5 & +zplane_1 & -zplane_2
floor_region = +xplane_1 & -xplane_6 & +yplane_1 & -yplane_5 & +zplane_3 & -zplane_4

outside_left_cell = openmc.Cell(region=outside_left_region, fill=air, name="outside_left_cell")
outside_right_cell = openmc.Cell(region=outside_right_region, fill=air, name="outside_right_cell")
outside_top_cell = openmc.Cell(region=outside_top_region, fill=air, name="outside_top_cell")
outside_bottom_cell = openmc.Cell(region=outside_bottom_region, fill=air, name="outside_bottom_cell")
wall_left_cell = openmc.Cell(region=wall_left_region, fill=concrete)
wall_right_cell = openmc.Cell(region=wall_right_region, fill=concrete)
wall_top_cell = openmc.Cell(region=wall_top_region, fill=concrete)
wall_bottom_cell = openmc.Cell(region=wall_bottom_region, fill=concrete)
wall_middle_cell = openmc.Cell(region=wall_middle_region, fill=concrete)
room_cell = openmc.Cell(region=room_region, fill=air, name="room_cell")
gap_cell = openmc.Cell(region=gap_region, fill=air)
corridor_cell = openmc.Cell(region=corridor_region, fill=air)

roof_cell = openmc.Cell(region=roof_region, fill=concrete)
floor_cell = openmc.Cell(region=floor_region, fill=concrete)

materials = openmc.Materials([air, concrete])
geometry = openmc.Geometry(
    [
        outside_bottom_cell,
        outside_top_cell,
        outside_left_cell,
        outside_right_cell,
        wall_left_cell,
        wall_right_cell,
        wall_top_cell,
        wall_bottom_cell,
        wall_middle_cell,
        room_cell,
        gap_cell,
        corridor_cell,
        roof_cell,
        floor_cell,
    ]
)

model = openmc.Model()
model.geometry = geometry

# location of the point source
source_x = width_a + width_b + width_c * 0.5
source_y = depth_a + depth_b + depth_c * 0.75
source_z = height_j + height_k * 0.5

xlabel, ylabel = geometry.get_axis_labels(view_direction="z")
plt.xlabel(xlabel)
plt.ylabel(ylabel)

plot_extent = geometry.get_mpl_plot_extent(view_direction="z")

data_slice = geometry.get_slice_of_material_ids(view_direction="z")
# plots the materials with randomly assigned colors
plt.imshow(
    np.fliplr(data_slice),
    extent=plot_extent,
)

# plots the outline of the cells
plt.contour(
    np.fliplr(data_slice),
    origin="upper",
    colors="k",
    linestyles="solid",
    linewidths=1,
    extent=plot_extent,
)

# plots the source location
plt.scatter(source_x, source_y, c="red")
plt.savefig('geometry_view.png')

plt.clf()
plt.cla()

xlabel, ylabel = geometry.get_axis_labels(view_direction="y")
plt.xlabel(xlabel)
plt.ylabel(ylabel)

plot_extent = geometry.get_mpl_plot_extent(view_direction="y")

data_slice = geometry.get_slice_of_material_ids(view_direction="y")
# plots the materials with randomly assigned colors
plt.imshow(
    np.fliplr(data_slice),
    extent=plot_extent,
)

# plots the outline of the cells
plt.contour(
    np.fliplr(data_slice),
    origin="upper",
    colors="k",
    linestyles="solid",
    linewidths=1,
    extent=plot_extent,
)

# plots the source location
plt.scatter(source_x, source_z, c="red")
plt.savefig('geometry_view_2.png')

mesh = openmc.RegularMesh().from_domain(geometry)
mesh.dimension = (100, 100, 1)

mesh_filter = openmc.MeshFilter(mesh)

flux_tally = openmc.Tally(name="flux tally")
flux_tally.filters = [mesh_filter]
flux_tally.scores = ["flux"]

model.tallies = [flux_tally]

space = openmc.stats.Point((source_x, source_y, source_z))
angle = openmc.stats.Isotropic()
energy = openmc.stats.Discrete([2.5e6], [1.0])

source = openmc.Source(space=space, angle=angle, energy=energy)
source.particle = "neutron"
model.settings.run_mode = "fixed source"
model.settings.source = source
model.settings.particles = 2000
model.settings.batches = 5


def run_and_plot(model, filename, output=True):

    sp_filename = model.run(output=output)

    with openmc.StatePoint(sp_filename) as sp:
        flux_tally = sp.get_tally(name="flux tally")

    llc, urc = model.geometry.bounding_box

    # create a plot of the mean flux values
    flux_mean = flux_tally.mean.reshape(100, 100)
    plt.subplot(1, 2, 1)
    plt.imshow(
        flux_mean,
        origin="lower",
        extent=(llc[0], urc[0], llc[1], urc[1]),
        norm=LogNorm(),
    )
    plt.title("Flux Mean")

    plot_extent = geometry.get_mpl_plot_extent(view_direction="z")
    data_slice = geometry.get_slice_of_material_ids(view_direction="z")
    xlabel, ylabel = geometry.get_axis_labels(view_direction="z")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.contour(
        np.fliplr(data_slice),
        origin="upper",
        colors="k",
        linestyles="solid",
        linewidths=1,
        extent=plot_extent,
    )

    plt.subplot(1, 2, 2)
    # # create a plot of the flux relative error
    flux_std_dev = flux_tally.get_values(value="std_dev").reshape(*mesh.dimension)
    plt.imshow(
        flux_std_dev,
        origin="lower",
        extent=(llc[0], urc[0], llc[1], urc[1]),
        norm=LogNorm(),
    )
    plt.title("Flux Std. Dev.")

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.contour(
        np.fliplr(data_slice),
        origin="upper",
        colors="k",
        linestyles="solid",
        linewidths=1,
        extent=plot_extent,
    )
    plt.savefig(filename)
    return sp


run_and_plot(model, "no_survival_biasing.png")

model.settings.survival_biasing = True
model.settings.cutoff = {
    "weight": 0.3,  # value needs to be between 0 and 1
    "weight_avg": 0.9,  # value needs to be between 0 and 1
}
run_and_plot(model, "yes_survival_biasing.png")
