
## <a name="task10"></a>Task 11 - Options for making materials

Google Colab Link: [Task_11](insert Link here)

Please allow XXXX minutes for this task.

Expected outputs from this task are in the [presentation](insert link for specific slides)

Constructing materials is a fundamental part of creating neutronics models to perform simulations. In the previous tasks, material creation has been touched on, however, this task aims to demonstrate neutronics material creation in more depth.

There are several ways to create materials. OpenMC itself can be used, however, external modules can also be used. In particularly, we will look at the neutronics_material_maker. (Link to GitHub). This is an open source code which aims to simplify material creation for use in neutronics models.

First, we will look at how materials can be created in OpenMC. OpenMC offers the ability to create materials from elements or isotopes, where elements are assumed to be the combination of all naturally occurring isotopes at natural abundance. Isotopes are required in some circumstances where we want a specific isotope rather than the element, or we need to deal with something like enrichment in a material.
Materials can be formed by a combination of isotopes and elements

- Creating Materials from isotopes

Here, we will create some materials purely using isotopes. As mentioned, this may be required to ge a specific material composition but also allows material enrichments to be changed.

Take a look at the script below.

(Insert first example script)

This script shows how to create two materials using only isotopes - water and Lithium Orthosilicate.

First, the openmc.Material class is instantiated with a name.
We then add our isotopes to the material with a percentage type. 'wo' or 'ao'.
We can then set the material density.
We are creating a natural material, meaning because we are using isotopes, we have to include all of the natural isotopes and weight them by their natural abundance.
For this, we are using the NATURAL_ABUNDANCE dictionary as part of openmc.data to obtain the natural abundances of each isotope.

Using isotopes to create natural materials requires a number of lines of code because each isotope must be added individually.
Therefore, this method is not the most efficient for creating materials with isotopes at natural abundances.
Where the use of isotopes is needed is when we need to specify specific material compositions that are not equivalent to natural.
or we have to deal with things like material enrichments.