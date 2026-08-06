# whowasi: a tool to record source version information into binaries.
#
# Copyright (c) 2026 Institut des Géosciences de l'Environnement, Grenoble.
#
# License: BSD 3-clause "new" or "revised" license (BSD-3-Clause).

import os
import subprocess

from ._ignore import IgnoreRuleSet


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


def detailed_git_status(repo, ignore=IgnoreRuleSet([])):
    """Build a detailed report on the status of given git repository.

    Parameters
    ----------
    repo: str
        Path to git repository (not necessarily the root of the repository).
    ignore: IgnoreRuleSet
        Rules to ignore certain files.

    Returns
    -------
    [str]
        The report on the status of given repository (array of lines of text).

    """
    # Prepare git command and get path to root of repository
    git = ["git", "--no-pager"]
    repo = run_stdout(git + ["rev-parse", "--show-toplevel", "-C", repo])[0]
    git += ["-C", repo]

    # Add information about current commit
    pretty = "%n".join(
        [
            " - Commit:  %H",
            " - Author:  %an <%aE>",
            " - Date:    %ad",
            " - Subject: %s",
        ]
    )
    cmd = git + ["log", "-n", "1", "--color=never", f'--pretty={pretty}']
    status = ["Commit", "------", ""] + run_stdout(cmd)

    # Get lists of new, modified, and deleted files
    files = {"new": [], "mod": [], "del": []}
    mapping = {
        "?? ": "new",
        " M ": "mod",
        "M  ": "mod",
        "MM ": "mod",
        " D ": "del",
    }
    for f in run_stdout(git + ["status", "-uall", "--porcelain=v1"]):
        if f != "" and not ignore.test_path(f[3:]):
            files[mapping[f[:3]]].append(f[3:])

    # Add list and content of new files
    for f in files["new"]:
        filepath = os.path.join(repo, f)
        # A file can be a sim link, a binary, or a text file
        try:
            target = os.readlink(filepath)
        except OSError:
            try:
                with open(filepath) as opened:
                    lines = opened.read().split("\n")
            except UnicodeDecodeError:
                text = f"New file: {f}, which seems to be binary"
                status += ["", text, "-" * len(text)]
            else:
                status += ["", f"New file: {f}", "-" * (10 + len(f)), ""]
                status += lines
        else:
            text = f"New symbolic link: {f} -> {target}"
            status += ["", text, "-" * len(text)]

    # Add list of modified files and their diff
    for f in files["mod"]:
        status += ["", f"Modified file: {f}", "-" * (15 + len(f)), ""]
        status += run_stdout(git + ["diff", "HEAD", "--color=never", f])

    # Add list of deleted files
    if files["del"]:
        status += ["", "List of deleted files", "-" * 21, ""]
        status += [f" - {f}" for f in files["del"]]

    return status


def write_line_c(line, stream="stream"):
    """Prepare the C instruction to write given line.

    Parameters
    ----------
    line: str
        The line to write.
    stream: str
        The name of the C variable that represents the stream where to write.

    Returns
    -------
    str
        The C instruction to write the line.

    """
    line = line.replace("\\", "\\\\").replace('"', '\\"')
    return f'fputs("{line}\\n", stream)'


def write_line_f90(line, unit="unit"):
    """Prepare the FORTRAN 90+ instruction to write given line.

    Parameters
    ----------
    line: str
        The line to write.
    unit: str
        The name of the FORTRAN variable that represents the file unit where
        to write.

    Returns
    -------
    str
        The FORTRAN 90+ instruction to write the line.

    """
    substrs = []
    i, n = 0, len(line)
    while i < n:
        if line[i] == '"':
            substrs.append("'" + '"' + "'")
            i += 1
        else:
            j = i
            while j < n and line[j] != '"':
                j += 1
            substrs.append(f'"{line[i:j]}"')
            i = j
    n = max(len(substrs), 1)
    return f"write({unit}, '({n}A)') " + ", ".join(substrs)
