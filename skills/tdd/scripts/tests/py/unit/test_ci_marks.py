"""ci_marks over a real directory: the file names and contents wait-ci.sh's marks have always had."""
import pytest
from veri import ci_marks
from veri.ci_marks import Marks

SHA = "c" * 40


@pytest.fixture
def run(tmp_path):
    (tmp_path / ".tdd").mkdir()
    return str(tmp_path)


def test_record_writes_the_value_and_a_newline_to_ci_kind_sha_under_the_run(run, tmp_path):
    for kind in ci_marks.KINDS:
        ci_marks.record(run, kind, SHA, 1234)

    assert {p.name: p.read_text() for p in (tmp_path / ".tdd").iterdir()} == {
        f"ci-deadline-{SHA}": "1234\n", f"ci-queued-{SHA}": "1234\n", f"ci-none-{SHA}": "1234\n",
        f"ci-head-{SHA}": "1234\n"}


def test_an_empty_run_names_marks_relative_to_the_current_directory():
    assert ci_marks.path("", "deadline", SHA) == ".tdd/ci-deadline-" + SHA


def test_record_in_a_run_with_no_tdd_directory_warns_on_stderr_and_writes_nothing(tmp_path, capsys):
    ci_marks.record(str(tmp_path), "queued", SHA, 5)

    assert (list(tmp_path.iterdir()), capsys.readouterr().err.startswith("wait-ci.sh: [Errno 2]")) == ([], True)


def test_load_reads_each_mark_as_its_kind_wants_it(run):
    ci_marks.record(run, "deadline", SHA, 99)
    ci_marks.record(run, "queued", SHA, 7)
    ci_marks.record(run, "none", "d" * 40, 8)

    assert ci_marks.load(run, SHA, "d" * 40) == Marks("99\n", ci_marks.path(run, "deadline", SHA), 7, 8)


def test_load_of_a_head_with_no_marks_is_all_absent(run):
    assert ci_marks.load(run, SHA, SHA) == Marks(None, ci_marks.path(run, "deadline", SHA), None, None)


@pytest.mark.parametrize("text", ["soon\n", "", "1.5\n"])
def test_a_queued_or_none_mark_that_is_not_a_whole_number_reads_as_absent(run, tmp_path, text):
    for kind in ("queued", "none"):
        (tmp_path / ".tdd" / f"ci-{kind}-{SHA}").write_text(text)

    assert (ci_marks.seconds(run, "queued", SHA), ci_marks.seconds(run, "none", SHA)) == (None, None)


def test_a_deadline_file_that_exists_but_cannot_be_read_reads_as_empty_text(run, tmp_path):
    (tmp_path / ".tdd" / f"ci-deadline-{SHA}").mkdir()

    assert (ci_marks.deadline_text(run, SHA), ci_marks.exists(run, "deadline", SHA)) == ("", True)


def test_remove_of_an_absent_mark_is_silent_and_fresh_window_drops_every_kind(run, tmp_path):
    ci_marks.remove(run, "none", SHA)
    for kind in ci_marks.KINDS:
        ci_marks.record(run, kind, SHA, 1)
    ci_marks.record(run, "deadline", "e" * 40, 1)

    ci_marks.fresh_window(run, SHA)

    assert [p.name for p in (tmp_path / ".tdd").iterdir()] == ["ci-deadline-" + "e" * 40]
