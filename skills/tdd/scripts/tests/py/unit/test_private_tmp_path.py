"""The pytest leg's tmp_path plugin: one fresh directory under the session basetemp, made without numbering."""
import _pytest.tmpdir
import pytest

import private_tmp_path


def test_making_a_cases_tmp_path_creates_a_fresh_empty_directory_named_for_the_case_without_calling_make_numbered_dir(
        tmp_path_factory, monkeypatch):
    numbered = []
    real = _pytest.tmpdir.make_numbered_dir
    monkeypatch.setattr(_pytest.tmpdir, "make_numbered_dir", lambda *args, **kwargs: numbered.append(args) or real(*args, **kwargs))

    made = private_tmp_path.make_tmp_path("test_case[1]", tmp_path_factory)

    assert numbered == []
    assert made.is_dir() and list(made.iterdir()) == []
    assert made.parent == tmp_path_factory.getbasetemp()
    assert "test_case_1_" in made.name
