import pathlib
import shutil

import pytest

FIXTURE = pathlib.Path(__file__).resolve().parents[3] / "fixtures" / "journal"


@pytest.fixture(autouse=True)
def veri_home(tmp_path, monkeypatch):
    home = tmp_path / "veri-home"
    shutil.copytree(FIXTURE, home / "runs", ignore=shutil.ignore_patterns("README.md"))
    monkeypatch.setenv("VERI_HOME", str(home))
    return home
