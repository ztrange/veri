"""Cases for veri.pin_fast_tier run in-process."""
import importlib
import types


def test_main_run_from_a_subdirectory_of_the_repo_writes_the_reason_under_tdd_at_the_repo_root_and_leaves_no_tdd_in_the_subdirectory_1895(
        tmp_path, monkeypatch):
    pin = importlib.import_module("veri.pin_fast_tier")
    monkeypatch.setattr(pin.subprocess, "run", lambda *a, **k: types.SimpleNamespace(
        returncode=1, stdout=b"FAIL - red\n"))

    def run_from(root, subdirectory):
        (root / ".git").mkdir(parents=True)
        work = root / subdirectory
        work.mkdir(parents=True, exist_ok=True)
        monkeypatch.chdir(work)
        code = pin.main(["make unit"])
        reason = root / ".tdd" / "verify-pin.reason"
        return code, reason.read_bytes() if reason.exists() else None, (work / ".tdd").exists() and work != root

    assert [run_from(tmp_path / "root", "."), run_from(tmp_path / "nested", "skills/deep")] == [
        (1, b"FAIL - red\n", False),
        (1, b"FAIL - red\n", False),
    ]
