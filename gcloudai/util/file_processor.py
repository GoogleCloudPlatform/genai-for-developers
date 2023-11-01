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

def get_text_files_contents(path):
    """
    Returns a dictionary with file paths (including file name) as keys 
    and the respective file contents as values.
    :param path: Directory path
    :return: Dictionary with file paths as keys and file contents as values
    """
    result = {}
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            if is_ascii_text(full_path):
                with open(full_path, 'r', encoding='ascii') as f:
                    result[full_path] = f.read()
    return result