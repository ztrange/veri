"""In-process cases for veri/step_budget.py, the module step-budget.sh is a shim over."""
import errno
import importlib
import io
import os
import sys

import pytest


@pytest.fixture
def step_budget():
    return importlib.import_module("veri.step_budget")


def test_main_with_both_budgets_unset_prints_the_defaults_and_refuses_an_argument_with_the_usage_line(monkeypatch, capsys, step_budget):
    monkeypatch.delenv("VERI_STEP_BUDGET", raising=False)
    monkeypatch.delenv("VERI_RUN_BUDGET", raising=False)
    seen = []
    for argv in ([], ["0"]):
        code = step_budget.main(argv)
        out, err = capsys.readouterr()
        seen.append((code, out, err))
    assert [code for code, _, _ in seen if code not in range(4)] == []
    assert seen == [
        (0, "12\n120\n", ""),
        (2, "", "usage: step-budget.sh (takes no arguments)\n"),
    ]


def test_main_checks_the_budgets_echoing_them_as_given_and_refusing_a_bad_one_after_the_arguments(monkeypatch, capsys, step_budget):
    def bad(var, value):
        return "step-budget: %s must be a non-negative decimal number: %s\n" % (var, value)

    usage = "usage: step-budget.sh (takes no arguments)\n"
    cases = [
        ({"VERI_STEP_BUDGET": "7.5", "VERI_RUN_BUDGET": "42.25"}, [], (0, "7.5\n42.25\n", "")),
        ({"VERI_STEP_BUDGET": "0", "VERI_RUN_BUDGET": "007.50"}, [], (0, "0\n007.50\n", "")),
        ({"VERI_RUN_BUDGET": "3"}, [], (0, "12\n3\n", "")),
        ({"VERI_STEP_BUDGET": ""}, [], (2, "", bad("VERI_STEP_BUDGET", ""))),
        ({"VERI_RUN_BUDGET": ""}, [], (2, "", bad("VERI_RUN_BUDGET", ""))),
    ]
    for value in ("twelve", "-5", "1.", ".5", "1e3", " 5", "5\n", "٣"):
        cases.append(({"VERI_STEP_BUDGET": value}, [], (2, "", bad("VERI_STEP_BUDGET", value))))
        cases.append(({"VERI_RUN_BUDGET": value}, [], (2, "", bad("VERI_RUN_BUDGET", value))))
    cases += [
        ({"VERI_STEP_BUDGET": "twelve", "VERI_RUN_BUDGET": "-5"}, [], (2, "", bad("VERI_STEP_BUDGET", "twelve"))),
        ({"VERI_STEP_BUDGET": "x"}, ["extra"], (2, "", usage)),
        ({}, [""], (2, "", usage)),
    ]
    seen = []
    expected = []
    for env, argv, want in cases:
        monkeypatch.delenv("VERI_STEP_BUDGET", raising=False)
        monkeypatch.delenv("VERI_RUN_BUDGET", raising=False)
        for name, value in env.items():
            monkeypatch.setenv(name, value)
        code = step_budget.main(argv)
        out, err = capsys.readouterr()
        seen.append((env, argv, (code, out, err)))
        expected.append((env, argv, want))
    assert seen == expected


def test_main_writes_bytes_whatever_the_locale_and_exits_1_when_stdout_is_closed(monkeypatch, step_budget):
    streams = {"C": ("ascii", "surrogateescape"), "C.UTF-8": ("utf-8", "strict")}
    ff = os.fsdecode(b"\xff")

    def run(locale, env):
        encoding, errors = streams[locale]
        monkeypatch.setenv("LC_ALL", locale)
        monkeypatch.delenv("VERI_STEP_BUDGET", raising=False)
        monkeypatch.delenv("VERI_RUN_BUDGET", raising=False)
        for name, value in env.items():
            monkeypatch.setenv(name, value)
        out, err = io.BytesIO(), io.BytesIO()
        monkeypatch.setattr(sys, "stdout", io.TextIOWrapper(out, encoding=encoding, errors=errors, write_through=True))
        monkeypatch.setattr(sys, "stderr", io.TextIOWrapper(err, encoding=encoding, errors="backslashreplace",
                                                            write_through=True))
        try:
            code = step_budget.main([])
        except Exception:
            code = 1
        sys.stdout.flush()
        sys.stderr.flush()
        return (code, out.getvalue(), err.getvalue())

    seen, wanted = {}, {}
    for locale in streams:
        seen[(locale, "valid")] = run(locale, {"VERI_STEP_BUDGET": "007.50", "VERI_RUN_BUDGET": "42.25"})
        wanted[(locale, "valid")] = (0, b"007.50\n42.25\n", b"")
        seen[(locale, "step")] = run(locale, {"VERI_STEP_BUDGET": ff})
        wanted[(locale, "step")] = (2, b"", b"step-budget: VERI_STEP_BUDGET must be a non-negative decimal number: \xff\n")
        seen[(locale, "run")] = run(locale, {"VERI_RUN_BUDGET": "1" + ff})
        wanted[(locale, "run")] = (2, b"", b"step-budget: VERI_RUN_BUDGET must be a non-negative decimal number: 1\xff\n")
    monkeypatch.delenv("VERI_STEP_BUDGET", raising=False)
    monkeypatch.delenv("VERI_RUN_BUDGET", raising=False)

    def closed(stdout):
        monkeypatch.setattr(sys, "stdout", stdout)
        try:
            return step_budget.main([])
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


def test_main_answers_each_contract_case_of_the_bash_suite_with_its_return_code_and_streams(monkeypatch, capsys, step_budget):
    def bad(var, value):
        return "step-budget: %s must be a non-negative decimal number: %s\n" % (var, value)

    def run(env, argv):
        monkeypatch.delenv("VERI_STEP_BUDGET", raising=False)
        monkeypatch.delenv("VERI_RUN_BUDGET", raising=False)
        for name, value in env.items():
            monkeypatch.setenv(name, value)
        code = step_budget.main(argv)
        out, err = capsys.readouterr()
        return (code, out, err)

    cases = {
        "neither budget set prints 12 then 120, each on its own line, exit 0":
            [({}, [], (0, "12\n120\n", ""))],
        "a set VERI_STEP_BUDGET then a set VERI_RUN_BUDGET, decimals included, printed in that order":
            [({"VERI_STEP_BUDGET": "7.5", "VERI_RUN_BUDGET": "42.25"}, [], (0, "7.5\n42.25\n", ""))],
        "a VERI_STEP_BUDGET that is not a non-negative decimal number exits 2, names it on stderr, prints nothing on stdout":
            [({"VERI_STEP_BUDGET": "twelve"}, [], (2, "", bad("VERI_STEP_BUDGET", "twelve")))],
        "a VERI_RUN_BUDGET that is not a non-negative decimal number exits 2, names it on stderr, prints nothing on stdout":
            [({"VERI_RUN_BUDGET": "-5"}, [], (2, "", bad("VERI_RUN_BUDGET", "-5")))],
        "both budgets invalid at once exits 2 and prints nothing on stdout, not the first figure then a failure":
            [({"VERI_STEP_BUDGET": "twelve", "VERI_RUN_BUDGET": "-5"}, [], (2, "", bad("VERI_STEP_BUDGET", "twelve")))],
        "either budget exported as the empty string exits 2 rather than falling back to its default":
            [({"VERI_STEP_BUDGET": ""}, [], (2, "", bad("VERI_STEP_BUDGET", ""))),
             ({"VERI_RUN_BUDGET": ""}, [], (2, "", bad("VERI_RUN_BUDGET", "")))],
        "a budget of 0 is accepted for either variable and printed back":
            [({"VERI_STEP_BUDGET": "0"}, [], (0, "0\n120\n", "")),
             ({"VERI_RUN_BUDGET": "0"}, [], (0, "12\n0\n", ""))],
        "any argument exits 2":
            [({}, ["0"], (2, "", "usage: step-budget.sh (takes no arguments)\n"))],
    }
    seen = {name: [run(env, argv) for env, argv, _ in runs] for name, runs in cases.items()}
    wanted = {name: [want for _, _, want in runs] for name, runs in cases.items()}
    assert seen == wanted
