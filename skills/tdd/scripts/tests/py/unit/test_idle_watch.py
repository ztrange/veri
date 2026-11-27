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
    assert len(terms) == 2 and len(kills) == 2 and kills[0] - terms[0] >= 5  # VERI_PYTEST_TERM_GRACE unset: its default
    assert written() == ("pytest leg idle for 30 s with no case running (last case seen: tests/py/unit/test_x.py::test_last); "
                         "workers 4101 4102 ended\n")


def test_4814_veri_pytest_term_grace_sets_the_seconds_between_a_worker_s_term_and_its_kill(idle_watch, stderr_pipe, monkeypatch):
    monkeypatch.setenv("VERI_PYTEST_TERM_GRACE", "2")
    out, _ = stderr_pipe
    world = World()
    world.kill = lambda pid, signum: world.signals.append((pid, signum, world.now))  # nothing ever dies
    watch = watch_in(idle_watch, world, 30, out)
    watch.workers[:] = [4111]

    watch.end_workers()

    (_, term, term_at), (_, kill, kill_at) = world.signals
    assert (term, kill) == (signal.SIGTERM, signal.SIGKILL)
    assert 2 <= kill_at - term_at < 2.5  # the injected clock: the configured grace, not the default 5 s


def test_4254_a_worker_that_obeys_term_is_never_killed_and_a_leg_that_saw_no_case_names_none(idle_watch, stderr_pipe):
    out, written = stderr_pipe
    world = World(obey_term=True)
    watch = watch_in(idle_watch, world, 5, out)
    watch.workers[:] = [4201]

    run_until_ended(watch)

    assert (world.codes, world.signals) == ([2], [(4201, signal.SIGTERM)])
    assert "(last case seen: none); workers 4201 ended" in written()


class DyingWorld(World):
    """Workers a KILL leaves dying: each answers gone only on the `gone()` call after the one that first sees it dying,
    as a killed child is still running or a zombie until it is reaped."""

    def __init__(self):
        super().__init__()
        self.dying, self.reaped = {}, set()

    def kill(self, pid, signum):
        if signum == signal.SIGKILL:
            self.signals.append((pid, signum))
            self.dying[pid] = 0
            return
        super().kill(pid, signum)

    def gone(self, pid):
        if pid in self.dying:
            self.dying[pid] += 1
            if self.dying[pid] > 1:
                self.reaped.add(pid)
        return pid in self.reaped


def test_4278_after_kill_end_workers_returns_only_once_every_killed_worker_is_gone_reaped_within_the_grace_window(idle_watch, stderr_pipe):
    out, _ = stderr_pipe
    world = DyingWorld()
    watch = watch_in(idle_watch, world, 30, out)
    watch.workers[:] = [4301, 4302]

    workers = watch.end_workers()

    assert workers == [4301, 4302]
    assert [signum for _, signum in world.signals] == [signal.SIGTERM] * 2 + [signal.SIGKILL] * 2
    assert world.reaped == {4301, 4302}


def test_4278_a_killed_worker_that_never_goes_bounds_the_wait_by_the_grace_window(idle_watch, stderr_pipe):
    out, _ = stderr_pipe
    world = World()
    world.kill = lambda pid, signum: world.signals.append((pid, signum))  # nothing ever dies
    watch = watch_in(idle_watch, world, 30, out)
    watch.workers[:] = [4401]
    start = world.now

    assert watch.end_workers() == [4401]
    assert world.now - start <= 2 * 5 + 0.5  # VERI_PYTEST_TERM_GRACE unset: its default


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


def test_4254_a_watch_claims_the_leg_before_it_writes_or_signals_so_a_return_during_the_stack_wait_yields_to_it(idle_watch, stderr_pipe):
    out, written = stderr_pipe
    world = World(obey_term=True)
    watch = watch_in(idle_watch, world, 1, out)
    watch.workers[:] = [4451, 4452]
    returns = []
    real_sleep = watch.sleep
    # the leg's passes return during the first wait for a worker's stacks: its return must not take the leg back, or
    # it would close the fd the watch goes on writing to and reap workers the watch goes on signalling
    watch.sleep = lambda seconds: (returns.append(watch.stop()) if not returns else None, real_sleep(seconds))[1]

    run_until_ended(watch)

    assert (returns, world.usr1, world.codes) == ([False], [4451, 4452], [2])


def test_4254_once_the_leg_has_returned_an_end_neither_runs_its_cleanups_nor_signals_nor_exits(idle_watch, stderr_pipe):
    out, written = stderr_pipe
    world = World()
    watch = watch_in(idle_watch, world, 1, out)
    watch.workers[:] = [4461]
    cleaned = []
    watch.cleanups.append(lambda: cleaned.append(1))

    returned = watch.stop()
    ended = watch.end(2, lambda workers: "idle %s\n" % workers)

    assert (returned, ended, world.codes, world.signals, cleaned) == (True, False, [], [], [])


def test_4254_a_leg_whose_passes_return_while_an_end_runs_is_told_not_to_run_its_own_cleanup(idle_watch, stderr_pipe):
    out, written = stderr_pipe
    world = World(obey_term=True)
    watch = watch_in(idle_watch, world, 1, out)
    watch.workers[:] = [4471]
    returned = []
    watch.cleanups.append(lambda: returned.append(watch.stop()))  # the passes return while the end runs its cleanups

    with pytest.raises(Ended):
        watch.end(2, lambda workers: "idle %s\n" % workers)

    assert (returned, world.codes) == ([False], [2])


def test_4254_an_idle_leg_asks_one_worker_at_a_time_for_its_stacks_waiting_between_so_their_dumps_never_interleave(idle_watch, stderr_pipe):
    out, written = stderr_pipe
    world = World(obey_term=True)
    watch = watch_in(idle_watch, world, 5, out)
    watch.workers[:] = [4481, 4482, 4483]
    timeline = []
    real_kill, real_sleep = watch.kill, watch.sleep
    watch.kill = lambda pid, signum: (timeline.append(("usr1", pid)) if signum == signal.SIGUSR1 else None, real_kill(pid, signum))[1]
    watch.sleep = lambda seconds: (timeline.append(("wait", seconds)), real_sleep(seconds))[1]

    run_until_ended(watch)

    asked = timeline[:timeline.index(("usr1", 4483)) + 2]
    assert asked == [("usr1", 4481), ("wait", idle_watch.STACK_WAIT), ("usr1", 4482), ("wait", idle_watch.STACK_WAIT),
                     ("usr1", 4483), ("wait", idle_watch.STACK_WAIT)]


def test_4254_a_worker_xdist_reports_down_is_dropped_so_its_pid_is_never_signalled_again(idle_watch, stderr_pipe, monkeypatch):
    out, written = stderr_pipe
    world = World(obey_term=True)
    watch = watch_in(idle_watch, world, 1, out)
    monkeypatch.setattr(idle_watch, "CURRENT", [watch])

    def gateway(pid):
        return type("Gateway", (), {"_io": type("IO", (), {"popen": type("Popen", (), {"pid": pid})()})()})()

    def node(pid):
        return type("Node", (), {"gateway": gateway(pid)})()

    for pid in (4491, 4492, 4493):
        idle_watch.pytest_xdist_newgateway(gateway(pid))
    idle_watch.pytest_testnodedown(node(4491), None)
    idle_watch.pytest_testnodedown(node(4493), "crashed")
    idle_watch.pytest_testnodedown(node(4999), None)

    run_until_ended(watch)

    assert world.usr1 == [4492] and world.signals == [(4492, signal.SIGTERM)]


def test_4254_the_leg_ends_only_workers_it_recorded_never_itself_nor_a_pid_of_1_or_less(idle_watch, stderr_pipe):
    out, written = stderr_pipe
    world = World(obey_term=True)
    watch = watch_in(idle_watch, world, 1, out)
    watch.workers[:] = [0, 1, os.getpid(), 4501]

    run_until_ended(watch)

    assert (world.usr1, world.signals) == ([4501], [(4501, signal.SIGTERM)])


@pytest.mark.parametrize("pid", [0, 1, -1, None, "4601"])
def test_4254_a_gateway_whose_popen_pid_is_not_a_pid_above_1_is_never_recorded_so_never_signalled(idle_watch, stderr_pipe, monkeypatch, pid):
    out, written = stderr_pipe
    world = World(obey_term=True)
    watch = watch_in(idle_watch, world, 1, out)
    monkeypatch.setattr(idle_watch, "CURRENT", [watch])
    gateway = type("Gateway", (), {"_io": type("IO", (), {"popen": type("Popen", (), {"pid": pid})()})()})()

    idle_watch.pytest_xdist_newgateway(gateway)
    run_until_ended(watch)

    assert (watch.workers, world.usr1, world.signals) == ([], [], [])


def test_4254_the_signal_path_never_blocks_on_a_claim_the_leg_s_own_return_is_making(idle_watch, stderr_pipe):
    import threading

    out, written = stderr_pipe
    world = World(obey_term=True)
    watch = watch_in(idle_watch, world, 1, out)
    ended = []
    watch.claim_lock.acquire()  # the leg's return, on the thread the signal handler interrupts, is mid-claim
    try:
        handler = threading.Thread(target=lambda: ended.append(watch.end(143, lambda workers: "signal %s\n" % workers)), daemon=True)
        handler.start()
        handler.join(2)
        blocked = handler.is_alive()
    finally:
        watch.claim_lock.release()
    handler.join(2)

    assert (blocked, ended, world.codes) == (False, [False], [])


def test_4254_a_worker_reported_down_during_the_stack_wait_is_not_asked_for_its_stacks(idle_watch, stderr_pipe):
    out, written = stderr_pipe
    world = World(obey_term=True)
    watch = watch_in(idle_watch, world, 1, out)
    watch.workers[:] = [4651, 4652]
    real_sleep = world.sleep

    def sleep(seconds):
        if 4652 in watch.workers and world.usr1 == [4651]:
            watch.workers.remove(4652)  # xdist reports 4652 down while the leg waits for 4651's stacks
        real_sleep(seconds)

    watch.sleep = sleep
    run_until_ended(watch)

    assert world.usr1 == [4651]


def test_4254_once_the_leg_has_returned_an_idle_watch_writes_no_dump_and_signals_no_worker(idle_watch, stderr_pipe):
    out, written = stderr_pipe
    world = World(obey_term=True)
    watch = watch_in(idle_watch, world, 1, out)
    watch.workers[:] = [4661, 4662]
    dumps = []
    watch.dump = lambda **kwargs: dumps.append(kwargs)
    watch.stop()

    watch.idle_end(1)

    assert (dumps, world.usr1, world.signals, world.codes) == ([], [], [], [])


@pytest.mark.parametrize("nodeid", ["unit/test_a.py::test_a[50%]", "unit/test_b.py::test_b[%s %d %(x)s {} {0}]"])
def test_4254_an_idle_leg_whose_last_case_id_holds_format_characters_still_exits_2_naming_it(idle_watch, stderr_pipe, nodeid):
    out, written = stderr_pipe
    world = World(obey_term=True)
    watch = watch_in(idle_watch, world, 30, out)
    watch.workers[:] = [4671]
    watch.seen(nodeid)

    run_until_ended(watch)

    assert (world.codes, written()) == ([2], "pytest leg idle for 30 s with no case running (last case seen: %s); "
                                             "workers 4671 ended\n" % nodeid)


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


@pytest.mark.timeout(10)
@pytest.mark.parametrize("sig", [signal.SIGTERM, signal.SIGHUP], ids=["TERM", "HUP"])
def test_4254_a_term_or_hup_landing_while_the_leg_s_return_holds_the_claim_ends_the_leg_128_plus_the_signal_after_one_cleanup(monkeypatch, tmp_path, sig):
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
    cleanups = []

    def spy(args):
        watch = idle_watch.CURRENT[0]
        if watch is None or cleanups:
            return pytest.ExitCode.NO_TESTS_COLLECTED
        watch.exit, watch.kill, watch.gone, watch.sleep = world.exit, world.kill, world.gone, world.sleep
        watch.cleanups.append(lambda: cleanups.append("end"))
        real_claim = watch.claim

        def claim(who):  # the signal lands on the main thread while its return holds the claim
            if who == "return":
                with watch.claim_lock:
                    os.kill(os.getpid(), sig)
            return real_claim(who)

        watch.claim = claim
        cleanups.append("spy")
        return pytest.ExitCode.OK

    monkeypatch.setattr(pytest, "main", spy)
    with pytest.raises(SystemExit) as ended:
        pytest_leg.main(["some/dir"])

    assert (ended.value.code, cleanups, world.codes, os.listdir(legs), open(lock.path()).read()) == (
        128 + sig, ["spy"], [], [], "")
