# whowasi: a tool to record source version information into binaries.
#
# Copyright (c) 2026 Institut des Géosciences de l'Environnement, Grenoble.
#
# License: BSD 3-clause "new" or "revised" license (BSD-3-Clause).
#
# This file implements tools to apply gitignore-style rules.

import re


def _indices_of_escaping_characters(s):
    """Return indices of escaping characters in given character string.

    Parameters
    ----------
    s: str
        Character string to analyze.

    Returns
    -------
    [int]
        List of the indices of all the escaping characters in s.

    Raises
    ------
    ValueError
        If given string ends with non-escaped backslash.

    """
    indices = []
    i, n = 0, len(s)
    while i < n:
        if s[i] == "\\":
            if i == n - 1:
                msg = "String ends with non-escaped backslash."
                raise ValueError(msg)
            indices.append(i)
            i += 1
        i += 1
    return indices


def _remove_non_escaped_trailing_spaces(s):
    """Return copy of given string without non-escaped trailing spaces.

    Parameters
    ----------
    s: str
        The character string to process.

    Returns
    -------
    str
        A copy of s, without non-escaped trailing spaces.

    """
    indices = _indices_of_escaping_characters(s)
    while s[-1].isspace() and len(s) - 2 not in indices:
        s = s[:-1]
    return s


def _check_range(range_):
    """Raise exception if given range is not valid.

    Parameters
    ----------
    range_: str
        The range to check, eg. "[A-Z]" or "[A-Z0-9]".


    Returns
    -------
    s:
        The given range, unmodified.

    Raises
    ------
    ValueError
        If given range is not valid.

    """
    if len(range_) < 5:
        msg = "Range is too short to be valid."
        raise ValueError(msg)
    if not range_.startswith("[") or not range_.endswith("]"):
        msg = "Range must be in between square brackets."
        raise ValueError(msg)
    content = range_[1:-1]
    n, r = divmod(len(content), 3)
    if r != 0:
        msg = "Range is invalid (number of characters not a multiple of 3)."
        raise ValueError(msg)
    # For now we are pretty strict about what we accept here
    sets = [
        "0123456789",
        "abcdefghijklmnopqrstuvwxyz",
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    ]
    for i in range(n):
        start, sep, end = content[3 * i : 3 * (i + 1)]
        if sep != "-":
            msg = f"Invalid separator: {sep}."
            raise ValueError(msg)
        for set_ in sets:
            try:
                i_start = set_.index(start)
                i_end = set_.index(end)
            except ValueError:
                continue
            if i_start >= i_end:
                msg = f"Range boundaries are out of order."
                raise ValueError(msg)
            break
        else:
            msg = "Could not parse range."
            raise ValueError(msg)
    return range_


class IgnoreRule:
    """Class to handle a single gitignore-style rule."""

    def __init__(self, rule):
        """Parse given rule.

        Parameters
        ----------
        rule: str
            The rule to parse (eg. "**/tests/*.py").

        """
        # Preliminary quality checks
        if rule.startswith("/"):
            msg = "Rule may not start with a slash."
            raise ValueError(msg)

        # Pre-process the rule
        rule = _remove_non_escaped_trailing_spaces(rule)
        if rule.startswith("!"):
            self._reverse = True
            rule = rule[1:]
        else:
            self._reverse = False

        # Create the internal regex representation of the rule
        self._re = ""
        i, n = 0, len(rule)
        found_double_asterisk = False
        while i < n:
            # Deal with escaped characters
            if rule[i] == "\\":
                if i == n - 1:
                    msg = "Rule may not end with non-escaped backslash."
                    raise ValueError(msg)
                elif rule[i + 1] == "/":
                    msg = "Escaped slash is forbidden."
                    raise ValueError(msg)
                self._re += re.escape(rule[i + 1])
                i += 2

            # Deal explicitly with the three possible occurences of **. Only
            # the first instance of ** is treated as such (all other
            # non-escaped * are treated as single *)
            elif i == 0 and rule[:3] == "**/":
                self._re += "(.+/|)"
                found_double_asterisk = True
                i = 3
            elif i > 0 and rule[i : i + 4] == "/**/":
                self._re += "(/|/.*/)"
                found_double_asterisk = True
                i += 4
            elif i == n - 3 and rule[i:] == "/**":
                self._re += "/.*"
                found_double_asterisk = True
                i += 3

            # A single non-escaped *should matches anything except a slash
            elif rule[i] == "*":
                self._re += "[^/]*"
                i += 1

            # A single non-escaped ? matches any one character except a slash
            elif rule[i] == "?":
                self._re += "[^/]"
                i += 1

            # Deal with ranges such as [a-z], or [A-Z0-9]
            elif rule[i] == "[":
                j = i + 1
                while j < n and rule[j] != "]":
                    j += 1
                if j >= n:
                    msg = "Could not get ending delimeter of range."
                    raise ValueError(msg)
                self._re += _check_range(rule[i : j + 1])
                i = j + 1

            # Deal with regular non-escaped characters
            else:
                self._re += re.escape(rule[i])
                i += 1

        self._re = re.compile(self._re)

    def test_path(self, path):
        """Test if given path matches the rule.

        Parameter
        ---------
        path: str
            The path to check.

        Returns
        -------
            True if given path matches the rule, False otherwise.

        """
        matches = self._re.fullmatch(path) is not None
        return matches if not self._reverse else not matches
