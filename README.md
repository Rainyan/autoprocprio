[![GitHub release (latest SemVer including pre-releases)](https://img.shields.io/github/v/release/Rainyan/autoprocprio?include_prereleases)](https://github.com/Rainyan/autoprocprio/releases)
[![MIT](https://img.shields.io/github/license/Rainyan/discord-bot-ntpug)](LICENSE)
[![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)
[![Pylint](https://github.com/Rainyan/autoprocprio/actions/workflows/pycodestyle.yml/badge.svg)](https://github.com/Rainyan/autoprocprio/actions/workflows/pycodestyle.yml)
[![CodeQL](https://github.com/Rainyan/discord-bot-ntpug/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/Rainyan/discord-bot-ntpug/actions/workflows/codeql-analysis.yml)

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

## Config:
  - Assign the `BAD_PROCNAMES` and `GOOD_PROCNAMES` globals as required.

## Usage:
### Windows app version:
#### Basic use:
  - Just run the app executable in the background
#### Custom app rules:
  - Create a shortcut to the executable.
  - Add the argparse options after the shortcut's Target path. Supported argparse options:
  ```
  -g GOOD, --good GOOD  comma-delimited list of app(s) to prioritize (optional)
  -b BAD, --bad BAD     comma-delimited list of app(s) to deprioritize (optional)
  -G, --appendgood      if set, will append the good apps list instead of overwriting
  -B, --appendbad       if set, will append the bad apps list instead of overwriting
  ```
  ![Example of setting the arguments via Windows shortcut GUI](https://user-images.githubusercontent.com/6595066/199002550-e61a06c0-8fef-40fe-a6ca-da51af1db5fd.png)

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
