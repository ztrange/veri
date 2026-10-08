"""In-process cases for veri/refactor_budget.py, the module refactor-budget.sh is a shim over."""
import errno
import importlib
import io
import os
import re
import sys

import pytest

from conftest import SCRIPTS


@pytest.fixture
def refactor_budget():
    return importlib.import_module("veri.refactor_budget")


def budgets(monkeypatch, env):
    monkeypatch.delenv("VERI_REFACTOR_BUDGET", raising=False)
    monkeypatch.delenv("VERI_ISSUE_REFACTOR_BUDGET", raising=False)
    for name, value in env.items():
        monkeypatch.setenv(name, value)


def stated(path, pattern):
    hit = re.search(pattern, path.read_text().replace("\n", " "))
    return re.findall(r"[0-9]+", hit.group(0))[-1] if hit else "<none>"


def test_main_with_both_budgets_unset_answers_against_the_default_every_prose_statement_of_it_names(monkeypatch, capsys, refactor_budget):
    budgets(monkeypatch, {})
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
    budgets(monkeypatch, {})
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


def test_main_checks_only_the_budget_in_force_before_the_count_and_refuses_what_bash_refuses(monkeypatch, capsys, refactor_budget):
    usage = "usage: refactor-budget.sh [--issue] <count>\n"

    def run(env, argv):
        budgets(monkeypatch, env)
        try:
            code = refactor_budget.main(argv)
        except Exception as error:
            code = repr(error)
        out, err = capsys.readouterr()
        return (code, out, err)

    bad = ["two", "-1", "1.5", "5\n", "٣"]
    seen, wanted = [], []
    for value in bad:
        for argv, var in ((["1"], "VERI_REFACTOR_BUDGET"), (["--issue", "1"], "VERI_ISSUE_REFACTOR_BUDGET")):
            refusal = (2, "", f"refactor-budget: {var} must be a whole number >= 0: {value}\n")
            seen.append(run({var: value}, argv))
            wanted.append(refusal)
            seen.append(run({var: value}, argv[:-1] + ["ten"]))
            wanted.append(refusal)
        seen.append(run({"VERI_REFACTOR_BUDGET": value}, ["--issue", "1"]))
        wanted.append((0, "refactor 1/3 — another transform may run\n", ""))
        seen.append(run({"VERI_ISSUE_REFACTOR_BUDGET": value}, ["1"]))
        wanted.append((0, "refactor 1/5 — another transform may run\n", ""))
    seen.append(run({"VERI_REFACTOR_BUDGET": ""}, ["1"]))
    wanted.append((0, "refactor 1/5 — another transform may run\n", ""))
    seen.append(run({"VERI_ISSUE_REFACTOR_BUDGET": ""}, ["--issue", "1"]))
    wanted.append((0, "refactor 1/3 — another transform may run\n", ""))
    for count in ("ten", "5\n", "٣"):
        seen.append(run({}, [count]))
        wanted.append((2, "", f"refactor-budget: <count> must be a whole number >= 0: {count}\n" + usage))
    seen.append(run({}, []))
    wanted.append((2, "", "refactor-budget: <count> must be a whole number >= 0: \n" + usage))
    assert seen == wanted


def test_main_reads_its_arguments_by_position_and_leading_zeros_and_counts_past_2_63_as_decimal_issue_776(monkeypatch, capsys, refactor_budget):
    usage = "usage: refactor-budget.sh [--issue] <count>\n"

    def run(env, argv):
        budgets(monkeypatch, env)
        code = refactor_budget.main(argv)
        out, err = capsys.readouterr()
        return (code, out, err)

    seen = [
        run({}, ["1", "--issue"]),
        run({}, ["--issue", "--issue", "1"]),
        run({"VERI_REFACTOR_BUDGET": "010"}, ["9"]),
        run({"VERI_ISSUE_REFACTOR_BUDGET": "010"}, ["--issue", "9"]),
        run({}, ["08"]),
        run({"VERI_REFACTOR_BUDGET": "08"}, ["1"]),
        run({"VERI_REFACTOR_BUDGET": "08"}, ["8"]),
        run({}, ["9223372036854775808"]),
        run({}, ["27670116110564327424"]),
        run({"VERI_REFACTOR_BUDGET": "09"}, ["08"]),
        run({}, ["007"]),
    ]
    assert seen == [
        (0, "refactor 1/5 — another transform may run\n", ""),
        (2, "", "refactor-budget: <count> must be a whole number >= 0: --issue\n" + usage),
        (0, "refactor 9/010 — another transform may run\n", ""),
        (0, "refactor 9/010 — another transform may run\n", ""),
        (3, "refactor 08/5 — budget spent\n", ""),
        (0, "refactor 1/08 — another transform may run\n", ""),
        (3, "refactor 8/08 — budget spent\n", ""),
        (3, "refactor 9223372036854775808/5 — budget spent\n", ""),
        (3, "refactor 27670116110564327424/5 — budget spent\n", ""),
        (0, "refactor 08/09 — another transform may run\n", ""),
        (3, "refactor 007/5 — budget spent\n", ""),
    ]


def test_main_writes_bytes_whatever_the_locale_and_exits_1_when_stdout_is_closed(monkeypatch, refactor_budget):
    streams = {"C": ("ascii", "surrogateescape"), "C.UTF-8": ("utf-8", "strict")}
    ff = os.fsdecode(b"\xff")

    def run(locale, env, argv):
        encoding, errors = streams[locale]
        monkeypatch.setenv("LC_ALL", locale)
        budgets(monkeypatch, env)
        out, err = io.BytesIO(), io.BytesIO()
        monkeypatch.setattr(sys, "stdout", io.TextIOWrapper(out, encoding=encoding, errors=errors, write_through=True))
        monkeypatch.setattr(sys, "stderr", io.TextIOWrapper(err, encoding=encoding, errors="backslashreplace",
                                                            write_through=True))
        try:
            code = refactor_budget.main(argv)
        except Exception:
            code = 1
        sys.stdout.flush()
        sys.stderr.flush()
        return (code, out.getvalue(), err.getvalue())

    seen, wanted = {}, {}
    for locale in streams:
        seen[(locale, "status")] = run(locale, {}, ["4"])
        wanted[(locale, "status")] = (0, b"refactor 4/5 \xe2\x80\x94 another transform may run\n", b"")
        seen[(locale, "count")] = run(locale, {}, [ff])
        wanted[(locale, "count")] = (2, b"", b"refactor-budget: <count> must be a whole number >= 0: \xff\n"
                                             b"usage: refactor-budget.sh [--issue] <count>\n")
        seen[(locale, "budget")] = run(locale, {"VERI_REFACTOR_BUDGET": ff}, ["1"])
        wanted[(locale, "budget")] = (2, b"", b"refactor-budget: VERI_REFACTOR_BUDGET must be a whole number >= 0: \xff\n")
    monkeypatch.delenv("VERI_REFACTOR_BUDGET", raising=False)

    def closed(stdout):
        monkeypatch.setattr(sys, "stdout", stdout)
        try:
            return refactor_budget.main(["4"])
        except Exception:
            return 1

    seen["closed"] = closed(None)
    wanted["closed"] = 1

    class ClosedFd(io.RawIOBase):
        closed_now = True

        def writable(self):
            return True

        def write(self, data):
            if self.closed_now:
                raise OSError(errno.EBADF, "Bad file descriptor")
            return len(data)

    fd = ClosedFd()
    seen["closed-fd"] = closed(io.TextIOWrapper(io.BufferedWriter(fd)))
    fd.closed_now = False
    wanted["closed-fd"] = 1
    assert seen == wanted


def test_main_answers_each_contract_case_the_bash_suite_ran_through_the_entry_point(monkeypatch, capsys, refactor_budget):
    problems = []

    def run(label, env, argv, code=None, out=None, err=None):
        budgets(monkeypatch, env)
        got_code = refactor_budget.main(argv)
        got_out, got_err = capsys.readouterr()
        if code is not None and got_code != code:
            problems.append(f"{label}: want exit {code}, got {got_code}")
        if out == "one-line" and (got_out == "" or got_out.count("\n") != 1 or not got_out.endswith("\n")):
            problems.append(f"{label}: want a one-line status on stdout, got {got_out!r}")
        elif out == "" and got_out != "":
            problems.append(f"{label}: want no status on stdout, got {got_out!r}")
        elif out not in (None, "one-line", "") and not got_out.startswith(out + " "):
            problems.append(f"{label}: want a status starting {out + ' '!r}, got {got_out!r}")
        if err == "some" and got_err == "":
            problems.append(f"{label}: want a diagnostic on stderr, got nothing")
        elif err == "" and got_err != "":
            problems.append(f"{label}: want nothing on stderr, got {got_err!r}")
        elif err not in (None, "some", "") and err + " " not in got_err:
            problems.append(f"{label}: want stderr naming {err!r}, got {got_err!r}")

    for count, code in (("0", 0), ("4", 0), ("5", 3)):
        run(f"default count {count}", {}, [count], code=code, out="one-line", err="")
    run("VERI_REFACTOR_BUDGET=0 count 0", {"VERI_REFACTOR_BUDGET": "0"}, ["0"], code=3)
    for bad in ("two", "-1"):
        run(f"VERI_REFACTOR_BUDGET={bad}", {"VERI_REFACTOR_BUDGET": bad}, ["0"], code=2, out="", err="some")
    for label, argv in (("count abc", ["abc"]), ("count -1", ["-1"]), ("no argument", []), ("count 1.5", ["1.5"])):
        run(label, {}, argv, code=2, out="", err="some")
    for label, env, argv, code, err in (
        ("--issue default count 0", {"VERI_REFACTOR_BUDGET": "0"}, ["--issue", "0"], 0, None),
        ("--issue default count 1", {"VERI_REFACTOR_BUDGET": "0"}, ["--issue", "1"], 0, None),
        ("--issue default count 2", {"VERI_REFACTOR_BUDGET": "0"}, ["--issue", "2"], 0, None),
        ("--issue default count 3", {"VERI_REFACTOR_BUDGET": "0"}, ["--issue", "3"], 3, None),
        ("--issue VERI_ISSUE_REFACTOR_BUDGET=10 count 9",
         {"VERI_REFACTOR_BUDGET": "0", "VERI_ISSUE_REFACTOR_BUDGET": "10"}, ["--issue", "9"], 0, None),
        ("--issue VERI_ISSUE_REFACTOR_BUDGET=10 count 10",
         {"VERI_REFACTOR_BUDGET": "0", "VERI_ISSUE_REFACTOR_BUDGET": "10"}, ["--issue", "10"], 3, None),
        ("--issue VERI_ISSUE_REFACTOR_BUDGET=two", {"VERI_ISSUE_REFACTOR_BUDGET": "two"}, ["--issue", "0"], 2,
         "VERI_ISSUE_REFACTOR_BUDGET"),
        ("--issue VERI_ISSUE_REFACTOR_BUDGET=-1", {"VERI_ISSUE_REFACTOR_BUDGET": "-1"}, ["--issue", "0"], 2,
         "VERI_ISSUE_REFACTOR_BUDGET"),
        ("no flag VERI_REFACTOR_BUDGET=2 count 2",
         {"VERI_REFACTOR_BUDGET": "2", "VERI_ISSUE_REFACTOR_BUDGET": "20"}, ["2"], 3, None),
    ):
        run(label, env, argv, code=code, err=err)
    for label, env, argv, code, out in (
        ("--issue VERI_ISSUE_REFACTOR_BUDGET=two", {"VERI_ISSUE_REFACTOR_BUDGET": "two"}, ["--issue", "0"], 2, ""),
        ("--issue VERI_ISSUE_REFACTOR_BUDGET=-1", {"VERI_ISSUE_REFACTOR_BUDGET": "-1"}, ["--issue", "0"], 2, ""),
        ("--issue VERI_ISSUE_REFACTOR_BUDGET=1.5", {"VERI_ISSUE_REFACTOR_BUDGET": "1.5"}, ["--issue", "0"], 2, ""),
        ("--issue VERI_ISSUE_REFACTOR_BUDGET=10 count 9", {"VERI_ISSUE_REFACTOR_BUDGET": "10"}, ["--issue", "9"], 0,
         "refactor 9/10"),
        ("--issue VERI_ISSUE_REFACTOR_BUDGET=10 count 10", {"VERI_ISSUE_REFACTOR_BUDGET": "10"}, ["--issue", "10"], 3,
         "refactor 10/10"),
        ("no flag, VERI_REFACTOR_BUDGET unset, count 4", {"VERI_ISSUE_REFACTOR_BUDGET": "3"}, ["4"], 0, "refactor 4/5"),
        ("no flag, VERI_REFACTOR_BUDGET unset, count 5", {"VERI_ISSUE_REFACTOR_BUDGET": "3"}, ["5"], 3, "refactor 5/5"),
    ):
        run(label, env, argv, code=code, out=out)
    assert problems == []
