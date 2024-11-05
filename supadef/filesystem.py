import os
import shutil
import tempfile
import zipfile
from typing import List
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern


def create_tempdir(key, nuke_existing=True):
    """
    Create a clean temporary directory.
    """
    # get the path that we should do our work in
    cwd = os.path.join(tempfile.gettempdir(), 'com.supadef.tempdir', key)
    # nuke the working directory, if it exists
    if nuke_existing and os.path.exists(cwd):
        # https://stackoverflow.com/questions/6996603/how-can-i-delete-a-file-or-folder-in-python
        shutil.rmtree(cwd)
    # create it
    os.makedirs(cwd)
    return cwd


def zip_directory(directory_path, zip_filename):
    # Create a ZIP file
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, directory_path)
                zipf.write(file_path, arcname=arcname)


def get_non_ignored_files(directory: str, gitignore_content: str) -> List[str]:
    # Create a PathSpec object from the gitignore content
    spec = PathSpec.from_lines(
        GitWildMatchPattern, gitignore_content.splitlines())

    non_ignored_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.relpath(
                os.path.join(root, file), directory)
            if not spec.match_file(file_path):
                non_ignored_files.append(file_path)

    return non_ignored_files


def copy_dir(source_dir: str, dest_dir: str, gitignore_content: str):
    # Get the list of files to copy
    files_to_copy = get_non_ignored_files(source_dir, gitignore_content)

    # Ensure the destination directory exists
    os.makedirs(dest_dir, exist_ok=True)

    # Copy each non-ignored file
    for file_path in files_to_copy:
        source_file = os.path.join(source_dir, file_path)
        dest_file = os.path.join(dest_dir, file_path)

        # Create the destination directory if it doesn't exist
        os.makedirs(os.path.dirname(dest_file), exist_ok=True)

        # Copy the file
        shutil.copy2(source_file, dest_file)
        print(f"Copied: {file_path}")

    print(f"Copied {len(files_to_copy)} files from {source_dir} to {dest_dir}")
