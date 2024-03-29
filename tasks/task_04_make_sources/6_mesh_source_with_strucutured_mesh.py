

import openmc

sphere_surf_1 = openmc.Sphere(r=2000)
sphere_region_1 = -sphere_surf_1
sphere_cell_1 = openmc.Cell(region=sphere_region_1, )

my_geometry = openmc.Geometry([sphere_cell_1])


cylindrical_mesh = openmc.CylindricalMesh().from_domain(
    my_geometry, # the corners of the mesh are being set automatically to surround the geometry
    dimension=[10,10,10] # 10
)

centroids
# for mesh_voxel in cylindrical_mesh.

# mesh_source = openmc.MeshSource(
#     mesh=cylindrical_mesh,
#     sources 
# )
