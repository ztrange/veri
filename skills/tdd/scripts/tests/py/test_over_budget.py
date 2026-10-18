"""In-process cases for veri/over_budget.py, the module over-budget.sh is a shim over."""
import importlib
import sys

import pytest


@pytest.fixture
def over_budget():
    return importlib.import_module("veri.over_budget")


def _tunables(monkeypatch, budget, ratio):
    monkeypatch.setenv("VERI_UNIT_BUDGET", budget)
    monkeypatch.setenv("VERI_TIME_WARN_RATIO", ratio)


def test_main_refuses_a_missing_argument_with_2_and_answers_0_1_or_2_from_the_tunables(capsys, monkeypatch, over_budget):
    _tunables(monkeypatch, "10", "1.5")
    for argv in ([], ["unit"], ["unit", "10"], ["unit", "10", ""]):
        code = over_budget.main(argv)
        out, err = capsys.readouterr()
        assert (argv, code, out, err) == (argv, 2, "", "usage: over-budget.sh <tier> <seconds> <usual>\n")

    code = over_budget.main(["unit", "12", "100"])
    out, _ = capsys.readouterr()
    assert (code, out) == (0, "⏱ unit tier took 12 s (usual 100 s, ratio 1.5, unit budget 10 s)\n")

    code = over_budget.main(["unit", "4", "100"])
    out, _ = capsys.readouterr()
    assert (code, out) == (1, "")

    _tunables(monkeypatch, "ten", "1.5")
    code = over_budget.main(["unit", "12", "100"])
    out, _ = capsys.readouterr()
    assert (code, out) == (2, "")

    _tunables(monkeypatch, "10", "x")
    code = over_budget.main(["unit", "12", "100"])
    out, _ = capsys.readouterr()
    assert (code, out) == (2, "")


def test_main_ignores_extra_arguments_and_prints_the_budget_and_ratio_the_environment_sets(capsys, monkeypatch, over_budget):
    _tunables(monkeypatch, "1000", "1.5")

    code = over_budget.main(["all", "160", "100", "extra"])
    out, _ = capsys.readouterr()
    assert (code, out) == (0, "⏱ all tier took 160 s (usual 100 s, ratio 1.5, unit budget 1000 s)\n")

    code = over_budget.main(["unit", "12", "100", "extra"])
    out, _ = capsys.readouterr()
    assert (code, out) == (1, "")


def test_main_compares_strictly_matches_the_tier_exactly_multiplies_as_doubles_and_prints_each_value_as_given(capsys, monkeypatch, over_budget):
    _tunables(monkeypatch, "10", "1.5")
    for argv in (["unit", "10", "100"], ["all", "150", "100"], ["Unit", "12", "100"], ["all", "0.15", "0.1"]):
        code = over_budget.main(argv)
        out, _ = capsys.readouterr()
        assert (argv, code, out) == (argv, 1, "")

    _tunables(monkeypatch, "10.0", "1.50")
    code = over_budget.main(["unit", "12.0", "100"])
    out, _ = capsys.readouterr()
    assert (code, out) == (0, "⏱ unit tier took 12.0 s (usual 100 s, ratio 1.50, unit budget 10.0 s)\n")


def test_main_reads_what_macos_awk_reads_as_a_number_as_a_number(capsys, monkeypatch, over_budget):
    _tunables(monkeypatch, "10", "0.5")
    for seconds in (" 12", "+200", ".5e3", "200.", "2e2", "inf", "0x1A"):
        code = over_budget.main(["all", seconds, "20"])
        capsys.readouterr()
        assert (seconds, code) == (seconds, 0)
    for argv in (["all", "nan", "1"], ["all", "-inf", "-1"]):
        code = over_budget.main(argv)
        capsys.readouterr()
        assert (argv, code) == (argv, 1)


def test_main_keeps_a_number_with_the_whitespace_macos_awk_skips_and_reads_a_trailing_formfeed_or_vtab_as_a_string(capsys, monkeypatch, over_budget):
    _tunables(monkeypatch, "10", "0.5")
    for seconds in ("\f1000", "\v1000", "\r1000", "1000 ", "1000\t", "1000\r"):
        code = over_budget.main(["all", seconds, "1000"])
        capsys.readouterr()
        assert (seconds, code) == (seconds, 0)
    for seconds in ("1000\f", "1000\v"):
        code = over_budget.main(["all", seconds, "1000"])
        capsys.readouterr()
        assert (seconds, code) == (seconds, 1)


def test_main_compares_seconds_awk_reads_as_a_string_as_text_against_the_budget_and_the_product_in_percent_6g(capsys, monkeypatch, over_budget):
    _tunables(monkeypatch, "10", "3")
    for argv, expected in ((["unit", "abc", "50"], 0), (["all", "160s", "50"], 0), (["all", "1000s", "50"], 1),
                           (["all", "1e", "500"], 0), (["all", "1_000", "500"], 0),
                           (["unit", "12x", "50"], 0), (["all", "12x", "50"], 1),
                           (["all", "1.6x", "500000.5"], 0), (["all", "1.6x", "500000"], 1),
                           (["all", "NaN", "50"], 1), (["all", "-Infinity", "-50"], 1),
                           (["all", "abc", "inf"], 1), (["all", "j", "inf"], 0),
                           (["all", "abc", "nan"], 1), (["all", "o", "nan"], 0)):
        code = over_budget.main(argv)
        capsys.readouterr()
        assert (argv, code) == (argv, expected)


def test_main_reads_a_usual_awk_reads_as_a_string_as_zero_inside_the_product(capsys, monkeypatch, over_budget):
    _tunables(monkeypatch, "20", "3")
    for argv, expected, line in ((["all", "160", "abc"], 0, "⏱ all tier took 160 s (usual abc s, ratio 3, unit budget 20 s)\n"),
                                 (["all", "0", "abc"], 1, "")):
        code = over_budget.main(argv)
        out, _ = capsys.readouterr()
        assert (argv, code, out) == (argv, expected, line)


def test_main_reads_a_dot_as_the_decimal_separator_whatever_lc_all_says(capsys, monkeypatch, over_budget):
    _tunables(monkeypatch, "10", "3")
    for locale in ("de_DE.UTF-8", "C"):
        monkeypatch.setenv("LC_ALL", locale)
        code = over_budget.main(["all", "1,6", "0.5"])
        out, _ = capsys.readouterr()
        assert (locale, code, out) == (locale, 1, "")


def test_main_compares_as_macos_awk_does_not_as_python_float_does(capsys, monkeypatch, over_budget):
    _tunables(monkeypatch, "10", "3")
    cases = [(["all", seconds, "0.5"], 0) for seconds in (" 12", "+200", ".5e3", "200.", "2e2", "inf", "0x1A")]
    cases += [(["all", "nan", "0.5"], 1), (["unit", "abc", "50"], 0), (["all", "160s", "50"], 0),
              (["all", "1000s", "50"], 1), (["all", "1e", "500"], 0), (["all", "1_000", "500"], 0),
              (["all", "160", "abc"], 0)]
    for locale in ("C", "de_DE.UTF-8"):
        monkeypatch.setenv("LC_ALL", locale)
        for argv, expected in cases + [(["all", "1,6", "0.5"], 1)]:
            code = over_budget.main(argv)
            capsys.readouterr()
            assert (locale, argv, code) == (locale, argv, expected)


def test_main_processes_backslash_escapes_in_every_value_as_awk_v_does(capsys, monkeypatch, over_budget):
    _tunables(monkeypatch, "11", "3")
    for argv, line in ((["x\\ny", "160", "50"], "⏱ x\ny tier took 160 s (usual 50 s, ratio 3, unit budget 11 s)\n"),
                       (["x\\\\y", "160", "50"], "⏱ x\\y tier took 160 s (usual 50 s, ratio 3, unit budget 11 s)\n"),
                       (["q\\", "160", "50"], "⏱ q\\ tier took 160 s (usual 50 s, ratio 3, unit budget 11 s)\n"),
                       (["unit", "12\\n", "50"], "⏱ unit tier took 12\n s (usual 50 s, ratio 3, unit budget 11 s)\n")):
        code = over_budget.main(argv)
        out, _ = capsys.readouterr()
        assert (argv, code, out) == (argv, 0, line)


def test_main_processes_awk_v_s_whole_escape_table_not_only_backslash_and_n(capsys, monkeypatch, over_budget):
    _tunables(monkeypatch, "11", "3")
    for tier, printed in (("x\\ty", "x\ty"), ("x\\\"y", "x\"y"), ("x\\ry", "x\ry"), ("x\\by", "x\by"),
                          ("x\\fy", "x\fy"), ("x\\vy", "x\vy"), ("x\\ay", "x\ay"), ("x\\/y", "x/y"),
                          ("x\\101y", "xAy"), ("x\\7y", "x\ay"), ("x\\0123", "x\n3")):
        code = over_budget.main([tier, "160", "50"])
        out, _ = capsys.readouterr()
        assert (tier, code, out) == (tier, 0, "⏱ %s tier took 160 s (usual 50 s, ratio 3, unit budget 11 s)\n" % printed)


def test_main_with_stdout_closed_returns_2_with_one_line_on_stderr_when_over_and_1_with_nothing_when_not(capsys, monkeypatch, over_budget):
    _tunables(monkeypatch, "9", "1.5")
    monkeypatch.setattr(sys, "stdout", None)

    code = over_budget.main(["unit", "10", "100"])
    err = capsys.readouterr().err
    assert (code, err.count("\n"), err.endswith("\n"), err.strip() != "") == (2, 1, True, True)

    code = over_budget.main(["unit", "4", "100"])
    err = capsys.readouterr().err
    assert (code, err) == (1, "")


def test_main_answers_in_full_under_the_tunables_when_any_start_of_time_budget_sh_is_refused(capsys, monkeypatch, over_budget):
    import os
    import subprocess

    def refuse(*args, **kwargs):
        raise OSError("refused: a process start at the boundary")

    monkeypatch.setattr(subprocess, "Popen", refuse)
    monkeypatch.setattr(os, "system", refuse)
    monkeypatch.setattr(os, "posix_spawn", refuse)
    monkeypatch.setattr(os, "fork", refuse)

    _tunables(monkeypatch, "10", "1.5")
    code = over_budget.main(["unit", "12", "100"])
    out, err = capsys.readouterr()
    assert (code, out, err) == (0, "⏱ unit tier took 12 s (usual 100 s, ratio 1.5, unit budget 10 s)\n", "")

    code = over_budget.main(["unit", "4", "100"])
    out, err = capsys.readouterr()
    assert (code, out, err) == (1, "", "")

    _tunables(monkeypatch, "ten", "1.5")
    code = over_budget.main(["unit", "12", "100"])
    out, err = capsys.readouterr()
    assert (code, out, err) == (2, "", "time-budget: VERI_UNIT_BUDGET must be a number of seconds: ten\n")

    _tunables(monkeypatch, "10", "x")
    code = over_budget.main(["unit", "12", "100"])
    out, err = capsys.readouterr()
    assert (code, out, err) == (2, "", "time-budget: VERI_TIME_WARN_RATIO must be a number: x\n")


def test_cli_prints_one_clock_line_for_an_over_budget_run_and_nothing_for_one_that_is_not_and_skill_md_says_to_paste_it_and_branch_on_nothing(run_cli, over_budget):
    import pathlib
    import re

    env = {"VERI_UNIT_BUDGET": "10", "VERI_TIME_WARN_RATIO": "1.5"}
    code, out, err = run_cli(over_budget, ["unit", "12", "100"], env=env)
    assert (code, out.count("\n"), "⏱" in out, err) == (0, 1, True, "")
    assert run_cli(over_budget, ["unit", "4", "100"], env=env) == (1, "", "")

    skill = pathlib.Path(__file__).resolve().parents[3] / "SCRIPTS.md"
    blocks, block = [], ""
    for line in skill.read_text(encoding="utf-8").split("\n") + [""]:
        if re.match(r"[-*] ", line) or not line.strip():
            blocks.append(block)
            block = ""
        block += " " + line
    instruction = " ".join(b for b in blocks if "over-budget.sh" in b).replace("*", "").replace("`", "").lower()
    assert instruction.strip(), "SKILL.md never names over-budget.sh"
    assert "⏱" in instruction
    assert re.search(r"narrat|issue thread|comment", instruction)
    assert re.search(r"(never|not|nothing|no)[^.]{0,80}(branch|gate|verdict|outcome|bail|retr)", instruction)


def _unset_tunables(monkeypatch):
    for name in ("VERI_UNIT_BUDGET", "VERI_TIME_WARN_RATIO"):
        monkeypatch.delenv(name, raising=False)


def _exit_codes(monkeypatch, run_cli, over_budget, runs):
    codes = []
    for argv, env in runs:
        _unset_tunables(monkeypatch)
        codes.append((argv, env, run_cli(over_budget, argv, env=env)[0]))
    return codes


def test_cli_reads_a_unit_tier_run_over_veri_unit_budget_as_over_budget_and_at_or_under_it_as_not(
        monkeypatch, run_cli, over_budget, fake_processes):
    calls = fake_processes()
    answers = _exit_codes(monkeypatch, run_cli, over_budget, (
        (["unit", "12", "100"], {}), (["unit", "10", "100"], {}), (["unit", "4", "100"], {}),
        (["unit", "4", "100"], {"VERI_UNIT_BUDGET": "3"})))
    assert answers == [(["unit", "12", "100"], {}, 0), (["unit", "10", "100"], {}, 1),
                       (["unit", "4", "100"], {}, 1), (["unit", "4", "100"], {"VERI_UNIT_BUDGET": "3"}, 0)]
    assert calls == []


def test_cli_reads_a_run_over_veri_time_warn_ratio_times_its_usual_as_over_budget_and_at_or_under_it_as_not(
        monkeypatch, run_cli, over_budget, fake_processes):
    calls = fake_processes()
    answers = _exit_codes(monkeypatch, run_cli, over_budget, (
        (["all", "160", "100"], {}), (["all", "150", "100"], {}), (["all", "100", "100"], {}),
        (["all", "160", "100"], {"VERI_TIME_WARN_RATIO": "2"}), (["unit", "8", "4"], {})))
    assert answers == [(["all", "160", "100"], {}, 0), (["all", "150", "100"], {}, 1),
                       (["all", "100", "100"], {}, 1), (["all", "160", "100"], {"VERI_TIME_WARN_RATIO": "2"}, 1),
                       (["unit", "8", "4"], {}, 0)]
    assert calls == []


def test_cli_ends_an_over_budget_run_on_its_leafs_own_verdict_with_no_retry_and_no_bail(
        monkeypatch, tmp_path, run_cli, over_budget, fake_processes, events):
    import json

    tier_usual = importlib.import_module("veri.tier_usual")
    verify = importlib.import_module("veri.verify")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(
        json.dumps({"ts": 1, "issue": "342", "actor": "", "phase": "", "step": "", "event": "test-run",
                    "attempt": "1", "skill_commit": "", "tier": "unit", "suites": "make unit",
                    "seconds": seconds}) + "\n" for seconds in ["1"] * 10 + ["40"]))
    (tmp_path / "spec.md").write_text("slugify must lowercase the title and join words with hyphens.\n")
    for name in ("VERI_MODEL", "VERI_MODEL_VERIFIER", "VERI_MODEL_DEVELOPER", "VERIFY_LEAF_ARGS"):
        monkeypatch.delenv(name, raising=False)
    _unset_tunables(monkeypatch)

    def answer(line, **_):
        if line.startswith("supervise.sh "):
            return 0, b"VERDICT: PASS\nREASON: the new case fails for the reason the step names.\n", b""
        return 0, b"", b""

    calls = fake_processes(answer)
    code, usual, _ = run_cli(tier_usual, ["unit"], cwd=tmp_path)
    assert code == 0
    assert run_cli(over_budget, ["unit", "40", usual.strip()], cwd=tmp_path)[0] == 0
    before = len(events.records(tmp_path))

    env = {"HOME": str(tmp_path), "VERI_NO_VERDICT_RETRIES": "0"}
    code, out, _ = run_cli(verify, ["red", str(tmp_path / "spec.md"), "tests/test_slugify.py", "test_lowercases"],
                           env=env, cwd=tmp_path)
    after = events.records(tmp_path)[before:]

    assert (code, "the reason the step names" in out) == (0, True)
    assert [(e["event"], e.get("verdict")) for e in after if e["event"] in ("verdict", "relaunch", "bail")] == [
        ("verdict", "PASS")]
    assert len([line for line in calls if line.startswith("supervise.sh ")]) == 1


def test_cli_refuses_a_missing_argument_with_the_usage_line_and_a_refused_tunable_with_2_and_nothing_on_stdout(
        monkeypatch, run_cli, over_budget, fake_processes):
    calls = fake_processes()
    _unset_tunables(monkeypatch)
    usage = "usage: over-budget.sh <tier> <seconds> <usual>\n"
    assert run_cli(over_budget, []) == (2, "", usage)
    assert run_cli(over_budget, ["unit", "10"]) == (2, "", usage)
    assert run_cli(over_budget, ["unit", "12", "100"], env={"VERI_UNIT_BUDGET": "x"}) == (
        2, "", "time-budget: VERI_UNIT_BUDGET must be a number of seconds: x\n")
    assert calls == []


@pytest.mark.process("over-budget.sh's shim run through a symlink to the skill directory from another working directory")
def test_shim_run_through_a_symlink_to_the_skill_directory_from_another_cwd_answers_as_in_place(tmp_path):
    import os
    import pathlib
    import subprocess

    skill = pathlib.Path(__file__).resolve().parents[3]
    (tmp_path / "link").mkdir()
    (tmp_path / "link" / "skill").symlink_to(skill, target_is_directory=True)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    env = {k: v for k, v in os.environ.items() if k not in ("VERI_UNIT_BUDGET", "VERI_TIME_WARN_RATIO")}

    def answer(script, cwd, argv):
        ran = subprocess.run([str(script), *argv], cwd=cwd, env=env, capture_output=True, text=True)
        return ran.returncode, ran.stdout

    for argv, want in ((["unit", "12", "100"], 0), (["unit", "4", "100"], 1)):
        in_place = answer(skill / "scripts" / "over-budget.sh", None, argv)
        via_link = answer(tmp_path / "link" / "skill" / "scripts" / "over-budget.sh", elsewhere, argv)
        assert (argv, via_link) == (argv, in_place)
        assert (argv, via_link[0], ("⏱" in via_link[1]) if want == 0 else via_link[1]) == (
            argv, want, True if want == 0 else "")
