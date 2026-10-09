"""The search-path setup conftest.py gives every suite under tests/py, read by a suite with none of its own."""
import importlib
import pathlib
import subprocess
from sys import path as search_path


def test_a_suite_with_no_path_setup_reads_scripts_from_conftest_and_imports_veri_and_script_modules():
    conftest = importlib.import_module("conftest")
    scripts = pathlib.Path(__file__).resolve().parents[2]
    entries = [str(scripts), str(scripts / "veri")]

    assert conftest.SCRIPTS == scripts
    assert [search_path.count(entry) for entry in entries] == [1, 1]
    assert sorted(search_path[:2]) == sorted(entries)
    assert importlib.import_module("ledger").__file__ == str(scripts / "veri" / "ledger.py")
    assert importlib.import_module("veri.ledger").__file__ == str(scripts / "veri" / "ledger.py")


def test_fake_processes_given_no_answer_records_every_entry_point_by_basename_and_answers_0_with_empty_output_starting_no_process(
        fake_processes, tmp_path):
    calls = fake_processes()
    entries = ("run", "Popen", "call", "check_call", "check_output")

    answers = [getattr(subprocess, entry)(["/usr/bin/touch", str(tmp_path / entry)]) for entry in entries]

    assert calls == ["touch %s" % (tmp_path / entry) for entry in entries]
    assert [(answer.returncode, answer.stdout, answer.stderr) for answer in answers] == [(0, "", "")] * len(entries)
    assert sorted(tmp_path.iterdir()) == []


def test_fake_processes_given_an_answer_hands_run_the_line_and_its_keyword_arguments_and_refuses_every_other_entry_point_naming_the_command(
        fake_processes, tmp_path):
    asked = []

    def answer(line, **kwargs):
        asked.append((line, kwargs))
        return 3, "out", "err"

    calls = fake_processes(answer)

    ran = subprocess.run(["/usr/bin/touch", str(tmp_path / "run")], capture_output=True, text=True)

    assert asked == [("touch %s" % (tmp_path / "run"), {"capture_output": True, "text": True})]
    assert (ran.returncode, ran.stdout, ran.stderr) == (3, "out", "err")
    for entry in ("Popen", "call", "check_call", "check_output"):
        line = "touch %s" % (tmp_path / entry)
        try:
            getattr(subprocess, entry)(["/usr/bin/touch", str(tmp_path / entry)])
        except AssertionError as refused:
            assert line in str(refused), entry
        else:
            raise AssertionError("%s answered rather than refusing" % entry)
    assert calls[0] == "touch %s" % (tmp_path / "run")
    assert sorted(tmp_path.iterdir()) == []
