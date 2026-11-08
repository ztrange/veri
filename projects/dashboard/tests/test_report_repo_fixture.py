import pathlib

SNAPSHOT = pathlib.Path(__file__).resolve().parents[1] / "fixtures" / "report-cache.json"


def test_report_repo_cache_is_a_copy_of_the_fixture_snapshot_in_tmp_path(report_repo, tmp_path):
    repo = pathlib.Path(report_repo).resolve()

    assert repo.is_relative_to(tmp_path.resolve())
    assert (repo / ".tdd" / "report-cache.json").read_bytes() == SNAPSHOT.read_bytes()
