"""In-process cases for veri/refresh_spec.py, the module refresh-spec.sh is a shim over."""
import importlib
import subprocess

import pytest


@pytest.fixture
def refresh_spec():
    return importlib.import_module("veri.refresh_spec")


def fake_gh(monkeypatch, labels, body):
    def fake_run(args, **kwargs):
        if list(args[:3]) == ["gh", "issue", "view"] and "labels" in args:
            stdout = labels
        elif list(args[:3]) == ["gh", "issue", "view"] and "body" in args:
            stdout = body
        else:
            raise AssertionError("unexpected command: %r" % (args,))
        return subprocess.CompletedProcess(args, 0, stdout, "")

    monkeypatch.setattr(subprocess, "run", fake_run)


def test_main_2572_exits_0_and_holds_the_live_capture_when_it_differs_with_the_same_checkbox_count(
        monkeypatch, tmp_path, refresh_spec):
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    spec = tmp_path / "issue-7-spec.md"
    spec.write_text("## Acceptance criteria\n\n- [ ] the old criterion\n- [ ] second\n")
    live = "## Acceptance criteria\n\n- [ ] the narrowed criterion\n- [ ] second\n"
    fake_gh(monkeypatch, "enhancement\n", live)

    code = refresh_spec.main(["7", str(spec)])

    assert (code, spec.read_bytes()) == (0, live.encode())
