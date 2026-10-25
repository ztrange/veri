"""The per-case temporary directory the autouse hermetic_environment fixture sets up."""
import os
import pathlib
import tempfile


def test_2246_case_runs_with_tmpdir_and_tempdir_set_to_one_directory_beside_tmp_path(tmp_path):
    case_dir = pathlib.Path(os.environ["TMPDIR"])

    assert tempfile.tempdir == str(case_dir)
    assert case_dir.parent == tmp_path.parent
    assert case_dir != tmp_path
    assert not case_dir.is_relative_to(tmp_path)
    assert pathlib.Path(tempfile.gettempdir()) == case_dir
    fd = os.open(case_dir / "probe", os.O_CREAT | os.O_WRONLY)
    os.close(fd)
