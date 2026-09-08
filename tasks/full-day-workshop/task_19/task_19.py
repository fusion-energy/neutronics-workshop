# %% [markdown]
# ---
# title: CAD conversion in memory
# ---

# %% [markdown]
# It is possible to convert from a CadQuery object to a DAGMC surface or volume mesh.
#
# This is quicker and more concise than writing to file and reading it in again.
#
# First import the packages needed for the cad creation ([CadQuery](https://cadquery.readthedocs.io)) and conversion ([cad_to_dagmc](https://github.com/fusion-energy/cad_to_dagmc))

# %%
from cad_to_dagmc import CadToDagmc
import cadquery as cq

# %% [markdown]
# CadQuery has a built in viewer for Jupyter but it writes JavaScript that
# needs a live notebook, so it shows nothing in this rendered book.
#
# This small function converts the CAD into a surface mesh and shows it with
# PyVista, the same viewer used for the vtk files later in the workshop, which
# works both in Jupyter and in the book.

# %%
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
# Make some CAD geometry, we have lots of options here but to keep the example concise I've made some text.
#
# The important thing to note here is that we have 10 separate solids in the CAD model

# %%
text = cq.Workplane().text(txt="cad to dagmc", fontsize=10, distance=1)
show_cad(text)

# %% [markdown]
# Next we make an instance of CadToDagmc with this geometry to prepare for conversion

# %%
my_model = CadToDagmc()
my_model.add_cadquery_object(
    cadquery_object=text,
    material_tags=["mat1"]* 10  # ten volumes each with with material tag "mat1"
)

# %% [markdown]
# The ```export_dagmc_h5m_file()``` function will make a surface mesh geometry of the CAD ready for use in neutronics simulations.
#
# With openmc this DAGMC h5m file can be loading in using the ```openmc.DAGMCUniverse``` class.
#
# This makes a 2D mesh / surface mesh / faceted geometry / triangles of the geometry faces.
#
# With this type of geometry you can do simulations and score material tallies, cell tallies directly on the mesh volumes.
#
# You can also overlay OpenMC meshes such as regular mesh or cylindrical mesh on top of the geometry.
#
# The ```export_dagmc_h5m_file()``` function supports different arguments to control the mesh parameters.
#
# For this example we will use simple settings for ```max_mesh_size``` and ```min_mesh_size```.
#
# To see more options take a look at the [cad_to_dagmc package](https://github.com/fusion-energy/cad_to_dagmc)

# %%
my_model.export_dagmc_h5m_file(
    filename="dagmc.h5m",
    max_mesh_size=10,
    min_mesh_size=2,
)

# %% [markdown]
# DAGMC and OpenMC support another form of mesh often called an unstructured mesh.
#
# An unstructured mesh can be overlaid over the geometry much like a regular mesh or cylindrical mesh and used to score tallies spatially.
#
# The ```openmc.UnstructuredMesh``` class supports MOAB and LibMesh type unstructured meshes.
#
# In this example we are making a MOAB / DAGMC unstructured mesh which is entirely made of tetrahedrals.
#
# This is a volume mesh where the outer surface is also the same as the outer surface of the 2D mesh as we have used the same mesh parameters.
#
# This means we have a conformal volume mesh to score on which aligns to the material / cell boundaries in the DAGMC h5m 2D mesh.
#
# This conformal mesh is one of the advantages of UnstructuredMesh over regular meshes and cylindrical meshes
#
# The ```export_unstructured_mesh_file()``` function will produce a vtk file than can be loaded into OpenMC using ```openmc.UnstructuredMesh```

# %%
my_model.export_unstructured_mesh_file(
    filename="dagmc.vtk",
    max_mesh_size=10,
    min_mesh_size=2,
)

# %% [markdown]
# Now you have two mesh files that can be used for neutronics simulations in OpenMC or other DAGMC compatible codes.
#
# Learning objectives for this task
# - Know how to produce DAGMC 2d surface mesh geometry
# - Know how to produce DAGMC 3d volume mesh
# - Understand the differences between the types of meshes produced by cad-to-dagmc
# - know some of the arguments for customising the mesh
