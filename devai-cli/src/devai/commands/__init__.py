import shutil, os, sys


os.environ["GIT_PYTHON_REFRESH"] = "quiet"
if shutil.which("git") is None:
    print("Git is required but not installed. Exiting.")
    sys.exit(1)

from . import cmd, prompt, release, review, document
