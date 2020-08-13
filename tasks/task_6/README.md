
## <a name="task6"></a>Task 6 - Finding the tritium production

Google Colab Link: [Task_6](https://colab.research.google.com/drive/188lPNZP_3clN1kC-nlJgI4HBMaSXKu5t)

Please allow 15 minutes for this task.

Expected outputs from this task are in the [presentation](https://slides.com/openmc_workshop/neutronics_workshop/#/18).

In this task you will find the tritium breeding ratio (TBR) for a single tokamak model using the ```1_example_tritium_production.py``` script. You will then find TBR values for several tokamak models with a range of different Li6 enrichment values using the ```1_example_tritium_production_study.py``` script.

- Try opening the example scripts and understanding how the TBR is found ```coder 1_example_tritium_production.py```

- Try running the example script and finding the TBR ```python 1_example_tritium_production.py```

You should see that TBR is printed along with its associated error. As you can see the error is large.

- Try increasing the number of ```batches``` to 10 and ```sett.particles``` to 500 and re-run the simulation. You should observe an improved estimate of TBR with better statsitical uncertainty. 

- Try changing '(n,Xt)' to '205' and you should get the same result as this is the equivalent [ENDF MT reaction number](https://www.oecd-nea.org/dbdata/data/manual-endf/endf102_MT.pdf) for tritium production.

There remains uncertainty in the nuclear interaction data and elsewhere but the statisitcal uncertainty can be decreased with more computing.

Your should find that the TBR value obtained from the simulation is below 1.0 so this design will not be self sufficient in fuel.

One option for increasing the TBR is to increase the Li6 content within the blanket. Open and run the next script and see how TBR changes as the Li6 enrichment is increased.

- Try opening and understanding how the next script changes the lithium 6 enrichment```coder 2_example_tritium_production_study.py```

- Try running the example script and observing the plot produced ```python 2_example_tritium_production_study.py```

The script should produce a plot of TBR as a function of Li6 enrichment, as shown below.

<p align="center"><img src="https://user-images.githubusercontent.com/56687624/90138191-87a37900-dd6e-11ea-807d-f4560ff61ee4.png" height="500"></p>

**Learning Outcomes**

- Finding TBR with OpenMC.
- Introduction to MT reaction numbers. e.g. (n,Xt) = 205.
- Simple methods of increasing the TBR using lithium enrichment.
- Improving the uncertainty on the result is possible with more computation.