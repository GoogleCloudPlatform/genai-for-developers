# Copyright 2023 Google LLC
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
        with open(file_path, 'rb') as f:
            f.read().decode('ascii')
        return True
    except UnicodeDecodeError:
        return False


def get_text_files_contents(path, ignored_names=None):
    if not os.path.isdir(path):
        raise ValueError("Invalid directory path: {}".format(path))

    if ignored_names is None:
        ignored_names = set()
    else:
        ignored_names = set(ignored_names)  # Convert to set for faster lookups

    result = {}
    for dirpath, dirnames, filenames in os.walk(path):
        # In-place modification
        dirnames[:] = [d for d in dirnames if d not in ignored_names]

        for filename in filenames:
            if filename not in ignored_names:
                full_path = os.path.join(dirpath, filename)
                if is_ascii_text(full_path):
                    with open(full_path, 'r', encoding='ascii') as f:
                        result[full_path] = f.read()
    return result


def format_files_as_string(file_or_paths):
    def process_file(file_path):
        if not is_ascii_text(file_path):
            return ""  # Return empty string for non-ASCII files

        with open(file_path, 'r') as file:
            content = file.read()
            return f"\nfile: {file_path}\ncontent:\n{content}\n"

    formatted_string = ""

    if isinstance(file_or_paths, str):
        # Handle single file or directory path
        if os.path.isdir(file_or_paths):
            # Recursively process files in the directory
            for root, _, files in os.walk(file_or_paths):
                for file in files:
                    file_path = os.path.join(root, file)
                    formatted_string += process_file(file_path)
        else:
            # Process single file
            formatted_string += process_file(file_or_paths)
    elif isinstance(file_or_paths, list):
        # Process list of file paths
        for file_path in file_or_paths:
            formatted_string += process_file(file_path)
    else:
        raise ValueError(
            "Input must be a directory path, a single file path, or a list of file paths")

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