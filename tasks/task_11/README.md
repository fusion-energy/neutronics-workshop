
## <a name="task10"></a>Task 11 - Options for making materials

Google Colab Link: [Task_11](https://colab.research.google.com/drive/1pY3dcsHu7nC3Mv3WmqUWLSCzr0gaeuvE)

Please allow XXX minutes for this task.

Expected outputs from this task are in the [presentation](insert link for specific slides)

Constructing materials is a fundamental part of creating neutronics models to perform simulations. In the previous tasks, material creation has been touched on, however, this task aims to demonstrate neutronics material creation in more depth.

There are several ways to create materials. OpenMC itself can be used, however, external modules can also be used. In particularly, we will look at the neutronics_material_maker. (Link to GitHub). This is an open source code which aims to simplify material creation for use in neutronics models.

First, we will look at how materials can be created in OpenMC. OpenMC offers the ability to create materials from elements or isotopes, where elements are assumed to be the combination of all naturally occurring isotopes at natural abundance. Isotopes are required in some circumstances where we want a specific isotope rather than the element, or we need to deal with something like enrichment in a material.
Materials can be formed by a combination of isotopes and elements

- Creating Materials from isotopes

Here, we will create some materials purely using isotopes. As mentioned, this may be required to ge a specific material composition but also allows material enrichments to be changed.

Take a look at the script below.

```1_example_materials_from_isotopes.py```

This script shows how to create two materials from isotopes.

Look through the script and try to understand how this is done.

Running the script shows that neutronics materials have been made and their parameters.

~~~~~
Don't know whether to add an explanation of the process here? Something like this -

First, the openmc.Material class is instantiated with a name.
We then add our isotopes to the material with a percentage type. 'wo' or 'ao'.
We can then set the material density.
We are creating a natural material, meaning because we are using isotopes, we have to include all of the natural isotopes and weight them by their natural abundance.
For this, we are using the NATURAL_ABUNDANCE dictionary as part of openmc.data to obtain the natural abundances of each isotope.
~~~~~

Try adding another material made out of isotopes.

Making materials out of isotopes is inefficient and should be reserved for when required. For example, when a material has a particular composition or enrichment.
However, materials can also be constructed from elements.


- Creating Materials from elements

Materials can also be created from elements. In OpenMC, an element is a combination of all naturally occuring isotopes of an element, removing the need to specify each individual isotope of a material.
However, isotopes in elements are weighted by their natural abundance meaning are only suitable when 'natural' materials are required. I.e. would be unsuitable to create enriched materials.

Look at the script below.

```2_example_materials_from_elements.py```

See how specifying the materials from elements greatly reduces the number of lines of code required to make the material.

Materials can also be constructed from a combination of isotopes and elements. This combines the flexibility of using isotopes (such that enriched/specific materials can be created) with the efficiency of using elements.
For example, Li4SiO4, we are only really bothered about its lithium composition, meaning we can specify Si and O as elements, and only deal with the Li with isotopes.
Take a look at the script to see this.
Also get some printout of things

Try adding another material made from elements (or a combination of isotopes and elements)

Constructing materials this way is still quite inefficient and difficult as parameters are difficult to account for - e.g. enrichment/packing/temperature/pressure. Luckily, a tool exist called the neutronics_material_maker which simplifies this process.


- Creating Materials using neutronics_material_maker

Description of the neutronics_material_maker
Usage etc.

```3_example_materials_from_material_maker.py```

Should get some graph outputs


- Creating Materials using mix_materials function

Description of using mix_materials function

```4_example_materials_from_mix_materials.py```

