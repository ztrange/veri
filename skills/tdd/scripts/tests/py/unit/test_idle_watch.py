"""In-process cases for tests/leg/idle_watch.py, the pytest leg's watchdog (#4254), under an injected clock."""
import importlib
import os
import signal
import sys

import pytest


@pytest.fixture
def idle_watch():
    return importlib.import_module("idle_watch")


class Ended(Exception):
    pass


class World:
    """A clock that only the watch's own waits move, workers that never exit unless KILLed (or TERMed, when they obey
    it), and an exit that records its code and stops the watch."""

    def __init__(self, obey_term=False):
        self.now, self.signals, self.dead, self.codes, self.obey_term = 1000.0, [], set(), [], obey_term
        self.usr1 = []

    def clock(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds

    def kill(self, pid, signum):
        if signum == signal.SIGUSR1:
            self.usr1.append(pid)
            return
        self.signals.append((pid, signum))
        if signum == signal.SIGKILL or (signum == signal.SIGTERM and self.obey_term):
            self.dead.add(pid)

    def gone(self, pid):
        return pid in self.dead

    def exit(self, code):
        self.codes.append(code)
        raise Ended()


def watch_in(idle_watch, world, idle, out):
    return idle_watch.Watch(idle, out, clock=world.clock, sleep=world.sleep, pause=world.sleep, kill=world.kill,
                            gone=world.gone, exit=world.exit, dump=lambda **_: None)


def run_until_ended(watch):
    with pytest.raises(Ended):
        watch.watch()


@pytest.fixture
def stderr_pipe():
    read, write = os.pipe()
    yield write, lambda: (os.close(write), os.read(read, 1 << 16).decode(), os.close(read))[1]


def test_4254_a_leg_idle_for_the_window_terms_its_workers_kills_those_alive_5_s_later_by_pid_and_exits_2_naming_the_last_case(idle_watch, stderr_pipe):
    out, written = stderr_pipe
    world = World()
    watch = watch_in(idle_watch, world, 30, out)
    watch.workers[:] = [4101, 4102]
    watch.seen("tests/py/unit/test_x.py::test_last")
    term_at = []
    real_kill = world.kill
    world.kill = lambda pid, signum: (term_at.append((signum, world.now)), real_kill(pid, signum))[1]
    watch.kill = world.kill

    run_until_ended(watch)

    terms = [at for signum, at in term_at if signum == signal.SIGTERM]
    kills = [at for signum, at in term_at if signum == signal.SIGKILL]
    assert world.codes == [2]
    assert [pid for pid, signum in world.signals] == [4101, 4102, 4101, 4102]
    assert len(terms) == 2 and len(kills) == 2 and kills[0] - terms[0] >= idle_watch.GRACE
    assert written() == ("pytest leg idle for 30 s with no case running (last case seen: tests/py/unit/test_x.py::test_last); "
                         "workers 4101 4102 ended\n")


def test_4254_a_worker_that_obeys_term_is_never_killed_and_a_leg_that_saw_no_case_names_none(idle_watch, stderr_pipe):
    out, written = stderr_pipe
    world = World(obey_term=True)
    watch = watch_in(idle_watch, world, 5, out)
    watch.workers[:] = [4201]

    run_until_ended(watch)

    assert (world.codes, world.signals) == ([2], [(4201, signal.SIGTERM)])
    assert "(last case seen: none); workers 4201 ended" in written()


def test_4254_a_case_that_keeps_reporting_within_the_window_is_never_ended_and_the_window_counts_from_its_last_report(idle_watch, stderr_pipe):
    out, written = stderr_pipe
    world = World(obey_term=True)
    watch = watch_in(idle_watch, world, 30, out)
    watch.workers[:] = [4301]
    reports = iter(range(1000))

    def pause(seconds):
        world.sleep(seconds)
        n = next(reports)
        if n < 90 and n % 20 == 0:
            watch.seen("tests/test_slow.py::test_%d" % n)

    watch.pause = pause
    started = world.now
    run_until_ended(watch)

    assert world.signals == [(4301, signal.SIGTERM)]
    assert world.now - started >= 80 + 30  # the last report came after 80 waits of a second; the window counts from it
    assert "last case seen: tests/test_slow.py::test_80)" in written()


def test_4254_a_stopped_watch_never_ends_its_leg(idle_watch, stderr_pipe):
    out, written = stderr_pipe
    world = World()
    watch = watch_in(idle_watch, world, 1, out)
    watch.workers[:] = [4401]
    watch.stop()

    watch.watch()

    assert (world.codes, world.signals) == ([], [])


def test_4254_a_leg_whose_passes_return_while_its_watch_writes_the_stacks_is_never_ended(idle_watch, stderr_pipe):
    out, written = stderr_pipe
    world = World()
    watch = watch_in(idle_watch, world, 1, out)
    watch.workers[:] = [4451]
    watch.sleep = lambda seconds: watch.stop()  # the leg's passes return during the wait for the workers' stacks

    watch.watch()

    assert (world.codes, world.signals) == ([], [])


def test_4254_the_leg_ends_only_workers_it_recorded_never_itself_nor_a_pid_of_1_or_less(idle_watch, stderr_pipe):
    out, written = stderr_pipe
    world = World(obey_term=True)
    watch = watch_in(idle_watch, world, 1, out)
    watch.workers[:] = [0, 1, os.getpid(), 4501]

    run_until_ended(watch)

    assert world.signals == [(4501, signal.SIGTERM)]


def test_4254_the_hooks_record_a_gateway_s_popen_pid_and_each_case_seen_on_the_current_watch_only(idle_watch, stderr_pipe, monkeypatch):
    out, written = stderr_pipe
    world = World()
    watch = watch_in(idle_watch, world, 1, out)
    gateway = type("Gateway", (), {"_io": type("IO", (), {"popen": type("Popen", (), {"pid": 4601})()})()})()
    idle_watch.pytest_xdist_newgateway(gateway)
    idle_watch.pytest_runtest_logstart("a.py::test_unwatched")
    monkeypatch.setattr(idle_watch, "CURRENT", [watch])

    idle_watch.pytest_xdist_newgateway(gateway)
    idle_watch.pytest_xdist_newgateway(type("Gateway", (), {})())
    world.now += 7
    idle_watch.pytest_runtest_logstart("a.py::test_started")
    started = (watch.last_case, watch.last)
    world.now += 3
    idle_watch.pytest_runtest_logreport(type("Report", (), {"nodeid": "a.py::test_reported"})())

    assert (watch.workers, started, (watch.last_case, watch.last)) == (
        [4601], ("a.py::test_started", 1007.0), ("a.py::test_reported", 1010.0))


def test_4254_an_idle_leg_removes_its_registry_entry_and_releases_the_full_run_lock_before_it_exits_2_after_failing_cases(monkeypatch, tmp_path):
    pytest_leg = importlib.import_module("pytest_leg")
    idle_watch = importlib.import_module("idle_watch")
    lock = importlib.import_module("veri.full_run_lock")
    legs = tmp_path / "legs"
    for name, value in {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1",
                        "VERI_PYTEST_XDIST_IMPORTABLE": "1", "VERI_PYTEST_LEGS": str(legs), "PYTEST_PLUGINS": ""}.items():
        monkeypatch.setenv(name, value)
    for name in ("VERI_PYTEST_WORKERS", "PYTEST_XDIST_WORKER", "PYTEST_LEG_FULL_LOCK_HOLDER", "PYTEST_LEG_LOCK_WAIT_MARKER"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.setattr(pytest_leg, "worker_count", lambda requested: 2)
    at_exit = {}

    def spy(args):
        if "code" in at_exit:
            return pytest.ExitCode.NO_TESTS_COLLECTED  # the serial pass, after the injected exit returned
        watch = idle_watch.CURRENT[0]
        at_exit["registered"] = os.listdir(legs)

        def record(code):
            at_exit.update(code=code, entries=os.listdir(legs), lock=open(lock.path()).read())
            raise Ended()

        watch.exit = record
        watch.workers[:] = []
        watch.seen("tests/test_red.py::test_failed")
        with pytest.raises(Ended):
            watch.idle_end(1200)
        return pytest.ExitCode.TESTS_FAILED

    monkeypatch.setattr(pytest, "main", spy)
    assert pytest_leg.main(["some/dir"]) == 1  # the injected exit returned; the leg's own teardown finds nothing left

    assert (at_exit["registered"], at_exit["code"], at_exit["entries"], at_exit["lock"]) == ([str(os.getpid())], 2, [], "")


def test_4254_an_idle_leg_dumps_all_its_threads_stacks_and_sends_each_worker_sigusr1_before_it_terms_any(idle_watch, stderr_pipe):
    out, written = stderr_pipe
    world = World(obey_term=True)
    watch = watch_in(idle_watch, world, 5, out)
    watch.workers[:] = [4701, 4702]
    dumps, order = [], []
    watch.dump = lambda **kwargs: dumps.append((kwargs, list(world.usr1), list(world.signals)))
    real_kill = watch.kill
    watch.kill = lambda pid, signum: (order.append((pid, signum)), real_kill(pid, signum))[1]

    run_until_ended(watch)

    assert dumps == [({"file": out, "all_threads": True}, [], [])]
    assert order == [(4701, signal.SIGUSR1), (4702, signal.SIGUSR1), (4701, signal.SIGTERM), (4702, signal.SIGTERM)]


def test_4254_in_a_worker_the_plugin_has_sigusr1_write_all_its_threads_stacks_to_the_stderr_it_started_with(idle_watch, monkeypatch):
    registered = []
    monkeypatch.setattr(idle_watch.faulthandler, "register", lambda signum, **kwargs: registered.append((signum, kwargs)))
    monkeypatch.setenv("PYTEST_XDIST_WORKER", "gw0")

    idle_watch.pytest_configure(None)
    monkeypatch.delenv("PYTEST_XDIST_WORKER")
    idle_watch.pytest_configure(None)

    assert [(signum, kwargs["all_threads"], kwargs["file"]) for signum, kwargs in registered] == [
        (signal.SIGUSR1, True, idle_watch.STDERR)]


@pytest.mark.parametrize("sig", [signal.SIGTERM, signal.SIGHUP], ids=["TERM", "HUP"])
def test_4254_a_leg_sent_term_or_hup_ends_its_workers_removes_its_entry_releases_the_lock_and_exits_128_plus_the_signal(monkeypatch, tmp_path, sig):
    pytest_leg = importlib.import_module("pytest_leg")
    idle_watch = importlib.import_module("idle_watch")
    lock = importlib.import_module("veri.full_run_lock")
    legs = tmp_path / "legs"
    for name, value in {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1",
                        "VERI_PYTEST_XDIST_IMPORTABLE": "1", "VERI_PYTEST_LEGS": str(legs), "PYTEST_PLUGINS": ""}.items():
        monkeypatch.setenv(name, value)
    for name in ("VERI_PYTEST_WORKERS", "PYTEST_XDIST_WORKER", "PYTEST_LEG_FULL_LOCK_HOLDER", "PYTEST_LEG_LOCK_WAIT_MARKER"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.setattr(pytest_leg, "worker_count", lambda requested: 2)
    world = World(obey_term=True)
    at_exit = {}

    def spy(args):
        if "code" in at_exit:
            return pytest.ExitCode.NO_TESTS_COLLECTED
        watch = idle_watch.CURRENT[0]
        at_exit["registered"] = os.listdir(legs)

        def record(code):
            at_exit.update(code=code, entries=os.listdir(legs), lock=open(lock.path()).read(), signals=list(world.signals))
            raise Ended()

        watch.exit, watch.kill, watch.gone, watch.sleep = record, world.kill, world.gone, world.sleep
        watch.workers[:] = [4801]
        with pytest.raises(Ended):
            os.kill(os.getpid(), sig)
        return pytest.ExitCode.OK

    monkeypatch.setattr(pytest, "main", spy)
    pytest_leg.main(["some/dir"])

    assert at_exit == {"registered": [str(os.getpid())], "code": 128 + sig, "entries": [], "lock": "",
                       "signals": [(4801, signal.SIGTERM)]}
