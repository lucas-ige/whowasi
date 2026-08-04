# whowasi: a tool to record source version information into binaries.
#
# Copyright (c) 2026 Institut des Géosciences de l'Environnement, Grenoble.
#
# License: BSD 3-clause "new" or "revised" license (BSD-3-Clause).
#
# This file implements tools to apply gitignore-style rules.

class CharacterRange():
    """A character range, eg. "[A-Z]" or "[A-Z0-9]"."""

    def __init__(self, range_):
        """Parse and self-define with given range.

        Parameters
        ----------
        range_: str
            The range to parse, eg. "[A-Z]" or "[A-Z0-9]".

        """
        self._ranges = []
        if not range_.startswith("[") or not range_.endswith("]"):
            msg = "Range must be in square brackets."
            raise ValueError(msg)
        content = range_[1:-1]
        if len(content) == 0 or len(content) % 3 != 0:
            msg = "Cannot parse range (bad length)."
            raise ValueError(msg)
        for i in range(len(content) // 3):
            self._process_single_range(content[3*i:3*(i+1)])

    def _process_single_range(self, range_):
        """Parse given single range and add it to self.

        Parameters
        ----------
        range_: str
            The range to parse, without square brackets, eg "A-Z" or "0-9".

        """
        start, sep, end = range_
        if sep != "-":
            msg = f"Expecting dash as separator but found {sep} instead."
            raise ValueError(msg)
        # We do not want to rely on the internal representation of characters
        # in the host system, so we hard-code them
        sets = [
            "0123456789",
            "abcdefghijklmnopqrstuvwxyz",
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        ]
        for set_ in sets:
            try:
                i_start = set_.index(start)
                i_end = set_.index(end)
            except ValueError:
                continue
            if i_start >= i_end:
                msg = f"Range boundaries out of order in range {range_}."
                raise ValueError(msg)
            self._ranges.append(set_[i_start : i_end + 1])
            return
        msg = f"Could not parse range {range_}."
        raise ValueError(msg)

    def test_char(self, c):
        """Tesst whether given character belongs to self.

        Parameters
        ----------
        c: str (len=1)
            Character to test.

        Returns
        -------
            True if c belongs to range defined by self, False otherwise.

        """
        if len(c) != 1:
            msg = f"Expecting single character, got '{c}'."
            raise ValueError(msg)
        for range_ in self._ranges:
            try:
                range_.index(c)
            except ValueError:
                continue
            return True
        return False
