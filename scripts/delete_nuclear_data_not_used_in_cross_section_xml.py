
""" This script deletes corss section .h5 files that are not used in the
cross_sections.xml file. This reduces the amount of memory the docker image
requires"""

import os
import xml.etree.ElementTree as ET
from pathlib import Path

# Get environment variable that points to the cross_section.xml file
cross_section_xml_path = os.getenv('OPENMC_CROSS_SECTIONS')

cs_xml_folder = Path(cross_section_xml_path).parent

tree = ET.parse(cross_section_xml_path)


root = tree.getroot()

nuc_data_in_xml = []

folders_with_nuc_data_in = []

for child in root:
     
    # Keeps track of the all files in the cross_Section.xml
    nuc_data_in_xml.append(str(Path(cs_xml_folder) / child.attrib['path']))

    # Keeps track of the all base folders in the cross_Section.xml
    folder_from_cs_xml = str(Path(child.attrib['path']).parent)
    folders_with_nuc_data_in.append(str(Path(cs_xml_folder) / folder_from_cs_xml))

# the unique folders containing h5 files mentioned in the cross_sections.xml file
folders_to_check = set(folders_with_nuc_data_in)

# searches the nuclear data containing folders for h5 files
nuc_data_in_folders = []
for folder in folders_to_check:
    print(folder)
    folder_with_prefix = Path(cs_xml_folder) / Path(folder)
    for nuc_data_file in list(folder_with_prefix.rglob('*.h5')):
        nuc_data_in_folders.append(str(Path(cs_xml_folder) / nuc_data_file))


print(len(nuc_data_in_folders), 'nuclear data files in folders')
print(len(nuc_data_in_xml), 'nuclear data files in cross_sections.xml')

# deletes h5 files found in folders that are not mentioned in th cross_sections.xml file
nuc_data_to_delete = []
mb_saved = 0
for nuc_data in nuc_data_in_folders:
    if nuc_data not in nuc_data_in_xml:
        nuc_data_to_delete.append(nuc_data)
        mb_saved += Path(nuc_data).stat().st_size
        os.system('rm ' + nuc_data)
        print('deleting ' + nuc_data)
print(len(nuc_data_to_delete), 'nuclear data files deleted')

print(round(mb_saved / (1024 * 1024), 3), 'MB saved')
