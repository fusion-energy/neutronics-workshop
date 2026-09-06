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

my_reactor

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

my_reactor

# %% [markdown]
# Further parameters are supported such as PF and TF magnets and divertors. Of course you can also add any CadQuery geometry so the models can be highly customised. Here is one final example of a more complete tokamak
#
# See if you can color the divertor blue in this more complex model

# %%
import cadquery as cq

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
my_reactor

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
