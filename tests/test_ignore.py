# whowasi: a tool to record source version information into binaries.
#
# Copyright (c) 2026 Institut des Géosciences de l'Environnement, Grenoble.
#
# License: BSD 3-clause "new" or "revised" license (BSD-3-Clause).
#
# This file tests whowasi._ignore.

from whowasi._ignore import CharacterRange


def test_CharacterRange_test_char_single_range():
    """Test CharacterRange.test_char with a single range."""
    assert CharacterRange("[A-Z]").test_char("A")
    assert CharacterRange("[A-Z]").test_char("F")
    assert CharacterRange("[A-Z]").test_char("Z")
    assert CharacterRange("[a-z]").test_char("a")
    assert CharacterRange("[a-z]").test_char("f")
    assert CharacterRange("[a-z]").test_char("z")
    assert not CharacterRange("[A-Z]").test_char("a")
    assert not CharacterRange("[A-Z]").test_char("f")
    assert not CharacterRange("[A-Z]").test_char("z")
    assert not CharacterRange("[A-Z]").test_char("4")
    assert not CharacterRange("[A-Z]").test_char("#")
    assert not CharacterRange("[a-z]").test_char("A")
    assert not CharacterRange("[a-z]").test_char("F")
    assert not CharacterRange("[a-z]").test_char("Z")
    assert not CharacterRange("[a-z]").test_char("4")
    assert not CharacterRange("[a-z]").test_char("#")
    assert CharacterRange("[0-9]").test_char("0")
    assert CharacterRange("[0-9]").test_char("4")
    assert CharacterRange("[0-9]").test_char("9")
    assert not CharacterRange("[0-9]").test_char("a")
    assert not CharacterRange("[0-9]").test_char("G")
    assert not CharacterRange("[0-9]").test_char("?")
    assert CharacterRange("[b-g]").test_char("b")
    assert CharacterRange("[b-g]").test_char("d")
    assert CharacterRange("[b-g]").test_char("g")
    assert not CharacterRange("[b-g]").test_char("a")
    assert not CharacterRange("[b-g]").test_char("h")


def test_CharacterRange_test_char_multiple_ranges():
    """Test CharacterRange.test_char with multiple ranges."""
    assert CharacterRange("[1-6a-g]").test_char("1")
    assert CharacterRange("[1-6a-g]").test_char("4")
    assert CharacterRange("[1-6a-g]").test_char("6")
    assert CharacterRange("[1-6c-g]").test_char("c")
    assert CharacterRange("[1-6c-g]").test_char("e")
    assert CharacterRange("[1-6c-g]").test_char("g")
    assert not CharacterRange("[1-6c-g]").test_char("0")
    assert not CharacterRange("[1-6c-g]").test_char("7")
    assert not CharacterRange("[1-6c-g]").test_char("b")
    assert not CharacterRange("[1-6c-g]").test_char("h")
