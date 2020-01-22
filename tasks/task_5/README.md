
## <a name="task5"></a>Task 5 - Finding the neutron and photon spectra

Google Colab Link: [Task_5](https://colab.research.google.com/drive/1piuEmG09E9kfkFTw2WZV6TdX_xovqmVj)

Please allow 15 minutes for this task.

Expected outputs from this task are in the [presentation](https://slides.com/openmc_workshop/neutronics_workshop/#/17).

In this task the neutron spectra at two different locations will be measured and visualized. OpenMC has several energy group structures such as VITAMIN-J-175 and [others](https://github.com/openmc-dev/openmc/blob/develop/openmc/mgxs/__init__.py) built in which makes the energy grid easy to define.

- Try opening the ```1_example_neutron_spectra_tokamak.py``` script to see how the neutron spectra is obtained for the breeder blanket cell.

- Try running the example script which plot the neutron spectra within the breeder blanket. ```python 1_example_neutron_spectra_tokamak.py```, the plot should look similar to the plot shown below.

<p align="center"><img src="tasks/task_5/images/1_example_neutron_spectra_tokamak.png" height="500"></p>

- Try adding the neutron spectra within the first wall cell to the same plot and compare it to the breeder blanket cell. Why might they be different?

The task now starts to look at secondary photons created from neutron interactions. These photons are often created in neutron scattering interactions where the nucleus is left excited and de-excites via photon production. To run OpenMC in coupled neutron, photon mode an additional setting is required to enable photon transport (which is disabled by default).

- Try opening the example script ```coder 2_example_photon_spectra_tokamak.py``` script to see how the photon spectra is obtained for the breeder blanket cell and photon transport is enabled.

- Try running the script to plot the photon spectra within the breeder blanket. ```python 2_example_photon_spectra_tokamak.py```. The output should look similar to the plot shown below.

Why do you think the photons generated are of lower energy?

<p align="center"><img src="tasks/task_5/images/2_example_photon_spectra_tokamak.png" height="500"></p>

**Learning Outcomes**

- Plotting neutron / photon spectra and observing the changing neutron energy at different locations in the reactor.
- Performing coupled neutron photon simulations where photons are created from neutron interactions.