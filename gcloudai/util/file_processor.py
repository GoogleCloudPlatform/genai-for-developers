import os

def is_ascii_text(file_path):
    """
    Check if the file contains ASCII text.
    :param file_path: Path to the file
    :return: Boolean indicating whether the file contains ASCII text
    """
    try:
        with open(file_path, 'rb') as f:
            f.read().decode('ascii')
        return True
    except UnicodeDecodeError:
        return False

def get_text_files_contents(path, ignore=None):
    """
    Returns a dictionary with file paths (including file name) as keys 
    and the respective file contents as values.
    :param path: Directory path
    :param ignore: List of file or folder names to be ignored
    :return: Dictionary with file paths as keys and file contents as values
    """
    if ignore is None:
        ignore = []

    result = {}
    for dirpath, dirnames, filenames in os.walk(path):
        # Remove ignored directories from dirnames so os.walk will skip them
        dirnames[:] = [dirname for dirname in dirnames if dirname not in ignore]

        for filename in filenames:
            if filename not in ignore:
                full_path = os.path.join(dirpath, filename)
                if is_ascii_text(full_path):
                    with open(full_path, 'r', encoding='ascii') as f:
                        result[full_path] = f.read()
    return result


def format_files_as_string(input):
    def process_file(file_path):
        if not is_ascii_text(file_path):
            return f"file: {file_path}\nsource: [Binary File - Not ASCII Text]\n"

        with open(file_path, 'r') as file:
            content = file.read()
            return f"file: {file_path}\nsource:\n{content}\n"

    formatted_string = ""
    
    if isinstance(input, str):
        if os.path.isdir(input):
            for root, dirs, files in os.walk(input):
                for file in files:
                    file_path = os.path.join(root, file)
                    formatted_string += process_file(file_path)
        else:
            formatted_string += process_file(input)
    elif isinstance(input, list):
        for file_path in input:
            formatted_string += process_file(file_path)
    else:
        raise ValueError("Input must be a directory path, a single file path, or a list of file paths")

    return formatted_string
