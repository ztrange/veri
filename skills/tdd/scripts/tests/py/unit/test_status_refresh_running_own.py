"""Small cases for veri.status.refresh_running: only a refresh of this scripts directory's report-cache.sh counts as running."""
import importlib
import os
import subprocess


def _listing(monkeypatch, status, command):
    def run(argv, **kw):
        out = "4242\n" if argv[0] == "pgrep" else "4242 %s refresh\n" % command
        return subprocess.CompletedProcess(argv, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)


def test_3711_refresh_running_is_true_while_a_refresh_of_this_scripts_directory_is_alive(monkeypatch):
    status = importlib.import_module("veri.status")
    own = os.path.join(status.paths.resolved_scripts_of(status.__file__), "report-cache.sh")
    _listing(monkeypatch, status, own)

    assert status.refresh_running() is True


def test_3711_refresh_running_is_false_while_only_another_scripts_directory_refreshes(monkeypatch):
    status = importlib.import_module("veri.status")
    _listing(monkeypatch, status, "/elsewhere/scripts/report-cache.sh")

    assert status.refresh_running() is False
