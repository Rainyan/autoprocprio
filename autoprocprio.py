#!/usr/bin/env python3

"""This script is a kludge meant for continuously setting "BAD_PROCNAMES" to
   the lowest CPU priority, and isolating their threads affinity to CPU core(s)
   separate from the list of processes defined in "GOOD_PROCNAMES".

   "Inspired" by repeated bad experiences with steamwebhelper.exe losing me
   CS:GO rounds by using over 30 percent of CPU time when I really wanted to be
   drawing video game frames with those cycles instead.

   This script *should* be video game anti-cheat safe — all it does is iterate
   running processes, and selectively read & reassign said process priority and
   CPU affinity levels — but use at your own risk.

   URL to the latest version of this script:
       https://github.com/Rainyan/autoprocprio

   Config (recommended way):
     - Please see the readme for details on application args.
   Config (hardcoded defaults):
     - Assign the BAD_PROCNAMES and GOOD_PROCNAMES globals as required.

   Usage:
     - Just run the script ("python autoprocprio.py").
"""

# Copyright 2021 https://github.com/Rainyan
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import atexit
import datetime
import time
import os
import psutil
from psutil import cpu_count
from termcolor import colored


def platform_is_windows():
    """Returns a boolean of whether the current OS platform is Windows."""
    return os.name == "nt"


# pylint: disable=import-error
if platform_is_windows():
    import colorama  # For command prompt colors to work properly
    import ctypes    # For checking for admin privileges
    import win32api  # For catching user closing the app window via the X icon

SCRIPT_NAME = "AutoProcPrio"
SCRIPT_VERSION = "7.0.3"


def add_app(executable_name):
    """Returns executable name, suffixed with OS specific file extension.
    """
    has_windows_extension = executable_name.endswith(".exe")
    if platform_is_windows():
        if not has_windows_extension:
            executable_name += ".exe"
    else:
        assert not has_windows_extension
    return executable_name


# List of all the process names to prevent from using too much CPU time.
# This sets low priority and isolates them to CPU core 0.
BAD_PROCNAMES = [
    add_app(SCRIPT_NAME.lower()),  # Self-limit since we aren't time sensitive
    add_app("steamwebhelper"),
]


# List of all the process names where we really care about CPU performance.
# This sets high priority and isolates them from the "BAD_PROCNAMES" CPU core.
GOOD_PROCNAMES = [
    add_app("csgo"),
    add_app("hl2"),
]

# How long to wait between proc CPU niceness/affinity updates, in seconds.
POLL_DELAY_SECONDS = 60

# Whether to print some debug information.
VERBOSE = False

# Flag for sleeping threads to detect when we are about to exit.
EXITING = False

# For Windows, this is the "low priority" option on taskmgr.
BAD_NICENESS = psutil.IDLE_PRIORITY_CLASS if platform_is_windows() else 15
# Force buggy procs on these core(s).
BAD_AFFINITY = [0, ]
# If you don't want to set this, pass None to the TargetProcs ctor arg.
assert len(BAD_AFFINITY) > 0, "Need at least one CPU core"

# For Windows, this is the "high priority" option on taskmgr.
GOOD_NICENESS = psutil.HIGH_PRIORITY_CLASS if platform_is_windows() else -15
# Use all cores except the one(s) reserved for "bad" procs.
GOOD_AFFINITY = [a for a in list(range(cpu_count())) if a not in BAD_AFFINITY]
# If you don't want to set this, pass None to the TargetProcs ctor arg.
assert len(GOOD_AFFINITY) > 0, "Need at least one CPU core"


def is_admin():
    """Returns whether the user is running this script as admin/sudo."""
    if platform_is_windows():
        return ctypes.windll.shell32.IsUserAnAdmin()
    return "SUDO_UID" in os.environ


if platform_is_windows():
    colorama.init()  # Only required on Windows.

    def on_exit(signal_type):
        """Catch user exit signal, including user pressing the X icon.
        """
        global EXITING
        EXITING = True
        print(f"Caught signal: {signal_type}")
        restore_original_ps_values()
    win32api.SetConsoleCtrlHandler(on_exit, True)

# See possible color values at: https://pypi.org/project/termcolor/
ARROW_COLOR = "white"
DATE_COLOR = "yellow"
PROC_COLOR = "cyan"
PS_BAD_COLOR = "red"
PS_GOOD_COLOR = "green"


def get_nice_name(nice):
    """Get human readable description of a CPU priority ("nice") level.
    """
    if platform_is_windows():
        if nice == psutil.IDLE_PRIORITY_CLASS:
            return "Low"
        if nice == psutil.BELOW_NORMAL_PRIORITY_CLASS:
            return "Below normal"
        if nice == psutil.NORMAL_PRIORITY_CLASS:
            return "Normal"
        if nice == psutil.ABOVE_NORMAL_PRIORITY_CLASS:
            return "Above normal"
        if nice == psutil.HIGH_PRIORITY_CLASS:
            return "High"
        if nice == psutil.REALTIME_PRIORITY_CLASS:
            return "Realtime"
        return f"Unknown ({nice})"
    # Not Windows
    try:
        nice_n = int(nice)
        explanation = ""
        best_nice = -20
        worst_nice = 19
        # Adding +1 to include the upper bound.
        if nice_n not in range(best_nice, worst_nice + 1):
            explanation = "unknown"
        else:
            nice_percent = ((nice_n - worst_nice) / -(abs(best_nice)
                            + worst_nice) * 100)
            nice_percent += 0  # In case it was negative zero
            explanation = f"{nice_percent:.1f}%"
        return f"nice level {nice_n} ({explanation})"
    except ValueError:
        pass
    return f"{nice}"


def timestamp():
    """Return a pretty-print colored timestamp."""
    text = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"
    return colored(text, DATE_COLOR)


def print_info(msg, always_print=False, num_extra_lvls=0):
    """Helper for pretty-printing a line of info."""
    if not VERBOSE and not always_print:
        return
    arrow_base = "-"
    for _ in range(num_extra_lvls):
        arrow_base += "-"
    arrow = arrow_base + ">"  # "->" style arrow symbol
    print(timestamp() + " " + colored(arrow, ARROW_COLOR) + " " + msg)


class TargetProcs():
    """Set all processes of procname to specific nice and affinity.

       Periodically call update_procs() to refresh the proc cache.
    """

    def __init__(self, procname, nice=None, affinity=None, verbose=False):
        if platform_is_windows():
            assert procname.endswith(".exe")
        self.verbose = verbose
        self.procname = procname
        self.nice = nice
        self.affinity = affinity
        self.cachedprocs = []
        self.og_ps_vals = {}  # key: ps, val: tuple of (nice, affinity)
        print_info('Now ready to track processes for: '
                   f'{colored(self.procname, PROC_COLOR)}.', self.verbose, 4)

    def set_procs_properties(self):
        """Set the CPU niceness and affinity levels of our procs."""
        ps_color = PS_BAD_COLOR if self.nice == BAD_NICENESS else PS_GOOD_COLOR

        for p in self.cachedprocs:
            if self.nice is not None \
                    and self._get_nice(p) != self.nice \
                    and self._set_nice(p, self.nice):
                colored_nice = colored(get_nice_name(self._get_nice(p)),
                                       ps_color)
                print_info(f"{colored(self.procname, PROC_COLOR)}:"
                           f" Set nice to {colored_nice} priority", True, 4)
            if self.affinity is not None \
                    and self._get_affinity(p) != self.affinity \
                    and self._set_affinity(p, self.affinity):
                colored_aff = colored(self._get_affinity(p), ps_color)
                print_info(f'{colored(self.procname, PROC_COLOR)}: Set '
                           f"affinity to CPU cores {colored_aff}", True, 4)

    def update_procs(self):
        """Remove cached procs that have been terminated, cache any
           relevant procs that have not yet been cached, and finally
           call set_procs_properties().
        """
        self.cachedprocs = [p for p in self.cachedprocs if p.is_running()]
        self.og_ps_vals = {p: t for p, t in self.og_ps_vals.items()
                           if p.is_running()}

        for p in psutil.process_iter(["name", "pid"]):
            found_already = False
            for cp in self.cachedprocs:
                if p.pid == cp.pid:
                    found_already = True
                    break
            if not found_already and p.name() == self.procname:
                self.cachedprocs.append(p)
                self.og_ps_vals[p] = (self._get_nice(p), self._get_affinity(p))
        # Always showing this, because it's probably useful info to user
        print_info(f"{colored(self.procname, PROC_COLOR)} "
                   f"(priority: {get_nice_name(self.nice)}) currently caching "
                   f"{len(self.cachedprocs)} proc(s).", True, 2)

        self.set_procs_properties()

    def restore_procs_properties(self):
        """Restore original values for nice (priority) and CPU affinity of all
           previously cached instances of self.procname where that process
           instance is still currently running.
        """
        print_restore_info = True
        print_info("Restoring procs priority and affinity for instances of "
                   f"{colored(self.procname, PROC_COLOR)}...",
                   print_restore_info)

        self.og_ps_vals = {p: t for p, t in self.og_ps_vals.items()
                           if p.is_running()}

        if len(self.og_ps_vals) == 0:
            print_info("No instances found; skipping.", True, 2)
            return
        for p in self.og_ps_vals:
            og_tuple = self.og_ps_vals.get(p)
            if og_tuple is None:
                continue
            original_nice = og_tuple[0]
            original_affinity = og_tuple[1]
            proc_name = colored(p.name(), PROC_COLOR)

            nice_bef = self._get_nice(p)
            if nice_bef is None:
                continue
            if nice_bef != original_nice and self._set_nice(p, original_nice):
                nice_bef = colored(get_nice_name(nice_bef), PS_BAD_COLOR)
                nice_aft = colored(get_nice_name(original_nice), PS_GOOD_COLOR)
                print_info(f"Restored {proc_name} priority: "
                           f"{nice_bef} => {nice_aft}",
                           print_restore_info, 2)

            aff_bef = self._get_affinity(p)
            if aff_bef is None:
                continue
            if aff_bef != original_affinity:
                aff_bef = colored(aff_bef, PS_BAD_COLOR)
                aff_aft = colored(original_affinity, PS_GOOD_COLOR)
                if self._set_affinity(p, original_affinity):
                    print_info(f"Restored {proc_name} CPU core affinity: "
                               f"{aff_bef} => {aff_aft}",
                               print_restore_info, 2)

    def _get_nice(self, p):
        return self._try_psutil_get(p.nice)

    def _get_affinity(self, p):
        return self._try_psutil_get(p.cpu_affinity)

    def _set_nice(self, p, nice):
        return self._try_psutil_set(p.nice, nice)

    def _set_affinity(self, p, affinity):
        return self._try_psutil_set(p.cpu_affinity, affinity)

    def _try_psutil_get(self, fn):
        try:
            return fn()
        except psutil.AccessDenied as err:
            print_info(colored(f"WARNING: {err}", PS_BAD_COLOR), True)
        return False

    def _try_psutil_set(self, fn, val):
        try:
            fn(val)
            return True
        except psutil.AccessDenied as err:
            print_info(colored(f"WARNING: {err}", PS_BAD_COLOR), True)
            if not is_admin():
                print_info(colored("Please try running as admin.",
                                   PS_BAD_COLOR), True)
        return False


PROCS = []


def conditional(decorator, condition):
    def the_decorator(fun):
        return fun if not condition else decorator(fun)
    return the_decorator


# Can't register atexit on Windows, because we gotta catch the interrupt
# using a Win API in order to also catch the possibility of user closing
# the window via the top-right X icon.
@conditional(atexit.register, not platform_is_windows())
def restore_original_ps_values():
    """This function is registered to run at script exit.
       It's used to restore the processes' nice and affinity values to how they
       were prior to starting of this script, for ensuring unaffected app
       performance once our custom high priority settings defined in this
       script aren't needed anymore.
    """
    for p in PROCS:
        p.restore_procs_properties()
    print_info(colored("\n"
                       " = = = = = = = = = = = = = = = = = = = = = = = = =  ="
                       f"\n = The {SCRIPT_NAME} script is now exiting. Goodbye"
                       "! =\n = = = = = = = = = = = = = = = = = = = = = = = = "
                       "=  =\n",
                       "magenta"), True)


def main():
    parser = argparse.ArgumentParser(
        prog=SCRIPT_NAME,
        description="Automatically set processes' CPU priority and affinity "
                    "by process name",
        epilog=f"Version {SCRIPT_VERSION}",
    )
    parser.add_argument(
        "-g",
        "--good",
        help="comma-delimited list of app(s) to prioritize (optional); "
             "will overwrite defaults",
    )
    parser.add_argument(
        "-b",
        "--bad",
        help="comma-delimited list of app(s) to deprioritize (optional); "
             "will overwrite defaults",
    )
    parser.add_argument(
        "-G",
        "--appendgood",
        help="comma-delimited list of app(s) to prioritize (optional); "
             "will append to defaults",
    )
    parser.add_argument(
        "-B",
        "--appendbad",
        help="comma-delimited list of app(s) to deprioritize (optional); "
             "will append to defaults",
    )
    args = parser.parse_args()

    if any((args.good, args.appendgood)):
        assert not all(
            (args.good, args.appendgood)
        ), "Can't use --good and --appendgood at the same time."
    if any((args.bad, args.appendbad)):
        assert not all(
            (args.bad, args.appendbad)
        ), "Can't use --bad and --appendbad at the same time."

    print(f"\n\t== {SCRIPT_NAME} version {SCRIPT_VERSION} ==\n")

    global PROCS

    if args.good or args.appendgood:
        print_info("Setting custom GOOD_PROCNAMES...")
        try:
            for procname in [
                x
                for x in list(set((args.good or args.appendgood).split(",")))
                if add_app(x) not in [y.procname for y in PROCS]
            ]:
                PROCS.append(
                    TargetProcs(
                        add_app(procname), GOOD_NICENESS, GOOD_AFFINITY,
                        VERBOSE
                    )
                )
        except AttributeError:
            pass
    if not args.good:
        print_info("Setting default GOOD_PROCNAMES...")
        for procname in GOOD_PROCNAMES:
            PROCS.append(
                TargetProcs(procname, GOOD_NICENESS, GOOD_AFFINITY, VERBOSE)
            )

    if args.bad or args.appendbad:
        print_info("Setting custom BAD_PROCNAMES...")
        try:
            for procname in [
                x
                for x in list(set((args.bad or args.appendbad).split(",")))
                if add_app(x) not in [y.procname for y in PROCS]
            ]:
                PROCS.append(
                    TargetProcs(add_app(procname), BAD_NICENESS, BAD_AFFINITY,
                                VERBOSE)
                )
        except AttributeError:
            pass
    if not args.bad:
        print_info("Setting default BAD_PROCNAMES...")
        for procname in BAD_PROCNAMES:
            PROCS.append(
                TargetProcs(procname, BAD_NICENESS, BAD_AFFINITY, VERBOSE)
            )

    # If we're setting ourselves with low priority, make sure that item is
    # the last in the list, so that we're guaranteed to have sufficient
    # niceness to get all the way through self-initialization before it
    # takes effect.
    try:
        PROCS.append(
            PROCS.pop(
                PROCS.index(
                    [
                        x
                        for x in PROCS
                        if x.procname == add_app(SCRIPT_NAME.lower())
                    ][0]
                )
            )
        )
    except (ValueError, IndexError):
        pass

    global EXITING
    while not EXITING:
        print_info("Proc update...")
        for p in PROCS:
            p.update_procs()
        print_info(colored("(Now active. To revert CPU priority changes, "
                           "please close this window when you are done.)",
                           "magenta"), True)
        try:
            time.sleep(POLL_DELAY_SECONDS)
        except KeyboardInterrupt as e:
            EXITING = True


if __name__ == "__main__":
    main()
