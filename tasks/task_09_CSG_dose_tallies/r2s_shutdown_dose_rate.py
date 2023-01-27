# makes a sphere of Silver and irradiates it with a 14MeV neutron source.
# The activated material emits gammas and these are transported and tallied
# on a mesh tally. The resulting decay gamma flux is plotted as a series of
# images so that the variation over time can be observed. Note that silver
# activation results in Ag110 which has a half life of 24 seconds. The
# irradiation and decay timescales are set so that the buildup and decay can be
# observed
from pathlib import Path
import openmc
import typing


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
    timesteps : iterable of times, units
        Blah
    source_rates : iterable of float
        more blah
    depletion_options : dict
        dictionary with model.deplete kwargs
    photon_timesteps : iterable of int
        which depletion steps to do photon transport for
    photon_settings : Settings object
    photon_tallies : Tallies object
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
        matlist = [results.export_to_materials(i, path=self.depletion_path)
                   for i in range(len(self.timesteps))]

        # Set up photon calculation
        self.settings = self.photon_settings
        self.settings.photon_transport = True
        self.tallies = self.photon_tallies

        statepoint_paths = []
        # Run photon transport for each desired timestep
        for tidx in self.photon_timesteps:
            new_mats = matlist[tidx]
            rundir = self.ptransport_path / f'timestep_{tidx}'

            # Create Source for every depleted region
            src_list = []
            for cell in self.geometry.get_all_cells().values():
                if cell.fill is None:
                    continue
                src = openmc.Source.from_cell_with_material(cell)
                src_list.append(src)

            self.settings.source = src_list
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
                "The openmc.Material object used must have the volume "
                "property set"
            )
            raise ValueError(msg)

        photon_spec = material.decay_photon_energy

        if photon_spec is None:
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

sphere_surf_1 = openmc.Sphere(r=20, boundary_type="vacuum")
sphere_surf_2 = openmc.Sphere(r=5, x0=10)

sphere_region_1 = -sphere_surf_1 & +sphere_surf_2  # void space
sphere_region_2 = -sphere_surf_2

sphere_cell_1 = openmc.Cell(region=sphere_region_1)

sphere_cell_2 = openmc.Cell(region=sphere_region_2)

mat_silver = openmc.Material()
mat_silver.add_element("Ag", 1.0)
mat_silver.set_density("g/cm3", 10.49)
mat_silver.depletable = True
mat_silver.volume = 523.6
sphere_cell_2.fill = mat_silver

universe = openmc.Universe(cells=[sphere_cell_1, sphere_cell_2])
my_geometry = openmc.Geometry(universe)

my_materials = openmc.Materials([mat_silver])

my_neutron_settings = openmc.Settings()
my_neutron_settings.batches = 10
my_neutron_settings.particles = 500000
my_neutron_settings.run_mode = "fixed source"

source = openmc.Source()
source.space = openmc.stats.Point((0, 0, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])
my_neutron_settings.source = source

my_photon_settings = openmc.Settings()
my_photon_settings.batches = 10
my_photon_settings.particles = 50000
my_photon_settings.run_mode = "fixed source"

# Create mesh which will be used for tally
mesh = openmc.RegularMesh().from_domain(
    my_geometry,  # the corners of the mesh are being set automatically to surround the geometry
    dimension=[200, 200, 1],
)

mesh_filter = openmc.MeshFilter(mesh)

my_photon_tallies = openmc.Tallies()
# Create mesh filter for tally

# Create flux mesh tally to score flux
mesh_tally_1 = openmc.Tally(name="photon_flux_on_mesh")
particle_filter = openmc.ParticleFilter(['photon'])
mesh_tally_1.filters = [mesh_filter, particle_filter]
mesh_tally_1.scores = ["flux"]
my_photon_tallies.append(mesh_tally_1)

r2s_model = openmc.R2SModel(
    geometry=my_geometry,
    materials=my_materials,
    settings=my_neutron_settings,
)

r2s_model.timesteps = [200] * 100  # neutron irradiation timesteps
r2s_model.source_rates = [1e18] * 20 + [0] * 80  # 6 full power and 6 zero power neutron irradiation source rates
r2s_model.photon_settings = my_photon_settings
r2s_model.photon_tallies = my_photon_tallies
# runs photon transport on every timestep but could change to  after [6, 7, 8, 9, 10, 11] which would be ever step after the neutron source goes to 0
r2s_model.photon_timesteps = list(range(100))


statepoints = r2s_model.execute_run()
print([str(s) for s in statepoints])

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np

plotted_part_of_tallys=[]

for i, statepoint_file in enumerate(statepoints):
    with openmc.StatePoint(statepoint_file) as statepoint:
        my_tally = statepoint.get_tally(name="photon_flux_on_mesh")
        plotted_part_of_tally = my_tally.mean.flatten()
        print(sum(plotted_part_of_tally))
        plotted_part_of_tallys.append(plotted_part_of_tally)
        reshaped_tally = plotted_part_of_tally.reshape(mesh.dimension, order="F")
        tally_aligned = reshaped_tally.transpose(2, 0, 1) # specific transpose for slicing z axis
        image_slice = tally_aligned[int(mesh.dimension[2] / 2)] # mid mesh slice
        left = mesh.lower_left[2]  # 2 as z axis slice
        right = mesh.upper_right[2]
        bottom = mesh.lower_left[2]
        top = mesh.upper_right[2]
        norm = LogNorm(vmin=1e-4, vmax=1e1)
        mpl_image_slice = np.rot90(image_slice)
        plt.cla()
        plt.clf()
        plt.axes(title=f"Photon Flux from Activated Ag, timestep {i} = {sum(r2s_model.timesteps[:i])}s", xlabel='X [cm]', ylabel='y [cm]')
        plt.imshow(X=mpl_image_slice, extent=(left, right, bottom, top), norm=norm)
        plt.contour(mpl_image_slice, levels=[1e1])
        plt.colorbar(label='flux')
        plt.savefig(f'photon_flux_map{str(i).zfill(3)}.png')

plt.cla()
plt.clf()
plt.plot(plotted_part_of_tallys)
plt.savefig(f'flux_vs_time.png')
import os
os.system('convert -delay 20 -loop 0 photon_*.png  r2s.gif')
