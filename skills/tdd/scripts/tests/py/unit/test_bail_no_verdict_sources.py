"""BAIL.md's `no-verdict` entry names every script whose exit 2 bails `no-verdict`, and calls it a system failure.

A new `no-verdict` source is added to NO_VERDICT_SOURCES and to BAIL.md together.
"""
import re

from conftest import ROOT

NO_VERDICT_SOURCES = [
    "verify.sh",
    "run-verdict.sh",
    "grade-prose.sh",
    "skill-edit-step.sh",
    "resume-clean.sh",
    "rebase-onto-default.sh",
    "cover-outcome.sh",
    "ledger-growth.sh",
]


def entry_problems(bail_md):
    entry = re.search(r"^- `no-verdict` .*?(?=^- `|\Z)", bail_md, re.S | re.M).group(0)
    named = set(re.findall(r"[\w-]+\.sh", entry))
    problems = [f"missing {name}" for name in NO_VERDICT_SOURCES if name not in named]
    problems += [f"extra {name}" for name in sorted(named - set(NO_VERDICT_SOURCES))]
    if "**system** failure" not in entry:
        problems.append("not a system failure")
    return problems


def test_2152_bail_md_no_verdict_entry_names_every_source_and_calls_it_a_system_failure():
    bail_md = (ROOT / "skills" / "tdd" / "BAIL.md").read_text()
    entry = re.search(r"^- `no-verdict` .*?(?=^- `|\Z)", bail_md, re.S | re.M).group(0)

    assert {
        "real": entry_problems(bail_md),
        "dropped": entry_problems(bail_md.replace("`cover-outcome.sh`", "`cover`")),
        "extra": entry_problems(bail_md.replace("`cover-outcome.sh`", "`cover-outcome.sh` or `bogus.sh`")),
        "process": entry_problems(bail_md.replace(entry, entry.replace("**system** failure", "**process** failure"))),
    } == {
        "real": [],
        "dropped": ["missing cover-outcome.sh"],
        "extra": ["extra bogus.sh"],
        "process": ["not a system failure"],
    }


def test_2152_planted_no_verdict_entries_are_each_refused_by_the_one_fixed_list():
    names = ", ".join(f"`{name}`" for name in NO_VERDICT_SOURCES)
    whole = f"- `no-verdict` exit 2 from {names}: a **system** failure.\n- `other` x.\n"

    assert {
        "whole": entry_problems(whole),
        "dropped": entry_problems(whole.replace("`grade-prose.sh`, ", "")),
        "extra": entry_problems(whole.replace("`verify.sh`", "`verify.sh`, `bogus.sh`")),
        "process": entry_problems(whole.replace("**system**", "**process**")),
    } == {
        "whole": [],
        "dropped": ["missing grade-prose.sh"],
        "extra": ["extra bogus.sh"],
        "process": ["not a system failure"],
    }
