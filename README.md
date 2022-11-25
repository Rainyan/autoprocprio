[![GitHub release (latest SemVer including pre-releases)](https://img.shields.io/github/v/release/Rainyan/autoprocprio?include_prereleases)](https://github.com/Rainyan/autoprocprio/releases)
[![MIT](https://img.shields.io/github/license/Rainyan/autoprocprio)](LICENSE)
[![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)
[![Pylint](https://github.com/Rainyan/autoprocprio/actions/workflows/pycodestyle.yml/badge.svg)](https://github.com/Rainyan/autoprocprio/actions/workflows/pycodestyle.yml)
[![CodeQL](https://github.com/Rainyan/autoprocprio/actions/workflows/codeql.yml/badge.svg)](https://github.com/Rainyan/autoprocprio/actions/workflows/codeql.yml)

# autoprocprio

<hr>

### TL;DR:

Ad-hoc tool for making csgo not lag as much.

Windows app available; see the [Releases page](https://github.com/Rainyan/autoprocprio/releases) to download.

<hr>

### Longer version:

Python 3 script for automatically setting (primarily Windows) processes' CPU priority and affinity by process name. 

This script is a kludge meant for continuously setting `BAD_PROCNAMES` to
the lowest CPU priority, and isolating their threads affinity to CPU core(s)
separate from the list of processes defined in `GOOD_PROCNAMES`.

"Inspired" by repeated bad experiences with *steamwebhelper.exe* losing me
CS:GO rounds by using over 30 percent of CPU time when I really wanted to be
drawing video game frames with those cycles instead.

This script *should* be video game anti-cheat safe — all it does is iterate
running processes, and selectively read & reassign said process priority and
CPU affinity levels, much like one could manually do using a task manager — but use at your own risk.

For Python module requirements, please see the [requirements](requirements.txt) file.

## Usage:
### Windows app version:
#### Basic use:
  - Just run the app executable in the background
#### Custom app rules:
  - Create a shortcut to the executable.
  - Add the argparse options after the shortcut's Target path. Supported argparse options:
  ```
  -g GOOD, --good GOOD  comma-delimited list of app(s) to prioritize (optional); will overwrite defaults
  -b BAD, --bad BAD     comma-delimited list of app(s) to deprioritize (optional); will overwrite defaults
  -G, --appendgood      comma-delimited list of app(s) to prioritize (optional); will append to defaults
  -B, --appendbad       comma-delimited list of app(s) to deprioritize (optional); will append to defaults
  ```

For example:

![Example of setting the arguments via Windows shortcut GUI](https://user-images.githubusercontent.com/6595066/199398710-c4fd829b-11f4-43e6-aadc-a80244620f76.png)

This would append hammer.exe to the list of prioritized apps, and vrad.exe, vvis.exe, and vbsp.exe to the list of deprioritized apps.

### Python script version:
#### Basic use:
  - Run the script: `python autoprocprio.py`
  - Or from pipx:
    - Install:
        ```bash
        pip install --upgrade pipx
        pipx install git+https://github.com/Rainyan/autoprocprio.git
        ```
    - Run: `autoprocprio`
  - Or from pipenv:
    - Install: `pipenv --three && pipenv run pip install --upgrade -r requirements.txt`
    - Run: `pipenv run python autoprocprio.py`
    - Or run as sudo (required on Linuxes where lowering [niceness](https://man7.org/linux/man-pages/man2/nice.2.html) is typically a privileged action):
        ```bash
        pipenv shell && sudo $(which python) autoprocprio.py
        ```
 #### Custom app rules:
  - Launch the script with `--help` to see the supported argument inputs description.

## Troubleshooting/questions/feature requests
Feel free to [open a ticket](https://github.com/Rainyan/autoprocprio/issues)!
