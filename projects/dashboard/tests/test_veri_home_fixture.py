import os
import pathlib

FIXTURE = pathlib.Path(__file__).resolve().parents[3] / "fixtures" / "journal"


def test_veri_home_is_a_copy_of_the_journal_fixture_in_tmp_path(tmp_path):
    home = pathlib.Path(os.environ["VERI_HOME"]).resolve()

    assert home.is_relative_to(tmp_path.resolve())
    assert sorted(p.name for p in (home / "runs").iterdir()) == ["3277.jsonl"]
    assert (home / "runs" / "3277.jsonl").read_bytes() == (FIXTURE / "3277.jsonl").read_bytes()
