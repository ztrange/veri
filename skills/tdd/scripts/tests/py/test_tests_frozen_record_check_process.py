"""Cases for tests-frozen.sh that start the real entry point against files on disk."""
import hashlib
import re
import subprocess

import pytest

from conftest import SCRIPTS

FROZEN = SCRIPTS / "tests-frozen.sh"


def frozen(work, *args):
    ran = subprocess.run([str(FROZEN), *args], cwd=work, capture_output=True, text=True)
    return ran.returncode, ran.stdout, ran.stderr


@pytest.fixture
def work(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/a.test.sh").write_text("assert one\n")
    (tmp_path / "tests/b.test.sh").write_text("assert two\n")
    return tmp_path


@pytest.mark.process("tests-frozen.sh run against files on disk")
def test_tests_frozen_record_then_check_on_unchanged_files_exit_0_with_nothing_on_stdout(work):
    rec = work / "record"

    assert frozen(work, "record", str(rec), "tests/a.test.sh", "tests/b.test.sh")[0] == 0
    code, out, _ = frozen(work, "check", str(rec))

    assert (code, out) == (0, "")


@pytest.mark.process("tests-frozen.sh run against files on disk")
def test_tests_frozen_check_names_the_edited_and_the_deleted_recorded_file_one_per_line_exit_1(work):
    (work / "tests/c.test.sh").write_text("assert three\n")
    rec = work / "record3"
    frozen(work, "record", str(rec), "tests/a.test.sh", "tests/b.test.sh", "tests/c.test.sh")
    (work / "tests/a.test.sh").write_text("assert one, weakened\n")
    (work / "tests/b.test.sh").unlink()

    code, out, _ = frozen(work, "check", str(rec))

    assert code == 1
    assert out.splitlines() == ["tests/a.test.sh", "tests/b.test.sh"]


@pytest.mark.process("tests-frozen.sh run against files on disk")
@pytest.mark.parametrize("state, why", [("missing", "missing"), ("empty", "malformed"), ("malformed", "malformed")])
def test_tests_frozen_check_on_a_missing_empty_or_malformed_record_exit_2_one_stderr_line_naming_record_and_why(work, state, why):
    rec = work / "record"
    if state == "empty":
        rec.write_text("")
    elif state == "malformed":
        rec.write_text("not a digest line\n")

    code, out, err = frozen(work, "check", str(rec))

    assert code == 2
    assert out == ""
    assert str(rec) in err
    assert why in err
    assert len(err.strip().splitlines()) == 1


def _git(repo, *argv):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *argv], cwd=repo, check=True,
                   capture_output=True)


@pytest.mark.process("tests-frozen.sh and a real git repository under tmp_path")
def test_rerecord_refactored_rewrites_the_record_of_a_step_whose_ledger_line_is_refactor_pending_2808(
        tmp_path, monkeypatch):
    monkeypatch.setenv("VERI_ISSUE", "9")
    step, ledger = "step A adds the case", tmp_path / ".tdd/issue-9.md"
    (tmp_path / ".tdd").mkdir()
    suite = tmp_path / "test_suite.py"
    suite.write_text("def test_base():\n    assert 0\n")
    ledger.write_text("- [ ] %s\n" % step)
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "add", "test_suite.py", ".tdd/issue-9.md")
    _git(tmp_path, "commit", "-q", "-m", "plan")
    suite.write_text(suite.read_text() + "\n\ndef test_one():\n    x = 1\n    assert x\n")
    assert frozen(tmp_path, "record", "--step", step, "test_suite.py")[0] == 0
    _git(tmp_path, "commit", "-q", "-am", "red")
    ledger.write_text("- [x] %s \u27c2 refactor pending\n" % step)
    _git(tmp_path, "commit", "-q", "-am", "green")
    green = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True,
                           text=True).stdout.strip()
    suite.write_text(suite.read_text().replace("x = 1\n", "x = 2 - 1\n"))
    _git(tmp_path, "commit", "-q", "-am", "refactor")
    (tmp_path / ".tdd/verdict-refactor.exit").write_text("0")
    record = tmp_path / frozen(tmp_path, "path", step)[1].strip()

    code = frozen(tmp_path, "rerecord-refactored", str(ledger), green)[0]

    body = "def test_one():\n    x = 2 - 1\n    assert x"
    digests = re.findall(r"^body: test_suite\.py\ttest_one\t(\w+)$", record.read_text(), re.M)
    assert (code, digests) == (0, [hashlib.sha256(body.encode()).hexdigest()])
