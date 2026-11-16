"""Cases for record-test-commands.sh's CLAUDE.md rewrite and its refusals, in-process."""
import importlib

import pytest


@pytest.fixture
def record():
    return importlib.import_module("veri.record_test_commands")


def test_an_existing_tier_line_is_replaced_where_it_stands_keeping_what_precedes_its_marker_and_every_other_line(record):
    text = (b"# Project\n"
            b"Write `veri: fast tests:` lines here.\n"
            b"veri: fast tests:\n"
            b"- veri: fast tests: `old fast`\n"
            b"between\r\n"
            b"veri: all tests: old all\n"
            b"tail")

    assert record.recorded(text, b"make unit", b"make test") == (
        b"# Project\n"
        b"Write `veri: fast tests:` lines here.\n"
        b"veri: fast tests:\n"
        b"- veri: fast tests: make unit\n"
        b"between\r\n"
        b"veri: all tests: make test\n"
        b"tail")
