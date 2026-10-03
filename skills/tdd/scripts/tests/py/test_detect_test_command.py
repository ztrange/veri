"""In-process cases for veri/detect_test_command.py, the module detect-test-command.sh is a shim over."""
import importlib
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def detect():
    return importlib.import_module("veri.detect_test_command")


def test_main_returns_0_with_the_command_3_with_nothing_and_1_for_a_valueless_tier_or_issue(tmp_path, capsys, detect):
    made = tmp_path / "made"
    made.mkdir()
    (made / "Makefile").write_text("test:\n\t./run\n")
    bare = tmp_path / "bare"
    bare.mkdir()

    found = (detect.main([str(made)]), capsys.readouterr().out)
    none = (detect.main([str(bare)]), capsys.readouterr().out)
    tier = detect.main(["--tier"])
    issue = detect.main(["--issue"])

    assert (found, none, tier, issue) == ((0, "make test\n"), (3, ""), 1, 1)


def test_main_returns_3_with_nothing_for_a_makefile_without_a_test_target(tmp_path, capsys, detect):
    (tmp_path / "Makefile").write_text("build:\n\tcc main.c\n")

    assert (detect.main([str(tmp_path)]), capsys.readouterr().out) == (3, "")


def test_main_answers_the_issue_bodys_test_command_ahead_of_veri_test_command_and_inference(tmp_path, capsys, detect):
    repo = tmp_path / "repo"
    (repo / ".veri").mkdir(parents=True)
    (repo / ".veri" / "test-command").write_text("./run-tests\n")
    (repo / "Makefile").write_text("test:\n\t./run\n")
    (repo / "go.mod").write_text("module x\n")
    body = tmp_path / "body.md"
    body.write_text("## What to build\n\nA thing.\n\nTest command: make docs-test\n")

    assert (detect.main(["--issue", str(body), str(repo)]), capsys.readouterr().out) == (0, "make docs-test\n")


def test_main_answers_from_the_working_directory_when_the_root_is_empty(tmp_path, capsys, monkeypatch, detect):
    (tmp_path / "Makefile").write_text("test:\n\t./run\n")
    monkeypatch.chdir(tmp_path)

    assert (detect.main([""]), capsys.readouterr().out) == (0, "make test\n")


def test_main_finds_tests_under_a_root_whose_name_holds_glob_characters(tmp_path, capsys, detect):
    root = tmp_path / "r[x]"
    (root / "tests").mkdir(parents=True)
    (root / "tests" / "test_a.py").write_text("")
    (tmp_path / "rx" / "tests").mkdir(parents=True)

    assert (detect.main([str(root)]), capsys.readouterr().out) == (0, "python3 -m unittest discover -q\n")


def test_main_counts_a_makefile_test_assignment_as_a_test_target(tmp_path, capsys, detect):
    (tmp_path / "Makefile").write_text("test := x\n")

    assert (detect.main([str(tmp_path)]), capsys.readouterr().out) == (0, "make test\n")


def test_main_answers_the_issue_bodys_marker_bare_or_backticked_and_falls_through_without_one(tmp_path, capsys, detect):
    def answer(*argv):
        return detect.main(list(argv)), capsys.readouterr().out

    override = tmp_path / "override"
    (override / ".veri").mkdir(parents=True)
    (override / ".veri" / "test-command").write_text("bin/run-suite --all --strict\n")
    (override / "package.json").write_text('{"scripts":{"test":"jest"}}\n')
    inference = tmp_path / "inference"
    inference.mkdir()
    (inference / "Makefile").write_text("test:\n\techo hi\n")
    (inference / "pytest.ini").write_text("")
    none = tmp_path / "none"
    (none / "src").mkdir(parents=True)
    (none / "README.md").write_text("# demo\n\nRun the test suite however you like.\n")
    silent = tmp_path / "silent.md"
    silent.write_text("## Notes\n\nNo line here names the run command; `make docs-test` appears in prose only.\n")
    midline = tmp_path / "midline.md"
    midline.write_text("## Notes\n\n`docs/wt/app.js`, `docs/wt/style.css`. Test command: `make docs-test`. More prose.\n")
    linestart = tmp_path / "linestart.md"
    linestart.write_text("## Notes\n\nTest command: `make docs-test`. `docs/walkthrough.html` is GENERATED — never hand-edit it.\n")
    bare = tmp_path / "bare.md"
    bare.write_text("## Notes\n\nTest command: bin/run --all\n")
    fixtures = SCRIPTS / "tests" / "fixtures" / "detect-test-command"

    untouched = [answer(*flag, str(repo)) for repo in (override, inference, none) for flag in (["--issue", str(silent)], [])]
    stated = [answer("--issue", str(body), str(inference)) for body in (midline, linestart, bare)]
    real = [answer("--issue", str(fixtures / f"issue-{n}.md"), str(inference)) for n in (71, 75, 80, 123)]

    assert (untouched, stated, real) == (
        [(0, "bin/run-suite --all --strict\n")] * 2 + [(0, "make test\n")] * 2 + [(3, "")] * 2,
        [(0, "make docs-test\n"), (0, "make docs-test\n"), (0, "bin/run --all\n")],
        [(0, "make docs-test\n")] * 4,
    )
