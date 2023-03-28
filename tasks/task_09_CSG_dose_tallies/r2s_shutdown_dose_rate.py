# makes a sphere of iron and another sphere of tungsten and irradiates them
# with a 2MeV point neutron source.
# The activated material emits gammas and these are transported and tallied
# on a mesh tally. The resulting decay gamma flux is plotted as a series of
# images so that the variation / decay over time can be observed.
from pathlib import Path
import openmc
import typing
import matplotlib.pyplot as plt
import numpy as np
import regular_mesh_plotter  # extends openmc.Mesh to include data slice functions
import openmc_geometry_plot  # extends openmc.Geometry class with plotting functions
import math
from matplotlib.colors import LogNorm

# be sure to have matching chain and cross section file
openmc.config['chain_file'] = '/home/jshimwell/m4_csg_neutronics_model/chain-nndc-b8.0.xml'
openmc.config['cross_sections'] = '/home/jshimwell/openmc_data/nndc-b8.0-hdf5/endfb-viii.0-hdf5/cross_sections.xml'

# R2SModel class code is by eepeterson
# with a few tiny modifications made by shimwell
# this is not merged into openmc
# Adding the class to the script to allow usage within the script
# If this gets merged into openmc then this class can be removed
class R2SModel(openmc.Model):
    """A Model container for an R2S calculation.
    Parameters
    ----------
    Attributes
    ----------
    timesteps : iterable of float
        Array of timesteps in units of [s]. Note that values are not
        cumulative.
    source_rates : float or iterable of float, optional
        Source rate in [neutron/sec] or neutron flux in [neutron/s-cm^2] for
        each interval in :attr:`timesteps`
    depletion_options : dict
        dictionary with model.deplete kwargs
    photon_timesteps : iterable of int
        which depletion steps to do photon transport for
    photon_settings : openmc.Settings object
        The simulation settings to use for photon timesteps
    photon_tallies : openmc.Tallies object
        The tallies to use for photon timesteps
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ntransport_path = Path('neutron_transport')
        self.depletion_path = Path('depletion')
        self.ptransport_path = Path('photon_transport')
        depletion_options = {}
        depletion_options['method'] = 'predictor'
        depletion_options['final_step'] = False
        operator_kwargs={
            'normalization_mode': 'source-rate',
            'dilute_initial': 0,
            'reduce_chain': True,
            'reduce_chain_level': 5
        }
        depletion_options['operator_kwargs'] = operator_kwargs
        self.depletion_options = depletion_options

    def execute_run(self, **kwargs):
        # Do neutron transport and depletion calcs
        self.export_to_xml(self.ntransport_path)
        #super().run(cwd=self.ntransport_path)
        self.deplete(self.timesteps,
                     directory=self.depletion_path,
                     source_rates=self.source_rates,
                     **self.depletion_options
                     )

        # Read in results and get new depleted materials
        results = openmc.deplete.Results.from_hdf5(self.depletion_path / "depletion_results.h5")
        matlist = [results.export_to_materials(i, path=self.depletion_path/'materials.xml')
                   for i in range(len(self.timesteps))]

        # Set up photon calculation
        self.settings = self.photon_settings

        total_strength = sum(src.strength for src in self.settings.source)
        print('total source strength', total_strength)

        self.settings.photon_transport = True
        self.tallies = self.photon_tallies

        statepoint_paths = []
        # Run photon transport for each desired timestep
        for tidx in self.photon_timesteps:
            # makes a dictionary of materials for easy look up later
            new_mats_by_id = {}
            for new_mat in matlist[tidx]:
                new_mats_by_id[new_mat.id] = new_mat

            rundir = self.ptransport_path / f'timestep_{tidx}'

            # Create Source for every depleted region
            src_list = []
            for cell in self.geometry.get_all_cells().values():
                if cell.fill is None:
                    print(f'cell {cell.id} is not filled, continuing')
                    continue
                print('cell is filled')
                if cell.fill.depletable is False:
                    print(f'cell {cell.id} is not depletable, continuing')
                    continue
                src = openmc.Source.from_cell_with_material(
                    cell, new_mats_by_id[cell.fill.id]
                )
                print(src.strength, src.energy)
                if src is not None:  # some materials will have no photon decays
                    src_list.append(src)

            self.settings.source = src_list
            total_strength = sum(src.strength for src in self.settings.source)
            print('total_strength', total_strength)
            self.export_to_xml(rundir)
            statepoint_path = self.run(cwd=rundir)
            statepoint_paths.append(statepoint_path)
        return statepoint_paths

# this patches openmc to include the new R2SModel class
openmc.R2SModel = R2SModel

class Source(openmc.Source):
    @classmethod
    def from_cell_with_material(
        cls,
        cell: openmc.Cell,
        material: typing.Optional[openmc.Material] = None
    ) -> typing.Optional['openmc.Source']:
        """Generate an isotropic photon source from an openmc.Cell object. By
        default the cells material is used to generate the source. If the
        material used to fill the cell has no photon emission then None is
        returned.

        Parameters
        ----------
        cell : openmc.Cell
            OpenMC cell object to use for the source creation. Source domain is
            set to the cell.
        material : openmc.Material, optional
            OpenMC material object to use for the source creation. If set then
            this material is used preferentially over the cell.fill material.

        Returns
        -------
        Optional[openmc.Source, None]
            Source generated from an openmc.Material or None
        """

        if material is None:
            print('material is None so material is set to ', cell.fill)
            material = cell.fill

        if material is None:
            msg = (
                "Either a material must be provided or the cell must be "
                "filled with an openmc.Material object as this method make "
                "use of a material and the Material.decay_photon_energy method"
            )
            raise ValueError(msg)
        if material.volume is None:
            msg = (
                "The openmc.Material ID={material.id} Name={material.name} "
                "used must have the volume property set"
            )
            raise ValueError(msg)

        photon_spec = material.decay_photon_energy

        if photon_spec is None:
            print('photon_spec is None')
            return None

        source = cls(domains=[cell])
        source.particle = 'photon'
        source.energy = photon_spec
        source.strength = photon_spec.integral()
        source.space = openmc.stats.Box(*cell.bounding_box)
        source.angle = openmc.stats.multivariate.Isotropic()

        return source


# this patches openmc to include the new R2SModel class
openmc.Source = Source

# The actual example starts here ...

# First we make a simple geometry with three cells, (two with material)
sphere_surf_1 = openmc.Sphere(r=20, boundary_type="vacuum")
sphere_surf_2 = openmc.Sphere(r=1, y0=10)
sphere_surf_3 = openmc.Sphere(r=5, z0=10)

sphere_region_1 = -sphere_surf_1 & +sphere_surf_2 & +sphere_surf_3  # void space
sphere_region_2 = -sphere_surf_2
sphere_region_3 = -sphere_surf_3

sphere_cell_1 = openmc.Cell(region=sphere_region_1)
sphere_cell_2 = openmc.Cell(region=sphere_region_2)
sphere_cell_3 = openmc.Cell(region=sphere_region_3)

# We make a iron material which should produce a few activation products
mat_iron = openmc.Material()
mat_iron.id = 1
mat_iron.add_element("Ni", 1.0)
mat_iron.set_density("g/cm3", 1)
# must set the depletion to True to deplete the material
mat_iron.depletable = True
# volume must set the volume as well as openmc calculates number of atoms
mat_iron.volume = (4/3) * math.pi * math.pow(1, 3)
sphere_cell_2.fill = mat_iron

# We make a Al material which should produce a few different activation products
mat_aluminum = openmc.Material()
mat_aluminum.id = 2
mat_aluminum.add_element("W", 1.0)
mat_aluminum.set_density("g/cm3", 19.3)
# must set the depletion to True to deplete the material
mat_aluminum.depletable = True
# volume must set the volume as well as openmc calculates number of atoms
mat_aluminum.volume = (4/3) * math.pi * math.pow(5, 3)
sphere_cell_3.fill = mat_aluminum

my_geometry = openmc.Geometry([sphere_cell_1, sphere_cell_2, sphere_cell_3])

my_materials = openmc.Materials([mat_iron, mat_aluminum])

my_neutron_settings = openmc.Settings()
my_neutron_settings.batches = 10
my_neutron_settings.particles = 500000
my_neutron_settings.run_mode = "fixed source"
my_neutron_settings.photon_transport = True  # ph

source = openmc.Source()
source.space = openmc.stats.Point((0, 0, 0))  # source is located at x 0, y 0, z 0
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([2e6], [1])
my_neutron_settings.source = source

my_photon_settings = openmc.Settings()
my_photon_settings.batches = 10
my_photon_settings.particles = 500000
my_photon_settings.run_mode = "fixed source"

# Create mesh which will be used for tally
mesh = openmc.RegularMesh().from_domain(
    my_geometry,  # the corners of the mesh are being set automatically to surround the geometry
    dimension=[100, 100, 100],
)

mesh_filter = openmc.MeshFilter(mesh)

my_photon_tallies = openmc.Tallies()
# Create mesh filter for tally

# geometry argument refers to irradiation direction
# https://academic.oup.com/view-large/figure/119655666/ncx112f01.png
energy_bins_p, dose_coeffs_p = openmc.data.dose_coefficients(
    particle="photon", geometry="ISO"
)
energy_function_filter_p = openmc.EnergyFunctionFilter(energy_bins_p, dose_coeffs_p)
energy_function_filter_p.interpolation == "cubic"  # as recommended by ICRP

# Create flux mesh tally to score flux
mesh_tally_1 = openmc.Tally(name="photon_dose_on_mesh")
particle_filter = openmc.ParticleFilter(["photon"])
mesh_tally_1.filters = [mesh_filter, particle_filter, energy_function_filter_p]
mesh_tally_1.scores = ["flux"]
my_photon_tallies.append(mesh_tally_1)

r2s_model = openmc.R2SModel(
    geometry=my_geometry,
    materials=my_materials,
    settings=my_neutron_settings,
)

neutrons_per_second = 1e20
timestep_in_seconds = 60 * 60 * 24 * 50  # 50 days in seconds
# We define timesteps together with the source rate to make it clearer
# each timestep is 50 days long
timesteps_and_source_rates = [
    (timestep_in_seconds, neutrons_per_second),
    (timestep_in_seconds, 0),  # cooling timestep with zero neutron flux from here onwards
    (timestep_in_seconds, 0),
    # (timestep_in_seconds, 0),
    # (timestep_in_seconds, 0),
    # (timestep_in_seconds, 0),
    # (timestep_in_seconds, 0),
    # (timestep_in_seconds, 0),
    # (timestep_in_seconds, 0),
    # (timestep_in_seconds, 0),
    # (timestep_in_seconds, 0),
    # (timestep_in_seconds, 0),
]

# Uses list Python comprehension to get the timesteps and source_rates separately
timesteps = [item[0] for item in timesteps_and_source_rates]
source_rates = [item[1] for item in timesteps_and_source_rates]

r2s_model.timesteps = timesteps
r2s_model.source_rates = source_rates
r2s_model.photon_settings = my_photon_settings
r2s_model.photon_tallies = my_photon_tallies
# runs photon transport on every timestep,
# except the first timestep as there are no decay photons
r2s_model.photon_timesteps = [i for i in range(len(timesteps_and_source_rates))][1:]

statepoints = r2s_model.execute_run()

# these are the statepoint files produced by the photon simulations
print('photon statepoint files', [str(s) for s in statepoints])


# post processing the results and plotting


my_geometry.view_direction = "x"
plotted_part_of_tallys = []

material_ids_slice = my_geometry.get_slice_of_material_ids(pixels_across=400, view_direction='x')

# these are the material ids in the geometry
levels = np.unique([item for sublist in material_ids_slice for item in sublist])

# this loop plots the decay photon dose after each photon timestep
for photon_time_step_index in r2s_model.photon_timesteps:
    print(f'accessing photon_time_step_index {photon_time_step_index}')
    statepoint_filename=f"photon_transport/timestep_{photon_time_step_index}/statepoint.{my_photon_settings.batches}.h5"
    settings_filename=f"photon_transport/timestep_{photon_time_step_index}/settings.xml"

    with openmc.StatePoint(statepoint_filename) as statepoint:
        photon_tally_result = statepoint.get_tally(name="photon_dose_on_mesh")

    # gets the combined source strength of all the sources.
    # this is in units of Bq so it is photons emitted per second
    my_settings = openmc.Settings.from_xml(settings_filename)
    photons_per_second = sum(src.strength for src in my_settings.source)
    print('photons_per_second', photons_per_second)

    mesh = photon_tally_result.find_filter(openmc.MeshFilter).mesh

    # converts units from pSv-cm3/source_photon to pSv-cm3/second
    dose_rate = photon_tally_result.mean * photons_per_second

    # converts from (pico) pSv/second to (milli) mSv/second
    dose_rate = dose_rate * 1e-9

    tally_slice = mesh.slice_of_data(
        dataset=dose_rate,
        view_direction=my_geometry.view_direction,
        volume_normalization=True,  # converts from pSv-cm3/second to pSv/second
    )

    plt.cla()
    plt.clf()
    fig = plt.figure()

    plt.ylabel("Z [cm]")
    plt.xlabel("Y [cm]")
    days = timesteps_and_source_rates[photon_time_step_index][0] / (60 * 60 * 24)
    plt.title(
        f"Shut down dose rate with {days} day of cooldown,\n"
        f"view direction from {my_geometry.view_direction} axis, mid plane slice\n"
        f"assuming single shot of {neutrons_per_second} neutrons\n"
    )

    plot_1 = plt.imshow(
        tally_slice,
        interpolation="None",
        norm=LogNorm(
            vmin=1e12,
            vmax=1e21,
        ),
        extent=my_geometry.get_mpl_plot_extent(view_direction='x'),
    )

    cbar = plt.colorbar(plot_1)
    cbar.set_label('Photon dose [(milli) mSv/second]')

    # adds a contour of the cell geometry
    plt.contour(
        # data flipped as mpl operations imshow and contour result in different rotations
        np.flipud(np.flip(material_ids_slice)),
        origin="upper",
        colors="k",
        linestyles="solid",
        levels=levels,
        linewidths=1,
        extent=my_geometry.get_mpl_plot_extent(view_direction='x'),
    )

    plt.savefig(f"photon_flux_map_timestep_{str(photon_time_step_index).zfill(3)}.png")


import os
os.system('convert -delay 20 -loop 0 photon_flux_map_timestep_*.png  r2s.gif')