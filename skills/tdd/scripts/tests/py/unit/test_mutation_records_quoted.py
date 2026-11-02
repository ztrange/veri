import re

import pytest
from conftest import ROOT

from veri.pin_recheck import records

UNQUOTED_BASH_C = re.compile(r"bash -c(?! ?['\"])")


@pytest.mark.tree_audit("every .tdd/*-mutations.md record in this repository")
def test_2877_no_mutation_record_holds_a_bash_c_command_not_followed_by_a_quote():
    offenders = []
    for path in sorted((ROOT / ".tdd").glob("*-mutations.md")):
        for record in records(path.read_text(encoding="utf-8")):
            if UNQUOTED_BASH_C.search(record.get("command", "")):
                offenders.append("%s: %s" % (path.name, record["command"]))
    assert offenders == []
