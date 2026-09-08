# %% [markdown]
# ---
# title: Making CAD geometry with Paramak
# ---

# %% [markdown]
# We learned how to make some basic shapes with CadQuery.
#
# Now if only there was a short cut to making a complete reactor model
#
# Good news there is a package called Paramak that makes parametric CAD for Tokamak geometries.
#
# The resulting geometry is a CadQuery Assembly so it can be added to and customised further.
#
# In this example we are going to make a few simple reactors.

# %%
import paramak

# %% [markdown]
# CadQuery has a built in viewer for Jupyter but it writes JavaScript that
# needs a live notebook, so it shows nothing in this rendered book.
#
# This small function converts the CAD into a surface mesh and shows it with
# PyVista, the same viewer used for the vtk files later in the workshop, which
# works both in Jupyter and in the book.

# %%
import cadquery as cq
import pyvista as pv
from cadquery.occ_impl.exporters.vtk import extractEdgesFaces
from IPython.display import HTML


def show_cad(cad_object, tolerance=1e-3, angular_tolerance=0.1):
    """Shows a CadQuery Workplane, Shape or Assembly with PyVista.

    The tolerance is the relative deviation of the surface mesh from the CAD
    surface, smaller values give a smoother shape and a larger web page.
    """

    if isinstance(cad_object, cq.Assembly):
        parts = [(shape.moved(location), color) for shape, _, location, color in cad_object]
    elif isinstance(cad_object, cq.Workplane):
        parts = [(cad_object.val(), None)]
    else:
        parts = [(cad_object, None)]

    plotter = pv.Plotter(off_screen=True)
    for shape, color in parts:
        polydata = shape.toVtkPolyData(tolerance, angular_tolerance)
        # the cell arrays CadQuery attaches do not match the number of cells,
        # dropping them keeps VTK quiet when the scene is rendered
        polydata.GetCellData().Initialize()
        edges, faces = extractEdgesFaces(polydata)
        # the default is the same gold color that the CadQuery viewer uses
        red, green, blue, alpha = color.toTuple() if color else (1.0, 0.8, 0.0, 1.0)
        plotter.add_mesh(pv.wrap(faces), color=(red, green, blue), opacity=alpha)
        plotter.add_mesh(pv.wrap(edges), color='black', line_width=2)

    # PyVista would return an ipywidget here, an iframe holding the same scene
    # is used instead because it keeps the web page about half the size
    scene = plotter.trame.export_html(filename=None).getvalue()
    source = scene.replace('&', '&amp;').replace('"', '&quot;')
    return HTML(
        f'<div><iframe srcdoc="{source}" style="width:100%; height:600px; '
        'border:1px solid rgb(221,221,221);"></iframe></div>'
    )

# %% [markdown]
# We will start with the most minimal tokamak, this spherical_tokamak_from_plasma offers some parameters for the user to customise the shape, number of layers and layer thickness.
#
# Try changing the elongation and triangularity or some of the layer thicknesses

# %%
my_reactor = paramak.spherical_tokamak_from_plasma(
    radial_build=[
        (paramak.LayerType.GAP, 10),
        (paramak.LayerType.SOLID, 50),
        (paramak.LayerType.SOLID, 15),
        (paramak.LayerType.GAP, 50),
        (paramak.LayerType.PLASMA, 300),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 15),
        (paramak.LayerType.SOLID, 60),
        (paramak.LayerType.SOLID, 10),
    ],
    elongation=2,
    triangularity=0.55,
    rotation_angle=180,
)

show_cad(my_reactor)

# %% [markdown]
# There are other reactor types available such as this tokamak function. This allows both a radial and vertical build profile to be specified.
#
# We also add some color to this one

# %%
my_reactor = paramak.tokamak(
    radial_build=[
        (paramak.LayerType.GAP, 10),
        (paramak.LayerType.SOLID, 30),
        (paramak.LayerType.SOLID, 50),
        (paramak.LayerType.SOLID, 10),
        (paramak.LayerType.SOLID, 70),
        (paramak.LayerType.SOLID, 20),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.PLASMA, 300),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 20),
        (paramak.LayerType.SOLID, 110),
        (paramak.LayerType.SOLID, 10),
    ],
    vertical_build=[
        (paramak.LayerType.SOLID, 15),
        (paramak.LayerType.SOLID, 80),
        (paramak.LayerType.SOLID, 10),
        (paramak.LayerType.GAP, 50),
        (paramak.LayerType.PLASMA, 700),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 10),
        (paramak.LayerType.SOLID, 40),
        (paramak.LayerType.SOLID, 15),
    ],
    triangularity=0.55,
    rotation_angle=180,
    colors={
        'layer_1':(0.4, 0.9, 0.4),  # center column
        'layer_2':(0.6, 0.8, 0.6),  # magnet shield
        'layer_3':(0.1, 0.8, 0.6),  # first wall
        'layer_4':(0.1, 0.1, 0.9),  # breeder
        'layer_5':(0.4, 0.4, 0.8),  # rear wall
        'plasma':(1., 0.7, 0.8, 0.6),  # plasma has 4 numbers as the last number is the transparency
    },
)

show_cad(my_reactor)

# %% [markdown]
# Further parameters are supported such as PF and TF magnets and divertors. Of course you can also add any CadQuery geometry so the models can be highly customised. Here is one final example of a more complete tokamak
#
# See if you can color the divertor blue in this more complex model

# %%
# makes a rectangle that overlaps the lower blanket under the plasma
# the intersection of this and the layers will form the lower divertor
points = [(300, -700), (300, 0), (400, 0), (400, -700)]
divertor_lower = cq.Workplane("XZ", origin=(0, 0, 0)).polyline(points).close().revolve(180)

# creates a toroidal
tf = paramak.toroidal_field_coil_rectangle(
    horizontal_start_point=(10, 520),
    vertical_mid_point=(860, 0),
    thickness=50,
    distance=40,
    rotation_angle=180,
    with_inner_leg=True,
    azimuthal_placement_angles=[0, 30, 60, 90, 120, 150, 180],
)

extra_cut_shapes = [tf]

# creates pf coil
for case_thickness, height, width, center_point in zip(
    [10, 15, 15, 10], [20, 50, 50, 20], [20, 50, 50, 20], [(730, 370), (810, 235), (810, -235), (730, -370)]
):
    extra_cut_shapes.append(
        paramak.poloidal_field_coil(height=height, width=width, center_point=center_point, rotation_angle=180)
    )
    extra_cut_shapes.append(
        paramak.poloidal_field_coil_case(
            coil_height=height,
            coil_width=width,
            casing_thickness=case_thickness,
            rotation_angle=180,
            center_point=center_point,
        )
    )

my_reactor = paramak.tokamak(
    radial_build=[
        (paramak.LayerType.GAP, 10),
        (paramak.LayerType.SOLID, 30),
        (paramak.LayerType.SOLID, 50),
        (paramak.LayerType.SOLID, 10),
        (paramak.LayerType.SOLID, 60),
        (paramak.LayerType.SOLID, 60),
        (paramak.LayerType.SOLID, 20),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.PLASMA, 300),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 20),
        (paramak.LayerType.SOLID, 60),
        (paramak.LayerType.SOLID, 60),
        (paramak.LayerType.SOLID, 10),
    ],
    vertical_build=[
        (paramak.LayerType.SOLID, 10),
        (paramak.LayerType.SOLID, 50),
        (paramak.LayerType.SOLID, 50),
        (paramak.LayerType.SOLID, 20),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.PLASMA, 650),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 20),
        (paramak.LayerType.SOLID, 50),
        (paramak.LayerType.SOLID, 50),
        (paramak.LayerType.SOLID, 10),
    ],
    triangularity=0.55,
    rotation_angle=180,
    extra_cut_shapes=extra_cut_shapes,
    extra_intersect_shapes=[divertor_lower],
    colors={
        # TODO see if you can color the divertor
        # 'add_extra_cut_shape_1':
        # 'add_extra_cut_shape_2':
        # 'add_extra_cut_shape_3':
        # 'add_extra_cut_shape_4':
        # 'add_extra_cut_shape_5':
        # 'add_extra_cut_shape_6':
        # 'add_extra_cut_shape_7':
        # 'add_extra_cut_shape_8':
        # 'add_extra_cut_shape_9':
        # 'extra_intersect_shapes_1':
        'layer_1':(0.4, 0.9, 0.4),
        'layer_2':(0.6, 0.8, 0.6),
        'layer_3':(0.1, 0.8, 0.6),
        'layer_4':(0.1, 0.1, 0.9),
        'layer_5':(0.4, 0.4, 0.8),
        'layer_6': (0.5, 0.5, 0.8),
        'plasma':(1., 0.7, 0.8, 0.6),
    },
)
show_cad(my_reactor)

# %% [markdown]
# Of course these can be saved as STEP, BREP, STL files or added to just like a CadQuery assembly.
#
# ```my_reactor.names()``` is also useful for getting all the names of the parts in the assembly
#
#
# More details on Paramak
# - On the source code repository https://github.com/fusion-energy/paramak
# - On the documentation https://fusion-energy.github.io/paramak/stable/index.html
# - Example Paramak models https://github.com/fusion-energy/paramak/tree/main/examples
