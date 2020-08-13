
## <a name="task7"></a>Task 7 - Finding the neutron damage and stochastic volume calculation

Google Colab Link: [Task_7](https://colab.research.google.com/drive/1wH1Y4I2UHewk2BS6DQpkMGBuLHwtGg6B)

Please allow 15 minutes for this task.

Expected outputs from this task are in the [presentation](https://slides.com/openmc_workshop/neutronics_workshop/#/19).

Displacements per atom (DPA) is one measure of damage within materials exposed to neutron irradiation. Damage energy can be tallied in OpenMC with MT reaction number 444 and DPA can be estimated.

In the case of DPA a neutronics code alone can't fully calculate the value as material science techniques are needed to account for the material and recombination effects. For example after a displacement there is a chance that the atom relocates to it's original latic position (recombination) and different atoms require different amounts of energy to [displace](https://fispact.ukaea.uk/wiki/Output_interpretation#DPA_and_KERMA). The DPA tally from neutronics is therefore only an estimate of the DPA.

The MT 444 / damage energy tally is in units of eV per source particle. Therefore the result needs scaling by the source intensity (in neutrons per second) and the irradiation duration (in seconds) and the number of atoms in the volume.


- Try to understand the post proccessing steps involved in converting a neutronics damage tally into displacements by reading the relevant section at the end of the example script ```coder 1_find_dpa.py```

- Find the total number of displacements in the firstwall by running the example script ```python 1_find_dpa.py```. This script assume a threshold displacement energy of 40eV is required and that 20% of the displaced atoms recombine.

- Open the example script and see how a stochastic volume calculation can be performed using OpenMC ```coder 2_find_cell_volume.py```

- Find the volume and number of iron atoms in the firstwall using the python script ```python 2_find_cell_volume.py```

- Calculate the displacements per atoms for a full power year by using the outputs of both scripts

- Using this information find the DPA on the first wall for the 3GW (fusion energy) reactor over a 5 year period. Does this exceed the Eurofer DPA limit of 70 DPA? If so what could be changed about the design to ensure this limit is now reached?

**Learning Outcomes**

- Finding damage energy deposited with the OpenMC MT 444 tally
- Find the volume of a cell using the stochastic volume method
- Perform post tally calculations to convert the neutronics numbers into something more useful
- Gain an appreciation of how neutronics results can influence the design (e.g. radius of reactor must be increased to prevent critical material damage)

**Next task:** [Task 8 - Survey breeder blanket designs for tritium production - 25 minutes](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_8)