
from cad_to_dagmc import CadToDagmc
import cadquery as cq
import openmc
from matplotlib.colors import LogNorm
import openmc.deplete
from pathlib import Path
import numpy as np


openmc.config['chain_file'] = Path.home() / 'nuclear_data' / 'chain-endf-b8.0.xml'
openmc.config['cross_sections'] = Path.home() / 'nuclear_data' / 'cross_sections.xml'

# makes a CAD geometry to use for the neutronics geometry
text = cq.Workplane().text(txt="R2S", fontsize=10, distance=1)

my_model = CadToDagmc()
my_model.add_cadquery_object(
    cadquery_object=text,
    material_tags=[
        "mat1",
        "mat2",
        "mat3",
    ],  # 3 volumes one for each letter
)

my_model.export_dagmc_h5m_file(
    filename="dagmc.h5m",
    max_mesh_size=10,
    min_mesh_size=2,
)
my_model.export_unstructured_mesh_file(
    filename="umesh.vtk",
    max_mesh_size=10,
    min_mesh_size=2,
)

# the unstructured mesh to overlay on the DAGMC geometry
umesh = openmc.UnstructuredMesh("umesh.vtk", library="moab")
# filters for use inf the tally
mesh_filter = openmc.MeshFilter(umesh)
neutron_particle_filter = openmc.ParticleFilter(['neutron'])
energy_filter = openmc.EnergyFilter.from_group_structure('CCFE-709')

# sets up a neutron spectra tally on the unstructured mesh 
tally = openmc.Tally(name="unstructured_mesh_neutron_spectra_tally")
tally.filters = [mesh_filter, energy_filter, neutron_particle_filter]
tally.scores = ["flux"]
tally.estimator = "tracklength"
my_tallies = openmc.Tallies([tally])

fe_material = openmc.Material(name='mat1')
fe_material.add_nuclide("Fe56", 1, percent_type="ao") 
fe_material.set_density("g/cm3", 7.874)
fe_material.depletable = True

Li4SiO4_mat = openmc.Material(name='mat2')
Li4SiO4_mat.add_element('Li', 4.0, percent_type='ao')
Li4SiO4_mat.add_element('Si', 1.0, percent_type='ao')
Li4SiO4_mat.add_element('O', 4.0, percent_type='ao')
Li4SiO4_mat.set_density('g/cm3', 2.32) 
Li4SiO4_mat.depletable = True

water_mat = openmc.Material(name='mat3')
water_mat.add_element('H', 2.0, percent_type='ao')
water_mat.add_element('O', 1.0, percent_type='ao')
water_mat.set_density('g/cm3', 0.99821) 
water_mat.depletable = True


my_materials = openmc.Materials([fe_material, Li4SiO4_mat, water_mat])

universe = openmc.DAGMCUniverse("dagmc.h5m").bounded_universe()
my_geometry = openmc.Geometry(universe)

# Get the bounding box of the geometry and find its center for source positioning
box = my_geometry.bounding_box
geometry_center = box.center

my_settings = openmc.Settings()
my_settings.batches = 10
my_settings.inactive = 0
my_settings.particles = 5000
my_settings.run_mode = "fixed source"
my_settings.output = {'tallies': False}

# Create a DT point source
my_source = openmc.IndependentSource()
my_source.space = openmc.stats.Point(geometry_center)
my_source.angle = openmc.stats.Isotropic()
my_source.energy = openmc.stats.Discrete([14e6], [1])
my_settings.source = my_source

model = openmc.model.Model(my_geometry, my_materials, my_settings, my_tallies)
model.export_to_xml()   

timesteps_and_source_rates = [
    (5, 1e20),  # 5 second  
    (60, 0),  # 60 seconds
    (60, 0) # 60 seconds
]

timesteps = [item[0] for item in timesteps_and_source_rates]
source_rates = [item[1] for item in timesteps_and_source_rates]

sp_filename = model.run()

sp = openmc.StatePoint(sp_filename)

tally_result = sp.get_tally(name="unstructured_mesh_neutron_spectra_tally")
# normally with regular meshes I would get the mesh from the tally
# but with unstrucutred meshes the tally does not contain the mesh
# however we can get it from the statepoint file
# umesh = tally_result.find_filter(openmc.MeshFilter)
umesh_from_sp = sp.meshes[umesh.id]

# these trigger internal code in the mesh object so that its centroids and volumes become known.
# centroids and volumes are needed for the get_values and write_data_to_vtk steps
centroids = umesh_from_sp.centroids
mesh_vols = umesh_from_sp.volumes

# get material volumes for each mesh element from the unstructured mesh
mat_vol = umesh_from_sp.material_volumes(model=model,n_samples=1_000_000)

# Get all volumes for material ID 10
# Get material IDs from my_materials object
material_ids = [mat.id for mat in my_materials]
volumes = {mid: mat_vol[mid] for mid in material_ids}
nonzero_volumes = {mid: vol[vol != 0] for mid, vol in volumes.items()}
total_volumes = {mid: np.sum(nvol) for mid, nvol in nonzero_volumes.items()}

# Add total volume to each material
for mat, mat_id in zip(my_materials, material_ids):
    mat.volume = total_volumes[mat_id]

# flux in each group for each voxel return a array that is energy_groups x mesh_elements x 1 x 1
# reshape to energy_groups x mesh_elements
flux_in_each_group_for_each_voxel = tally_result.get_values(scores=["flux"], value="mean")
flux_in_each_group_for_each_voxel = flux_in_each_group_for_each_voxel.reshape(mesh_vols.size, energy_filter.num_bins)

for i_cool in range(1, len(timesteps)):
    print(f"Depleting to time {i_cool}")
    all_sources = []

    # First, create a dictionary to group mesh elements by material
    material_groups = {}
    for i, (flux_in_each_group, mesh_vol) in enumerate(zip(flux_in_each_group_for_each_voxel, mesh_vols)):
        element_volumes = mat_vol.by_element(i)
        for mat_id, vol in element_volumes:
            if vol > 0:
                if mat_id not in material_groups:
                    material_groups[mat_id] = []
                material_groups[mat_id].append((i, flux_in_each_group, mesh_vol))
                break

    # Then process each material group
    for mat_id, elements in material_groups.items():
        current_material = next(mat for mat in my_materials if mat.id == mat_id)
        
        # Create MicroXS once per material
        micro_xs = openmc.deplete.MicroXS.from_multigroup_flux(
            energies='CCFE-709',
            multigroup_flux=elements[0][1],  # Use first element's flux
            temperature=294,
            chain_file=openmc.config['chain_file'],
            nuclides=current_material.get_nuclides()
        )
        
        # Process all elements for this material
        for i, flux_in_each_group, mesh_vol in elements:
            # Process each element with shared resources
            # constructing the operator with only the current material
            operator = openmc.deplete.IndependentOperator(
                materials=[current_material],  # Only use the material present in this element
                fluxes=[sum(flux_in_each_group)*mesh_vol],
                micros=[micro_xs],
                reduce_chain_level=5,
                normalization_mode="source-rate"
            )
            integrator = openmc.deplete.PredictorIntegrator(
                operator=operator,
                timesteps=timesteps,
                source_rates=source_rates, # a 5 second pulse of neutrons followed by 120 seconds of decay
                timestep_units='s'
            )

            integrator.integrate()
            results = openmc.deplete.Results.from_hdf5("depletion_results.h5")
            activated_material = results[i_cool].get_material(str(current_material.id))

            activated_material.volume = mesh_vol

            energy = activated_material.get_decay_photon_energy(
                clip_tolerance = 1e-6,  # cuts out a small fraction of the very low energy (and hence negligible dose contribution) photons
                units = 'Bq',
            )
            if energy:
                strength = energy.integral()
            # for the strength == None case
            else:
                strength = 0
            # Get the vertices of the tetrahedron from the mesh
            vertices = umesh_from_sp.vertices[umesh_from_sp.connectivity[i]]
            
            # Calculate bounding box of the tetrahedron
            min_coords = np.min(vertices, axis=0)
            max_coords = np.max(vertices, axis=0)
            
            # Create a uniform sampling distribution within the bounding box
            # We'll use rejection sampling to ensure points are within the tetrahedron
            my_source = openmc.IndependentSource(
                space = openmc.stats.Box(
                    lower_left=min_coords,
                    upper_right=max_coords
                ),
                energy = energy,
                particle = "photon",
                strength = strength,
                constraints={
                    'domains': [activated_material],
                    'rejection_strategy': 'resample'
                }        
            )
            all_sources.append(my_source)
    #%%
    photon_folder = Path('photons')
    photon_folder.mkdir(exist_ok=True)

    mesh_source = openmc.MeshSource(
        mesh=umesh_from_sp,
        sources=all_sources,
    )
    my_gamma_settings = openmc.Settings()
    my_gamma_settings.run_mode = "fixed source"
    my_gamma_settings.batches = 100
    my_gamma_settings.particles = 100000
    my_gamma_settings.output = {'tallies': False}
    my_gamma_settings.source = mesh_source


    energies, pSv_cm2 = openmc.data.dose_coefficients(particle="photon", geometry="AP")
    dose_filter = openmc.EnergyFunctionFilter(
        energies, pSv_cm2, interpolation="cubic"  # interpolation method recommended by ICRP
    )
    regularmesh = openmc.RegularMesh().from_domain(
        my_geometry,
        dimension=[50, 50, 50],  # 10 voxels in each axis direction (x, y, z)
    )

    particle_filter = openmc.ParticleFilter(["photon"])
    mesh_filter = openmc.MeshFilter(regularmesh)
    dose_tally = openmc.Tally()
    dose_tally.filters = [mesh_filter, dose_filter, particle_filter]
    dose_tally.scores = ["flux"]
    dose_tally.name = "photon_dose_on_mesh"
    tallies = openmc.Tallies([dose_tally])

    my_gamma_materials = results.export_to_materials(i_cool)

    model_gamma = openmc.Model(my_geometry, my_gamma_materials, my_gamma_settings, tallies)
    model_gamma.export_to_xml(photon_folder / f"photon_at_time_{i_cool}")
    model_gamma.run(cwd=photon_folder / f"photon_at_time_{i_cool}")
#%%
for i_cool in range(1, len(timesteps)):
    from openmc_regular_mesh_plotter import plot_mesh_tally
    with openmc.StatePoint(photon_folder / f"photon_at_time_{i_cool}" / 'statepoint.100.h5') as statepoint:
        photon_tally = statepoint.get_tally(name="photon_dose_on_mesh")

        # normalising this tally is a little different to other examples as the source strength has been using units of photons per second.
        # tally.mean is in units of pSv-cm3/source photon.
        # as source strength is in photons_per_second this changes units to pSv-/second

        # multiplication by pico_to_micro converts from (pico) pSv/s to (micro) uSv/s
        # dividing by mesh voxel volume cancles out the cm3 units
        # could do the mesh volume scaling on the plot and vtk functions but doing it here instead
        pico_to_micro = 1e-6
        seconds_to_hours = 60*60
        scaling_factor = (seconds_to_hours * pico_to_micro) / regularmesh.volumes[0][0][0]

        plot = plot_mesh_tally(
                tally=photon_tally,
                basis="xz",
                # score='flux', # only one tally so can make use of default here
                value="mean",
                colorbar_kwargs={
                    'label': "Decay photon dose [µSv/h]",
                },
                norm=LogNorm(),
                volume_normalization=False,  # this is done in the scaling_factor
                scaling_factor=scaling_factor,
            )
        plot.figure.savefig(photon_folder / f"photon_at_time_{i_cool}" / f"shut_down_dose_map_timestep_{i_cool}.png")
