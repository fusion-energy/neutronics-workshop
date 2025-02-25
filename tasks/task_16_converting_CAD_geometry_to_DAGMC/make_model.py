from cad_to_dagmc import CadToDagmc
import cadquery as cq

text = cq.Workplane().text(txt="OpenMC", fontsize=10, distance=1)

text.export("step_cad_file_for_conversion.step")