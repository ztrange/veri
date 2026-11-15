"""Small cases for veri.status.refresh_running: only a refresh of this scripts directory's report-cache.sh counts as running."""
import importlib
import os


def _listing(monkeypatch, status, command):
    monkeypatch.setattr(status.pid_file, "pids_matching", lambda pattern: ["4242"])
    monkeypatch.setattr(status.pid_file, "commands_of", lambda pids: "4242 %s refresh\n" % command)


def test_3711_refresh_running_is_true_while_a_refresh_of_this_scripts_directory_is_alive(monkeypatch):
    status = importlib.import_module("veri.status")
    own = os.path.join(status.paths.resolved_scripts_of(status.__file__), "report-cache.sh")
    _listing(monkeypatch, status, own)

    assert status.refresh_running() is True


def test_3711_refresh_running_is_false_while_only_another_scripts_directory_refreshes(monkeypatch):
    status = importlib.import_module("veri.status")
    _listing(monkeypatch, status, "/elsewhere/scripts/report-cache.sh")

    assert status.refresh_running() is False
