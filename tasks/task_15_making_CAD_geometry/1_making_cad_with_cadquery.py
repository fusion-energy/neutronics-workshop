# %% [markdown]
# ---
# title: Making CAD with CadQuery
# ---

# %% [markdown]
# CadQuery is an intuitive, easy-to-use Python module for building parametric 3D CAD models. Using CadQuery, you can write short, simple scripts that produce high quality CAD models. It is easy to make many different objects using a single script that can be customized.
#
# More details can be found
# - On the documentation https://cadquery.readthedocs.io/en/latest/
# - On GitHub https://github.com/CadQuery/cadquery/
#
# CadQuery is particular well suited to fusion neutronics:
# - CadQuery is used by [cad-to-dagmc](https://github.com/fusion-energy/cad_to_dagmc) to convert CAD geometry to DAGMC neutronics geometry
# - Cadquery can pass geometry in memory to popular meshing software GMsh
# - CadQuery can tag surfaces and volumes so that their tags appear in the meshes and can automate boundary condition assignment in engineering workflows
# - CadQuery is easy to install with pip or conda

# %% [markdown]
# In this task we are going start by making a few simple CAD shapes

# %% [markdown]
# First we import cadquery

# %%
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

# %%
circle_solid = cq.Workplane("XY").circle(1.0).extrude(3.0)

show_cad(circle_solid)

# %% [markdown]
# More complex shapes can be made that include splines. These types of curves are not available with traditional CSG geometry 

# %%
xyz_coordinates = [
    (-1.0, -2.0),
    (-0.5, 2.0),
    (1.0, 3.0),
    (2.0, 2.0),
]
spine_solid = cq.Workplane("XY").spline(listOfXYTuple=xyz_coordinates, periodic=True).close().extrude(0.5)
show_cad(spine_solid)

# %% [markdown]
# Boolean operations are also supported

# %%
cut_spline = spine_solid.cut(circle_solid)
show_cad(cut_spline)

# %% [markdown]
# Assemblies can also be built up to contain several shapes

# %%
assembly = cq.Assembly()
assembly.add(circle_solid, color=cq.Color("red"))
assembly.add(cut_spline, color=cq.Color("blue"))
show_cad(assembly)

# %% [markdown]
# CAD geometry can also be save to STEP files which are a well supported open standard CAD file format 

# %%
assembly.export('my-cad-geometry.step')

from pathlib import Path
print(sorted(path.name for path in Path('.').glob('*.step')))

# %% [markdown]
# We can also load CAD files with CadQuery

# %%
loaded_shape = cq.importers.importStep('my-cad-geometry.step')
show_cad(loaded_shape)

# %% [markdown]
# The benefits of CAD geometry over CSG are:
# - CAD can be used to make more complex geometry
# - CAD can be used by other disciplines (e.g. mechanical engineering)
# - The void space does not need to be defined when we convert the geometry to a neutronics geomeyty. More on this later
#
# The potential disadvantage is that simulations might be slower. However understanding neutron transport algorthiums and building geometry well can help minimise this disadvantage.
#
# For more information on CadQuery take a look at the CadQuery examples 
# - https://cadquery.readthedocs.io/en/latest/examples.html
# - https://cadquery.readthedocs.io/en/latest/free-func.html
# - https://cadquery.readthedocs.io/en/latest/sketch.html
# - https://cadquery.readthedocs.io/en/latest/assy.html

# %%
text = cq.Workplane().text(txt="GitHub stars are appreciated ", fontsize=10, distance=1)
text.export('cad_geometry.step')
show_cad(text)
