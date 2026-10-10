# Python Scripts Collection

## Description

Collection of my own python scripts.

## Sections

- [cleanup](cleanup)
- [compress](compress)
- [copy_files](copy_files)
- [delete](delete)
- [generate_file_associations](generate_file_associations)
- [generate_folder_icons](generate_folder_icons)
- [generate_folder_images](generate_folder_images)
- [generate_shortcuts](generate_shortcuts)
- [group](group)
- [image](image)
- [jira](jira)
- [miscellaneous](miscellaneous)
- [overlay](overlay)
- [palette_tools](palette_tools)
- [pdf_to_image](pdf_to_image)
- [process_audio](process_audio)
- [process_books](process_books)
- [process_games](process_games)
- [process_manga](process_manga)
- [process_video](process_video)
- [rename](rename)
- [replace](replace)
- [steam](steam)
- [symlinks](symlinks)

## General Requirements

- Having python3 installed.
- Having the required dependencies installed.
  - You can run `install_all_dependencies.py` from the root level
  - You can run `pip install -r requirements.txt` individually from each module
- Having the required packages installed.
  - You can run `install_all_packages.py` from the root level
  - You can run `pip install .` individually from each package

## Running

- Execute `SCRIPT_NAME.py` from the file explorer.
- Run `py SCRIPT_NAME.py` from the terminal.
  - Depending on your installation, the executable may be either of these: `py` `py3` `python` `python3`.
  - Depending on the script, additional arguments may be used.<br>Check the individual scripts for more info.

(replace SCRIPT_NAME with your script of choice)

## Git Hooks

- Run `git config core.hooksPath _hooks` once per clone to enable the tracked hooks in [\_hooks](_hooks).
- The `pre-commit` hook runs `ruff check --fix` and `ruff format` on staged files and re-stages the changes.
- The `pre-push` hook runs `run_all_tests.py` and blocks the push if any test fails.
