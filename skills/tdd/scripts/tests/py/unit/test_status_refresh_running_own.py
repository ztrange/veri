"""Small cases for veri.status.refresh_running: only a refresh of this scripts directory's report-cache.sh counts as running."""
import importlib
import os


def _listing(fake_processes, command):
    fake_processes.answers({"pgrep": (0, "4242\n", ""), "ps": (0, "4242 %s refresh\n" % command, "")})


def test_3711_refresh_running_is_true_while_a_refresh_of_this_scripts_directory_is_alive(fake_processes):
    status = importlib.import_module("veri.status")
    own = os.path.join(status.paths.resolved_scripts_of(status.__file__), "report-cache.sh")
    _listing(fake_processes, own)

    assert status.refresh_running() is True


def test_3711_refresh_running_is_false_while_only_another_scripts_directory_refreshes(fake_processes):
    status = importlib.import_module("veri.status")
    _listing(fake_processes, "/elsewhere/scripts/report-cache.sh")

    assert status.refresh_running() is False
