
## <a name="task5"></a>Task 5 - Finding the neutron and photon spectra

Google Colab Link: [Task_5](https://colab.research.google.com/drive/1piuEmG09E9kfkFTw2WZV6TdX_xovqmVj)

Please allow 15 minutes for this task.

Expected outputs from this task are in the [presentation](https://slides.com/openmc_workshop/neutronics_workshop/#/17).

In this task the neutron spectra at two different locations will be measured and visualized. OpenMC has several energy group structures such as CCFE-709 and [others](https://github.com/openmc-dev/openmc/blob/develop/openmc/mgxs/__init__.py) built in which makes the energy grid easy to define.

- Try opening the ```1_example_neutron_spectra.py``` script to see how the neutron spectra is obtained for the breeder blanket cell.

- Try running the example script which plot the neutron spectra within the breeder blanket. ```python 1_example_neutron_spectra.py```, the plot should look similar to the plot shown below.

<p align="center"><img src="images/1_example_neutron_spectra.png" height="500"></p>

- Look for the Maxwell distribution of energys in the thermal energy range. This is where neutrons are in thermodynamic equilibrium with the material they are moving through. 

- Currently the neutron flux spectra is being found for the blanket cell / volume. Try Changing this to the neutron current spectra on the back surface of the model. The code is contained in the scripts but needs uncommenting. Why do the two spectra differ and why has the standard deviation on the results increased so much?

The task now starts to look at secondary photons created from neutron interactions. These photons are often created in neutron scattering interactions where the nucleus is left excited and de-excites via photon production. To run OpenMC in coupled neutron, photon mode an additional setting is required to enable photon transport (which is disabled by default).

- Try opening the example script ```coder 2_example_photon_spectra.py``` script to see how the photon spectra is obtained for the breeder blanket cell and photon transport is enabled.

- Try running the script to plot the photon spectra within the breeder blanket. ```python 2_example_photon_spectra.py```. The output should look similar to the plot shown below.

Why do you think the photons generated are of lower energy?

<p align="center"><img src="images/2_example_photon_spectra.png" height="500"></p>

**Learning Outcomes**

- Plotting neutron / photon spectra for cells and surfaces and observing the changing neutron energy at different locations in the reactor.
- Performing coupled neutron photon simulations where photons are created from neutron interactions.