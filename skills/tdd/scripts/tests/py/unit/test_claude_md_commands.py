"""Every `.PHONY` target of the root Makefile has a row in CLAUDE.md's *Commands* table (#4054, PRD 025.19 MT3).

Completeness only, as test_scripts_md_rows.py checks SCRIPTS.md: what a row says is graded by its CLAUDE.md row in
REQUIREMENTS.md, never pinned here."""
import re

from conftest import ROOT


def phony_targets(makefile):
    return [name for line in re.findall(r"^\.PHONY:(.*)$", makefile, flags=re.M) for name in line.split()]


def commands_rows(claude_md):
    section = claude_md.split("\n## Commands\n", 1)[1]
    section = re.split(r"^## ", section, maxsplit=1, flags=re.M)[0]
    return set(re.findall(r"^\| `make ([\w-]+)", section, flags=re.M))


def unlisted_targets(makefile, claude_md):
    rows = commands_rows(claude_md)
    return [target for target in phony_targets(makefile) if target not in rows]


def test_every_phony_makefile_target_has_a_row_in_claude_md_s_commands_table_4054():
    makefile = (ROOT / "Makefile").read_text()
    claude_md = (ROOT / "CLAUDE.md").read_text()

    assert phony_targets(makefile), "no .PHONY target read from the Makefile"
    assert not unlisted_targets(makefile, claude_md), (
        "Makefile .PHONY targets with no `make <target>` row in CLAUDE.md's Commands table: %s"
        % unlisted_targets(makefile, claude_md))


def test_a_target_is_matched_by_its_whole_name_and_a_row_outside_the_commands_section_does_not_count_4054():
    makefile = ".PHONY: test unit\n.PHONY: run-finished\n"
    claude_md = ("# x\n\n## Commands\n\n| | |\n|---|---|\n| `make test` | a |\n| `make run-finished ISSUE=<n>` | b |\n"
                 "| `make units` | c |\n\n## Other\n\n| `make unit` | d |\n")

    assert unlisted_targets(makefile, claude_md) == ["unit"]
