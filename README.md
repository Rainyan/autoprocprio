![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/downloads-pre/Rainyan/autoprocprio/latest/total)
[![Pylint](https://github.com/Rainyan/autoprocprio/actions/workflows/pycodestyle.yml/badge.svg)](https://github.com/Rainyan/autoprocprio/actions/workflows/pycodestyle.yml)

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
  - Just run the script: `python autoprocprio.py`
  - Or from virtual env: `pipenv install && pipenv run python autoprocprio.py`
