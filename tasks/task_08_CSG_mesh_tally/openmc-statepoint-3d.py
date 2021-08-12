#!/usr/env/python3

"""
Script for converting OpenMC mesh in an OpenMC
statepoint file to other mesh formats for visualization
"""

import argparse
import sys
import math
import openmc
import numpy as np


def write_moab(xs, ys, zs, tally_label, tally_data, error_data, outfile):
    # attempt to import pymoab
    try:
        from pymoab import core
        from pymoab.hcoord import HomCoord
        from pymoab.scd import ScdInterface
        from pymoab import types
    except (ImportError, ModuleNotFoundError):
        msg = "Conversion to MOAB .h5m file requested," "but PyMOAB is not installed"
        raise ImportError(msg)

    mb = core.Core()

    scd = ScdInterface(mb)

    coords = []
    for k in zs:
        for j in ys:
            for i in xs:
                coords += [i, j, k]

    low = HomCoord([0, 0, 0, 0])
    high = HomCoord([len(xs) - 1, len(ys) - 1, len(zs) - 1, 0])

    scdbox = scd.construct_box(low, high, coords)

    hexes = mb.get_entities_by_type(0, types.MBHEX)

    tally_tag = mb.tag_get_handle(
        tally_label, 1, types.MB_TYPE_DOUBLE, types.MB_TAG_DENSE, True
    )
    error_tag = mb.tag_get_handle(
        "error_tag", 1, types.MB_TYPE_DOUBLE, types.MB_TAG_DENSE, True
    )

    mb.tag_set_data(tally_tag, hexes, tally_data)
    mb.tag_set_data(error_tag, hexes, error_data)

    print("Writing %s" % outfile)

    mb.write_file(outfile)


def write_vtk(xs, ys, zs, tally_label, tally_data, error_data, outfile):
    try:
        import vtk
    except (ImportError, ModuleNotFoundError) as e:
        msg = (
            "Conversion to VTK requested," "but the Python VTK module is not installed."
        )
        raise ImportError(msg)

    vtk_box = vtk.vtkRectilinearGrid()

    vtk_box.SetDimensions(len(xs), len(ys), len(zs))

    vtk_x_array = vtk.vtkDoubleArray()
    vtk_x_array.SetName("x-coords")
    vtk_x_array.SetArray(xs, len(xs), True)
    print(vtk_x_array)
    vtk_box.SetXCoordinates(vtk_x_array)

    vtk_y_array = vtk.vtkDoubleArray()
    vtk_y_array.SetName("y-coords")
    vtk_y_array.SetArray(ys, len(ys), True)
    vtk_box.SetYCoordinates(vtk_y_array)

    vtk_z_array = vtk.vtkDoubleArray()
    vtk_z_array.SetName("z-coords")
    vtk_z_array.SetArray(zs, len(zs), True)
    vtk_box.SetZCoordinates(vtk_z_array)

    tally = np.array(tally_data)
    tally_data = vtk.vtkDoubleArray()
    tally_data.SetName(tally_label)
    tally_data.SetArray(tally, tally.size, True)

    error = np.array(error_data)
    error_data = vtk.vtkDoubleArray()
    error_data.SetName("error_tag")
    error_data.SetArray(error, error.size, True)

    vtk_box.GetCellData().AddArray(tally_data)
    vtk_box.GetCellData().AddArray(error_data)

    writer = vtk.vtkRectilinearGridWriter()

    writer.SetFileName(outfile)

    writer.SetInputData(vtk_box)

    print("Writing %s" % outfile)

    writer.Write()


def initiate_mesh(statepoint_filename, tally_name, output_filename, mesh_id, tally_id):

    print("Loading file %s" % input_filename)

    sp = openmc.StatePoint(input_filename)

    print("Loading mesh with ID of %s" % mesh_id)
    mesh = sp.meshes[mesh_id]

    xs = np.linspace(mesh.lower_left[0], mesh.upper_right[0], mesh.dimension[0] + 1)
    ys = np.linspace(mesh.lower_left[1], mesh.upper_right[1], mesh.dimension[1] + 1)
    zs = np.linspace(mesh.lower_left[2], mesh.upper_right[2], mesh.dimension[2] + 1)

    tally_args = {"name": tally_name, "id": tally_id}

    msg = "Loading retrieving tally with \n"
    if tally_name is not None:
        msg += "Name: {}\n".format(tally_name)
    if tally_id is not None:
        msg += "ID: {}\n".format(tally_id)
    try:
        tally = sp.get_tally(**tally_args)
    except LookupError as e:
        raise e

    data = tally.mean[:, 0, 0]
    error = tally.std_dev[:, 0, 0]

    data = data.tolist()
    error = error.tolist()

    for c, i in enumerate(data):
        if math.isnan(i):
            data[c] = 0.0

    for c, i in enumerate(error):
        if math.isnan(i):
            error[c] = 0.0

    if tally_name is None:
        tally_label = "tally_{}".format(tally_id)
    else:
        tally_label = tally_name

    if output_filename.endswith(".vtk"):
        write_vtk(xs, ys, zs, tally_label, data, error, output_filename)
    else:
        write_moab(xs, ys, zs, tally_label, data, error, output_filename)


def main():

    ap = argparse.ArgumentParser(description=__doc__)

    ap.add_argument("-i", "--input", required=True, help="Path to statepoint h5 file")

    ap.add_argument("-n", "--tally-name", help="Tally name to add to mesh")

    ap.add_argument(
        "-t", "--tally-id", type=int, required=True, help="Tally name to add to mesh"
    )

    ap.add_argument(
        "-m", "--mesh-id", type=int, required=True, help="ID of the mesh to convert"
    )

    ap.add_argument(
        "-o",
        "--output",
        action="store",
        default="meshtally.vtk",
        help="Name of outputfile (.h5m for MOAB, .vtk for VTK)",
    )

    args = ap.parse_args()

    initiate_mesh(
        statepoint_filename=args.input,
        tally_name=args.tally_name,
        output_filename=args.output,
        mesh_id=args.mesh_id,
        tally_id=args.tally_id,
    )


if __name__ == "__main__":
    main()
