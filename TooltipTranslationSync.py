import re
import os

# Functions used in the code
def extract_info(line):
    contentuid_match = re.search(r'contentuid="([^"]+)"', line)
    tooltip_match = re.search(r'Tooltip="([^"]+)"', line)
    contentuid = contentuid_match.group(1) if contentuid_match else None
    tooltip = tooltip_match.group(1) if tooltip_match else None
    return contentuid, tooltip

def is_korean(text):
    if text is None:
        return False
    return any('\uac00' <= char <= '\ud7a3' for char in text)

def replace_tooltip_line(original_line, new_tooltip):
    return re.sub(r'(Tooltip=")[^"]+(")', r'\1' + new_tooltip + r'\2', original_line)

def update_file_with_correct_tooltip(spells_lines, spells_bak_lines, lines_to_replace):
    updated_lines = spells_lines[:]
    for line in spells_bak_lines:
        contentuid, tooltip = extract_info(line)
        if contentuid in lines_to_replace:
            for i, original_line in enumerate(spells_lines):
                if contentuid in original_line:
                    updated_lines[i] = replace_tooltip_line(original_line, tooltip)
                    break
    return updated_lines

# Main function to process the files
def process_files(original_file_path, backup_file_path):
    with open(original_file_path, 'r', encoding='utf-8') as file:
        spells_lines = file.readlines()

    lines_to_replace = {}
    for line in spells_lines:
        contentuid, tooltip = extract_info(line)
        if contentuid and is_korean(tooltip):
            lines_to_replace[contentuid] = line.strip()

    with open(backup_file_path, 'r', encoding='utf-8') as file:
        spells_bak_lines = file.readlines()

    updated_spells_lines = update_file_with_correct_tooltip(spells_lines, spells_bak_lines, lines_to_replace)

    updated_file_path = original_file_path.replace('.xml', '.xml')
    with open(updated_file_path, 'w', encoding='utf-8') as file:
        file.writelines(updated_spells_lines)
    
    return updated_file_path

# Find all xml files in the same directory as the script
script_directory = os.path.dirname(os.path.realpath(__file__))
xml_files = [file for file in os.listdir(script_directory) if file.endswith('.xml') and not file.endswith('_bak.xml')]

# Process each xml file if its corresponding _bak.xml file exists
for file_name in xml_files:
    original_file_path = os.path.join(script_directory, file_name)
    backup_file_name = file_name.replace('.xml', '_bak.xml')
    backup_file_path = os.path.join(script_directory, backup_file_name)

    if os.path.exists(backup_file_path):
        try:
            updated_file = process_files(original_file_path, backup_file_path)
            print(f"Updated file saved to: {updated_file}")
        except Exception as e:
            print(f"An error occurred while processing {file_name}: {e}")
    else:
        print(f"{file_name} does not have a corresponding backup file.")
input("Press any key to exit...")
