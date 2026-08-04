# whowasi: a tool to record source version information into binaries.
#
# Copyright (c) 2026 Institut des Géosciences de l'Environnement, Grenoble.
#
# License: BSD 3-clause "new" or "revised" license (BSD-3-Clause).
#
# This file tests whowasi._ignore.

import pytest

from whowasi._ignore import (
    IgnoreRule,
    _check_range,
    _indices_of_escaping_characters,
    _remove_non_escaped_trailing_spaces,
)


def test_indices_of_escaping_characters():
    """Test _indices_of_escaping_characters."""
    assert _indices_of_escaping_characters("hello") == []
    assert _indices_of_escaping_characters(r"he\llo") == [2]
    assert _indices_of_escaping_characters(r"he\llo\ ") == [2, 6]
    assert _indices_of_escaping_characters(r"he\\\llo\ ") == [2, 4, 8]
    assert _indices_of_escaping_characters(r"hello\\") == [5]
    with pytest.raises(ValueError):
        assert _indices_of_escaping_characters("hello\\")


def test_remove_non_escaped_trailing_spaces():
    """Test _remove_non_escaped_trailing_spaces."""
    fct = _remove_non_escaped_trailing_spaces
    assert fct("hello") == "hello"
    assert fct("hello ") == "hello"
    assert fct("hello \t") == "hello"
    assert fct("hello\\ \\\t") == "hello\\ \\\t"
    assert fct("hello\\ \\\t ") == "hello\\ \\\t"
    assert fct("hello\\ \\\t \t") == "hello\\ \\\t"


def test_check_range():
    """Test _check_range."""
    for valid in ("[A-Z]", "[b-g]", "[0-4]", "[A-Z0-9]", "[b-mA-V]"):
        assert _check_range(valid) == valid
    for invalid in ("[A-]", "b-g", "[0_4]", "[Z-A]"):
        with pytest.raises(ValueError):
            assert _check_range(invalid)


def test_IgnoreRule_test_path():
    """Test IgnoreRule.test_path."""
    assert IgnoreRule("**/*.py").test_path("hello.py")
    assert IgnoreRule("**/*.py").test_path("foo/hello.py")
    assert IgnoreRule("**/*.py").test_path("foo/bar/hello.py")
    assert IgnoreRule("foo/**/*.py").test_path("foo/hello.py")
    assert IgnoreRule("foo/**/*.py").test_path("foo/bar/hello.py")
    assert IgnoreRule("foo/**/*.py").test_path("foo/bar/ter/hello.py")
    assert IgnoreRule("foo/**").test_path("foo/hello.py")
    assert IgnoreRule("foo/**").test_path("foo/bar/hello.py")
    assert IgnoreRule("foo/bar/*.py").test_path("foo/bar/hello.py")
    assert IgnoreRule("foo/bar/*.py").test_path("foo/bar/world.py")
    assert IgnoreRule("foo/bar/h?llo.py").test_path("foo/bar/hello.py")
    assert not IgnoreRule("**/*.py").test_path("hello.pyA")
    assert not IgnoreRule("**/*.py").test_path("foo/hello.pyA")
    assert not IgnoreRule("**/*.py").test_path("foo/bar/hello.pyA")
    assert not IgnoreRule("foo/**/*.py").test_path("foo/hello.pyA")
    assert not IgnoreRule("foo/**/*.py").test_path("foo/bar/hello.pyA")
    assert not IgnoreRule("foo/**/*.py").test_path("foo/bar/ter/hello.pyA")
    assert IgnoreRule("foo/**").test_path("foo/hello.pyA")
    assert IgnoreRule("foo/**").test_path("foo/bar/hello.pyA")
    assert not IgnoreRule("foo/bar/*.py").test_path("foo/bar/hello.pyA")
    assert not IgnoreRule("foo/bar/*.py").test_path("foo/bar/world.pyA")
    assert not IgnoreRule("foo/bar/h?llo.py").test_path("foo/bar/hello.pyA")
