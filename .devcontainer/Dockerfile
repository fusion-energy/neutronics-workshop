# This Dockerfile adds the workshop files to the base dockerfile to make a
# complete neutronics-workshop docker image

# This Dockerfile can be build locally or a prebuild image can be downloaded

# To download the prebuild image
# docker pull ghcr.io/fusion-energy/neutronics-workshop

# To build this Dockerfile into a docker image:
# docker build -t neutronics-workshop -f .devcontainer/Dockerfile .

# then run with this command
# docker run -p 8888:8888 neutronics-workshop

# remote image
FROM ghcr.io/fusion-energy/neutronics-workshop:base as base
# local image
# FROM neutronics-workshop:base as base

# Copy over the local repository files
COPY tasks tasks/
COPY tests tests/


RUN mkdir tasks/half-day-workshop
RUN cp tasks/task_01_cross_sections/1_isotope_xs_plot.ipynb tasks/half-day-workshop/task_01_isotope_xs_plot.ipynb
RUN cp tasks/task_01_cross_sections/2_element_xs_plot.ipynb tasks/half-day-workshop/task_02_element_xs_plot.ipynb
RUN cp tasks/task_01_cross_sections/3_material_xs_plot.ipynb tasks/half-day-workshop/task_03_material_xs_plot.ipynb
RUN cp tasks/task_02_making_materials/1_example_materials_from_isotopes.ipynb tasks/half-day-workshop/task_04_example_materials_from_isotopes.ipynb
RUN cp tasks/task_02_making_materials/2_example_materials_from_elements.ipynb tasks/half-day-workshop/task_05_example_materials_from_elements.ipynb
RUN cp tasks/task_03_making_CSG_geometry/1_simple_csg_geometry.ipynb tasks/half-day-workshop/task_06_simple_csg_geometry.ipynb
RUN cp tasks/task_04_make_sources/1_point_source_plots.ipynb tasks/half-day-workshop/task_07_point_source_plots.ipynb
RUN cp tasks/task_04_make_sources/2_ring_source.ipynb tasks/half-day-workshop/task_08_ring_source.ipynb
RUN cp tasks/task_04_make_sources/3_plasma_source_plots.ipynb tasks/half-day-workshop/task_09_plasma_source_plots.ipynb
RUN cp tasks/task_05_CSG_cell_tally_TBR/1_example_tritium_production.ipynb tasks/half-day-workshop/task_10_example_tritium_production.ipynb
RUN cp tasks/task_06_CSG_cell_tally_DPA/1_find_dpa.ipynb tasks/half-day-workshop/task_11_find_dpa.ipynb
RUN cp tasks/task_07_CSG_cell_tally_spectra/2_example_neutron_spectra_on_cell.ipynb tasks/half-day-workshop/task_12_example_neutron_spectra_on_cell.ipynb
RUN cp tasks/task_07_CSG_cell_tally_spectra/4_example_photon_spectra.ipynb tasks/half-day-workshop/task_13_example_photon_spectra.ipynb
RUN cp tasks/task_08_CSG_mesh_tally/1_example_2d_regular_mesh_tallies.ipynb tasks/half-day-workshop/task_14_example_2d_regular_mesh_tallies.ipynb
RUN cp tasks/task_10_activation_transmutation_depletion/3_full_pulse_schedule.ipynb tasks/half-day-workshop/task_15_full_pulse_schedule.ipynb
RUN cp tasks/task_19_design_task/1_optimal_design.ipynb tasks/half-day-workshop/task_16_optimal_design.ipynb 
RUN cp tasks/task_19_design_task/1_optimal_design_with_hints.ipynb tasks/half-day-workshop/task_16_optimal_designs_with_hints.ipynb 

WORKDIR /tasks

# this sets the port, gcr looks for this varible
FROM base as jupyter_cmd

ENV PORT 8888

# could switch to --ip='*'
CMD ["jupyter", "lab", "--notebook-dir=/tasks", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]
