"""In-process cases for veri/refactor_budget.py, the module refactor-budget.sh is a shim over."""
import importlib
import pathlib
import re
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def refactor_budget():
    return importlib.import_module("veri.refactor_budget")


def stated(path, pattern):
    hit = re.search(pattern, path.read_text().replace("\n", " "))
    return re.findall(r"[0-9]+", hit.group(0))[-1] if hit else "<none>"


def test_main_with_both_budgets_unset_answers_against_the_default_every_prose_statement_of_it_names(monkeypatch, capsys, refactor_budget):
    monkeypatch.delenv("VERI_REFACTOR_BUDGET", raising=False)
    monkeypatch.delenv("VERI_ISSUE_REFACTOR_BUDGET", raising=False)
    seen = []
    for count in ("4", "5"):
        code = refactor_budget.main([count])
        out, _ = capsys.readouterr()
        seen.append((code, out))
    in_force = {re.match(r"refactor [0-9]+/([0-9]+) ", out).group(1) for _, out in seen}
    sites = {
        "refactor-budget.sh-header": stated(SCRIPTS / "refactor-budget.sh", r"VERI_REFACTOR_BUDGET \(default [0-9]+"),
        "SKILL.md-refactor": stated(SCRIPTS.parent / "SKILL.md", r"VERI_REFACTOR_BUDGET.{0,3} \(default [0-9]+"),
    }
    disagreeing = ["%s: states %s, in force %s" % (site, figure, sorted(in_force))
                   for site, figure in sites.items() if {figure} != in_force]
    assert disagreeing == []
    assert seen == [
        (0, "refactor 4/5 — another transform may run\n"),
        (3, "refactor 5/5 — budget spent\n"),
    ]


def test_main_with_both_budgets_unset_answers_each_exit_code_its_header_names(monkeypatch, capsys, refactor_budget):
    monkeypatch.delenv("VERI_REFACTOR_BUDGET", raising=False)
    monkeypatch.delenv("VERI_ISSUE_REFACTOR_BUDGET", raising=False)
    seen = []
    for argv in (["0"], ["--issue", "3"], ["ten"]):
        code = refactor_budget.main(argv)
        out, err = capsys.readouterr()
        seen.append((code, out, err))
    assert [code for code, _, _ in seen if code not in range(4)] == []
    assert seen == [
        (0, "refactor 0/5 — another transform may run\n", ""),
        (3, "refactor 3/3 — budget spent\n", ""),
        (2, "", "refactor-budget: <count> must be a whole number >= 0: ten\n"
                "usage: refactor-budget.sh [--issue] <count>\n"),
    ]
