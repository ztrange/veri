"""In-process cases for veri/surround_mutants.py, the module surround-mutants.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def surround_mutants():
    return importlib.import_module("veri.surround_mutants")


DEVELOPER = ("narration\nTEST_PATH: tests/test_parse_cli.py\n"
             "MUTANT: src/parse.py | return tree | return None\n"
             "MUTANT: src/parse.py | if strict: | if not strict:\n"
             "SUITE: GREEN — 4 passed\n")
VERIFIER = "MUTANT: src/parse.py | depth + 1 | depth\nVERDICT: PASS\nREASON: black-box\n"
COMMAND = ["make", "test", "TESTS=tests/test_parse_cli.py"]


def probe(*fields):
    return " ".join(("mutation-probe.sh",) + fields + ("--",) + tuple(COMMAND))


def reports(tmp_path, developer=DEVELOPER, verifier=VERIFIER):
    paths = []
    for name, text in (("develop-surround.out", developer), ("verify-surround.reason", verifier)):
        path = tmp_path / name
        path.write_text(text)
        paths.append(str(path))
    return paths


def test_main_runs_every_mutant_row_of_both_reports_through_mutation_probe_and_prints_one_line_per_row_ending_its_result_4108(
        tmp_path, run_cli, fake_processes, surround_mutants):
    probes = fake_processes.answers({
        probe("src/parse.py", "return tree", "return None"): (0, "", ""),
        probe("src/parse.py", "if strict:", "if not strict:"): (1, "", "suite stayed green under the mutation\n"),
        probe("src/parse.py", "depth + 1", "depth"): (2, "", "file not mutated\n"),
    }, exact=True)

    code, out, _ = run_cli(surround_mutants, [*reports(tmp_path), "--", *COMMAND],
                           env={"VERI_SURROUND_MUTANTS": "1"})

    assert [line.rsplit(" ", 1)[1] for line in out.splitlines()] == ["red", "survived", "no-answer"]
    assert [argv[1:4] for argv in probes.argvs] == [
        ["src/parse.py", "return tree", "return None"], ["src/parse.py", "if strict:", "if not strict:"],
        ["src/parse.py", "depth + 1", "depth"]]
    assert all(argv[4:] == ["--", *COMMAND] for argv in probes.argvs)
    assert out.splitlines()[0].startswith("src/parse.py | return tree | return None")


ALL_RED = {probe("src/parse.py", "return tree", "return None"): (0, "", ""),
           probe("src/parse.py", "if strict:", "if not strict:"): (0, "", ""),
           probe("src/parse.py", "depth + 1", "depth"): (0, "", "")}


def test_main_exits_0_when_every_row_is_red_and_the_table_holds_at_least_veri_surround_mutants_rows_and_1_on_a_survivor_4108(
        tmp_path, run_cli, fake_processes, surround_mutants):
    fake_processes.answers(ALL_RED, exact=True)
    enough = run_cli(surround_mutants, [*reports(tmp_path), "--", *COMMAND], env={"VERI_SURROUND_MUTANTS": "3"})
    fake_processes.answers({**ALL_RED, probe("src/parse.py", "if strict:", "if not strict:"): (1, "", "")}, exact=True)
    survivor = run_cli(surround_mutants, [*reports(tmp_path), "--", *COMMAND], env={"VERI_SURROUND_MUTANTS": "3"})

    assert (enough[0], enough[1].splitlines()[-1].endswith(" red")) == (0, True)
    assert (survivor[0], survivor[1].splitlines()[-1].endswith(" red"),
            "src/parse.py | if strict: | if not strict: survived" in survivor[1].splitlines()) == (1, True, True)


def test_main_exits_1_with_its_last_line_short_k_of_n_when_every_row_is_red_but_too_few_counting_a_repeated_row_once_4108(
        tmp_path, run_cli, fake_processes, surround_mutants, monkeypatch):
    monkeypatch.delenv("VERI_SURROUND_MUTANTS", raising=False)
    fake_processes.answers(ALL_RED, exact=True)
    repeated = VERIFIER + "MUTANT: src/parse.py | return tree | return None\n"

    code, out, err = run_cli(surround_mutants, [*reports(tmp_path, verifier=repeated), "--", *COMMAND])

    assert (code, out.splitlines()[-1], len(out.splitlines()), err) == (1, "short 3 of 5", 4, "")


def test_main_exits_2_for_no_command_an_unreadable_report_a_malformed_mutant_line_or_a_row_the_probe_could_not_answer_4108(
        tmp_path, run_cli, fake_processes, surround_mutants):
    probes = fake_processes.answers(ALL_RED, exact=True)
    developer, verifier = reports(tmp_path)
    malformed = tmp_path / "malformed.out"
    malformed.write_text("MUTANT: src/parse.py | return tree\n")
    blank = tmp_path / "blank.out"
    blank.write_text("MUTANT: src/parse.py |  | return None\n")

    def answer(argv, env=None):
        return run_cli(surround_mutants, argv, env={"VERI_SURROUND_MUTANTS": "1", **(env or {})})

    refusals = {
        "no --": answer([developer, verifier]),
        "nothing after --": answer([developer, verifier, "--"]),
        "no report": answer(["--", *COMMAND]),
        "unreadable report": answer([developer, str(tmp_path / "absent.out"), "--", *COMMAND]),
        "two fields": answer([developer, str(malformed), "--", *COMMAND]),
        "an empty field": answer([developer, str(blank), "--", *COMMAND]),
    }
    started = len(probes.calls)
    fake_processes.answers({**ALL_RED, probe("src/parse.py", "depth + 1", "depth"): (2, "", "file not mutated\n")},
                           exact=True)
    no_answer = answer([developer, verifier, "--", *COMMAND])

    assert {name: (code, out, bool(err)) for name, (code, out, err) in refusals.items()} == {
        name: (2, "", True) for name in refusals}
    assert started == 0
    assert (no_answer[0], no_answer[1].splitlines()[-1], "file not mutated" in no_answer[2]) == (
        2, "src/parse.py | depth + 1 | depth no-answer", True)


@pytest.mark.parametrize("value", ["0", "abc", "1.5", "-3", ""])
def test_main_refuses_a_veri_surround_mutants_that_is_not_a_whole_number_of_at_least_1_with_exit_2_and_one_line_naming_it_4108(
        tmp_path, run_cli, fake_processes, surround_mutants, value):
    probes = fake_processes.answers(ALL_RED, exact=True)
    tunables = importlib.import_module("veri.tunables")

    code, out, err = run_cli(surround_mutants, [*reports(tmp_path), "--", *COMMAND], env={"VERI_SURROUND_MUTANTS": value})

    assert tunables.default("VERI_SURROUND_MUTANTS") == "5"
    assert (code, out, len(err.splitlines()), "VERI_SURROUND_MUTANTS" in err, probes.calls) == (
        (1, "src/parse.py | return tree | return None red\nsrc/parse.py | if strict: | if not strict: red\n"
            "src/parse.py | depth + 1 | depth red\nshort 3 of 5\n", 0, False, probes.calls)
        if value == "" else (2, "", 1, True, []))
