# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import subprocess

def is_ascii_text(file_path):
    """
    Check if the file contains ASCII text.
    :param file_path: Path to the file
    :return: Boolean indicating whether the file contains ASCII text
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read()
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
        ignore = set(['venv', '__pycache__', '.gitignore'])

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
            # pass

        with open(file_path, 'r') as file:
            content = file.read()
            return f"\nfile: {file_path}\ncontent:\n{content}\n"
            # return f"{content}\n\n"

    formatted_string = ""

    exclude_directories = set(['venv', '__pycache__', '.gitignore']) 

    if isinstance(input, str):
        if os.path.isdir(input):
            
            for root, dirs, files in os.walk(input):
                dirs[:] = [d for d in dirs if d not in exclude_directories]
                files[:] = [f for f in files if f not in exclude_directories]
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        formatted_string += process_file(file_path)
        else:
            if os.path.exists(input):
                formatted_string += process_file(input)
    elif isinstance(input, list):
        for file_path in input:
            if os.path.exists(file_path):
                formatted_string += process_file(file_path)
    else:
        raise ValueError("Input must be a directory path, a single file path, or a list of file paths")

    return formatted_string

def list_files(start_sha, end_sha, refer_commit_parent=False):

    if refer_commit_parent:
        start_sha = f"{start_sha}^"
        
    command = ["git", "diff", "--name-only", start_sha, end_sha]

    return run_git_command(command)

def list_changes(start_sha, end_sha, refer_commit_parent=False):
    if refer_commit_parent:
        start_sha = f"{start_sha}^"

    command = ["git", "diff", start_sha, end_sha]
    output = subprocess.check_output(command, text=True)
    return output

def list_commit_messages(start_sha, end_sha, refer_commit_parent=False):
    
    command = ["git", "log", "--pretty=format:%s", "--name-only", start_sha, end_sha]
    if refer_commit_parent:
        command = ["git", "log", "--pretty=format:%s", "--name-only", f"{start_sha}^..{end_sha}"]

    output = subprocess.check_output(command, text=True)
    return output

def list_commits_for_branches(branch_a, branch_b):
    command = ["git", "log", "--pretty=format:%h", f"{branch_a}..{branch_b}"]
    return run_git_command(command)

def list_commits_for_tags(tag_a, tag_b):
    command = ["git", "log", "--pretty=format:%h", tag_a, tag_b]
    return run_git_command(command)

def list_tags():
    command = ["git", "tag"]
    return run_git_command(command)

def run_git_command(command):
    output = subprocess.check_output(command).decode("utf-8").strip()
    records = output.splitlines()

    list = []
    for record in records:
        list.append(record)

    return list