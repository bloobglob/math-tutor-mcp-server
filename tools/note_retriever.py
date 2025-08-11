import os

def retrieve(grade: str, section: str) -> str:
    """
    Retrieve notes from a specific section.

    Args:
        grade (str): The grade level of the notes. Ex: 7th or 8th.
        section (str): The section to retrieve notes from. Ex: 1.1, 4.3, etc.

    Returns:
        str: The retrieved notes.
    """
    # Parse module and section from input (e.g., "1.1" -> module1, section1.1.txt)
    module_num = section.split('.')[0]
    module_folder = f"module{module_num}"
    section_file = f"section{section}.txt"
    file_path = os.path.join("data", grade, module_folder, section_file)

    print(os.getcwd(), file_path)

    # Check if the file exists
    if not os.path.isfile(file_path):
        return f"Notes for section {section} not found."

    # Read and return the content of the file
    with open(file_path, 'r') as file:
        return file.read()
    
def get_sections(grade: str) -> str:
    """
    Get all section identifiers and their titles for a specific grade.
    
    Args:
        grade (str): The grade level to retrieve sections for. Ex: 7th or 8th.

    Returns:
        str: A string with each section_id and title on a new line.
    """
    sections = []
    base_path = os.path.join('data', grade)
    # Loop through all module folders
    for module in os.listdir(base_path):
        module_path = os.path.join(base_path, module)
        if os.path.isdir(module_path):
            # Loop through all section files
            for filename in os.listdir(module_path):
                if filename.startswith('section') and filename.endswith('.txt'):
                    section_id = filename.replace('section', '').replace('.txt', '')
                    file_path = os.path.join(module_path, filename)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            first_line = f.readline().strip().split(': ')[1]
                            sections.append((section_id, first_line))
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
    sections = sorted(sections, key=lambda x: x[0])
    return "\n".join([f"{id}: {title}" for id, title in sections])

if __name__ == "__main__":
    print(get_sections("8th"))