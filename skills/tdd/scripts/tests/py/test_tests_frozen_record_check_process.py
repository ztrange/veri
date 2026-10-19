"""Cases for tests-frozen.sh that start the real entry point against files on disk."""
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
