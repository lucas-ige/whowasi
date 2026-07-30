# whowasi: a tool to record source version information into binaries.
#
# Copyright (c) 2026 Institut des Géosciences de l'Environnement, Grenoble.
#
# License: BSD 3-clause "new" or "revised" license (BSD-3-Clause).

import subprocess


def run(args, **kwargs):
    """Run given command and arguments as a subprocess.

    Parameters
    ----------
    args: sequence
        The command to run and its arguments, eg. ["grep", "-v", "some text"].
    kwargs: dict
        These are passed "as is" to subprocess.run.

    Returns
    -------
    subprocess.CompletedProcess
        The result of running the command.

    Raises
    ------
    RuntimeError
        If the command returns a non-zero exit code.

    """
    out = subprocess.run(args, **kwargs)
    if out.returncode:
        msg = f"Command '{' '.join(args)}' exited with non-zero return code."
        raise RuntimeError(msg)
    return out


def run_stdout(args, **kwargs):
    """Run given command and arguments as a subprocess and return stdout.

    Parameters
    ----------
    args: sequence
        The command to run and its arguments, eg. ["grep", "-v", "some text"].
    kwargs: dict
        These are passed "as is" to subprocess.run, but cannot contain
        "capture_output" nor "text".

    Returns
    -------
    [str]
        The standard output of the command (one string per line).

    Raises
    ------
    RuntimeError
        If the command returns a non-zero exit code.

    """
    nope_list = ("capture_output", "text")
    forbidden_kwargs = list(filter(lambda kwarg: kwarg in nope_list, kwargs))
    if forbidden_kwargs:
        msg = f"Forbidden keyword argument(s): {', '.join(forbidden_kwargs)}."
        raise ValueError(msg)
    out = run(args, capture_output=True, text=True, **kwargs)
    return out.stdout[:-1].split("\n")

def detailed_git_status(repo):
    """Build a detailed report on the status of given git repository.

    Parameters
    ----------
    repo: str
        Path to git repository (not necessarily the root of the repository).

    Returns
    -------
    [str]
        A detailed report on the status of given repository (array of lines).

    """
    cmd = ["git", "--no-pager"]
    repo = run_stdout(cmd + ["rev-parse", "--show-toplevel", "-C", repo])[0]
    cmd += ["-C", repo]
    commit = run_stdout(cmd + ["log", "-n", "1", "--format=%H"])[0]
    diff = run_stdout(cmd + ["diff", "--color=never"])
    return [f"Commit = {commit}", ""] + diff
