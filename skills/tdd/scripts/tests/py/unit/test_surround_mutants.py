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
