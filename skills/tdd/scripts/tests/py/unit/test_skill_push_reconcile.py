"""Cases for how skills/tdd/SKILL.md answers a rejected push, read as text.

Contract under test:
  At verify-refactor's `push-branch.sh` call site, exit 1 sends the run to the reconcile leaf and exit 2 bails;
  "exits 0 either way" is gone.
"""
import pathlib
import re

from skill_sections import plain as _plain

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

def _records(lines):
    out, rec = [], ""
    for line in lines:
        if re.match(r"[0-9]+\. ", line) or re.match(r"[ \t]*- ", line):
            if rec:
                out.append(rec)
            rec = line
        elif not line.strip():
            if rec:
                out.append(rec)
            rec = ""
        elif not rec:
            rec = line
        else:
            rec = rec + " " + line
    if rec:
        out.append(rec)
    return [_plain(re.sub(r"\s+", " ", r)) for r in out]


def test_both_push_branch_call_sites_branch_exit_1_to_a_supervised_develop_reconcile_leaf_and_exit_2_to_a_bail_the_reconcile_re_pushes_and_checks_the_ledger_or_bails_reconcile_failed_and_exits_0_either_way_is_gone():
    lines = SKILL.read_text().splitlines()
    records = _records(lines)
    assert records, "SKILL.md has no instructions to read — nothing could be checked"
    problems = []
    if any("exits 0 either way" in r for r in records):
        problems.append("SKILL.md still says push-branch.sh exits 0 either way")
    assert not problems, "\n".join(problems)
