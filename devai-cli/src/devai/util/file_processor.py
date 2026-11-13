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

MAX_FILE_SIZE = 1_000_000  # 1MB per file limit
MAX_DIRECTORY_DEPTH = 10   # Max directory recursion depth
MAX_TOTAL_CHARS = 10_000_000  # 10MB total output limit

DEFAULT_EXCLUDE_DIRECTORIES = {
    'venv', '.venv', '__pycache__', '.git', '.github', '.gitlab',
    '.idea', '.vscode', 'node_modules', '.gitignore'
}

SENSITIVE_FILE_NAMES = {
    '.gitignore', '.npmrc', '.pypirc', '.htpasswd', '.netrc',
    'credentials.json', 'client_secrets.json'
}

SENSITIVE_EXTENSIONS = (
    '.pem', '.key', '.pfx', '.p12', '.pkcs12', '.kdbx', '.keystore'
)

SENSITIVE_NAME_PATTERNS = (
    'id_rsa', 'id_ed25519', 'id_ecdsa', 'service-account', 'client_secret'
)


def is_secret_or_sensitive(file_path):
    """
    Check if a file is sensitive or secret.
    :param file_path: Path to the file
    :return: Boolean indicating whether the file is considered sensitive
    """
    basename = os.path.basename(file_path).lower()
    if basename.startswith('.env'):
        return True
    if basename in SENSITIVE_FILE_NAMES:
        return True
    if basename.endswith(SENSITIVE_EXTENSIONS):
        return True
    if any(pat in basename for pat in SENSITIVE_NAME_PATTERNS):
        return True
    return False


def is_ascii_text(file_path):
    """
    Check if the file contains ASCII/UTF-8 text safely within size limits.
    :param file_path: Path to the file
    :return: Boolean indicating whether the file contains ASCII/UTF-8 text
    """
    if os.path.islink(file_path):
        return False
    try:
        if os.path.getsize(file_path) > MAX_FILE_SIZE:
            return False
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(8192)
        return True
    except (UnicodeDecodeError, OSError):
        return False


def get_text_files_contents(path, ignore=None):
    """
    Returns a dictionary with file paths (including file name) as keys 
    and the respective file contents as values.
    :param path: Directory path
    :param ignore: List or set of file or folder names to be ignored
    :return: Dictionary with file paths as keys and file contents as values
    """
    if ignore is None:
        ignore = DEFAULT_EXCLUDE_DIRECTORIES
    else:
        ignore = set(ignore)

    result = {}
    base_real_path = os.path.realpath(path)
    visited_dirs = set()

    for dirpath, dirnames, filenames in os.walk(path):
        # Prevent symlink directory loops and unbounded recursion depth
        real_dirpath = os.path.realpath(dirpath)
        if real_dirpath in visited_dirs:
            dirnames[:] = []
            continue
        visited_dirs.add(real_dirpath)

        depth = len(os.path.relpath(dirpath, path).split(os.sep))
        if depth > MAX_DIRECTORY_DEPTH:
            dirnames[:] = []
            continue

        # Remove ignored directories from dirnames so os.walk will skip them
        dirnames[:] = [
            dirname for dirname in dirnames
            if dirname not in ignore and not os.path.islink(os.path.join(dirpath, dirname))
        ]

        for filename in filenames:
            if filename not in ignore:
                full_path = os.path.join(dirpath, filename)
                # Skip symlinks and sensitive files
                if os.path.islink(full_path):
                    continue
                if is_secret_or_sensitive(full_path):
                    continue
                try:
                    real_file = os.path.realpath(full_path)
                    if not real_file.startswith(base_real_path):
                        continue
                    if os.path.getsize(full_path) > MAX_FILE_SIZE:
                        continue
                    if is_ascii_text(full_path):
                        with open(full_path, 'r', encoding='utf-8') as f:
                            result[full_path] = f.read(MAX_FILE_SIZE)
                except OSError:
                    continue
    return result


def format_files_as_string(input):
    def process_file(file_path, base_path=None):
        if os.path.islink(file_path):
            return f"file: {file_path}\nsource: [Skipped - Symbolic Link]\n"

        if is_secret_or_sensitive(file_path):
            return f"file: {file_path}\nsource: [Skipped - Sensitive File]\n"

        if base_path:
            try:
                real_file = os.path.realpath(file_path)
                real_base = os.path.realpath(base_path)
                if not real_file.startswith(real_base):
                    return f"file: {file_path}\nsource: [Skipped - Path Outside Base Directory]\n"
            except OSError:
                return f"file: {file_path}\nsource: [Skipped - Invalid File Path]\n"

        try:
            if os.path.getsize(file_path) > MAX_FILE_SIZE:
                return f"file: {file_path}\nsource: [Skipped - Exceeds Maximum Size Limit]\n"
        except OSError:
            return f"file: {file_path}\nsource: [Skipped - Inaccessible File]\n"

        if not is_ascii_text(file_path):
            return f"file: {file_path}\nsource: [Binary File - Not ASCII Text]\n"

        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                content = file.read(MAX_FILE_SIZE)
                return f"\nfile: {file_path}\ncontent:\n{content}\n"
        except OSError:
            return f"file: {file_path}\nsource: [Skipped - Read Error]\n"

    formatted_string = ""
    exclude_directories = DEFAULT_EXCLUDE_DIRECTORIES

    if isinstance(input, str):
        if os.path.isdir(input):
            base_real_path = os.path.realpath(input)
            visited_dirs = set()
            for root, dirs, files in os.walk(input):
                real_root = os.path.realpath(root)
                if real_root in visited_dirs:
                    dirs[:] = []
                    continue
                visited_dirs.add(real_root)

                depth = len(os.path.relpath(root, input).split(os.sep))
                if depth > MAX_DIRECTORY_DEPTH:
                    dirs[:] = []
                    continue

                dirs[:] = [
                    d for d in dirs
                    if d not in exclude_directories and not os.path.islink(os.path.join(root, d))
                ]
                files[:] = [f for f in files if f not in exclude_directories]
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        formatted_string += process_file(file_path, base_path=input)
                        if len(formatted_string) >= MAX_TOTAL_CHARS:
                            formatted_string += "\n[Warning - Content truncated: reached maximum total size limit]\n"
                            return formatted_string
        else:
            if os.path.exists(input):
                formatted_string += process_file(input)
    elif isinstance(input, list):
        for file_path in input:
            if os.path.exists(file_path):
                formatted_string += process_file(file_path)
                if len(formatted_string) >= MAX_TOTAL_CHARS:
                    formatted_string += "\n[Warning - Content truncated: reached maximum total size limit]\n"
                    return formatted_string
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

    file_list = []
    for record in records:
        file_list.append(record)

    return file_list
