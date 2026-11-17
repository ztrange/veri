"""The leg's watchdog (#4254): a leg in which no case starts or reports for VERI_PYTEST_IDLE seconds ends itself.

xdist's controller waits for its workers' events with no deadline (`DSession.pytest_runtestloop`), and a per-case timeout
fires only while a case runs, so a worker that stops reporting outside a case held its leg for hours. The leg loads this
module as a plugin (PYTEST_PLUGINS, so its workers load it too) and makes a `Watch` the CURRENT one while its passes run:
the hooks below record, in the leg, each worker it started (by pid) and the time and node id of the last case that
started or reported; in a worker, where no Watch is current, they do nothing. The Watch's thread, once the leg has been
idle for the window, ends the workers (TERM, then KILL by pid after GRACE seconds), runs the leg's cleanups, prints one
line and exits 2. `end` is also what
the leg's TERM and HUP handler calls, so a signalled leg never waits on xdist's worker teardown.

PYTEST_DONT_REWRITE: the leg imports this module before pytest loads it as a plugin."""
import faulthandler
import os
import signal
import threading
import time

import pytest

GRACE = 5
STACK_WAIT = 1


def worker_pid(gateway):
    """The pid of the process an execnet popen gateway started, or None for any other kind."""
    popen = getattr(getattr(gateway, "_io", None), "popen", None)
    pid = getattr(popen, "pid", None)
    return pid if isinstance(pid, int) and pid > 1 else None


def gone(pid):
    """Whether `pid`, a child this leg started, has exited: reaped here, or no longer answering kill 0."""
    try:
        reaped, _ = os.waitpid(pid, os.WNOHANG)
        if reaped == pid:
            return True
    except ChildProcessError:
        pass
    except OSError:
        return True
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    except PermissionError:
        return False
    return False


CURRENT = [None]


@pytest.hookimpl(optionalhook=True)
def pytest_xdist_newgateway(gateway):
    pid = worker_pid(gateway)
    if CURRENT[0] is not None and pid is not None:
        CURRENT[0].workers.append(pid)


def pytest_runtest_logstart(nodeid):
    if CURRENT[0] is not None:
        CURRENT[0].seen(nodeid)


def pytest_runtest_logreport(report):
    if CURRENT[0] is not None:
        CURRENT[0].seen(report.nodeid)


class Watch:
    def __init__(self, idle, out, clock=time.monotonic, sleep=time.sleep, pause=None, kill=os.kill, gone=gone,
                 exit=os._exit, dump=faulthandler.dump_traceback):
        self.idle, self.out = idle, out
        self.clock, self.sleep, self.kill, self.gone, self.exit, self.dump = clock, sleep, kill, gone, exit, dump
        self.stopped = threading.Event()
        self.pause = pause or self.stopped.wait
        self.last, self.last_case = clock(), None
        self.workers, self.cleanups = [], []
        self.ending = threading.Lock()

    def seen(self, nodeid):
        self.last, self.last_case = self.clock(), nodeid

    def write(self, text):
        try:
            os.write(self.out, text.encode())
        except OSError:
            pass

    def end_workers(self):
        """TERM to each worker this leg started, KILL by pid to any still alive GRACE seconds later; their pids."""
        workers = [pid for pid in self.workers if pid > 1 and pid != os.getpid()]
        for pid in workers:
            self.signal(pid, signal.SIGTERM)
        deadline = self.clock() + GRACE
        while any(not self.gone(pid) for pid in workers) and self.clock() < deadline:
            self.sleep(0.1)
        for pid in workers:
            if not self.gone(pid):
                self.signal(pid, signal.SIGKILL)
        return workers

    def signal(self, pid, signum):
        try:
            self.kill(pid, signum)
        except OSError:
            pass

    def end(self, code, line=None):
        """Ends the workers, runs the leg's cleanups, writes `line` (formatted with the workers' pids) and exits `code`."""
        if not self.ending.acquire(blocking=False):
            return
        workers = self.end_workers()
        for cleanup in self.cleanups:
            try:
                cleanup()
            except Exception as exc:
                self.write("the leg's cleanup %s failed: %s\n" % (getattr(cleanup, "__name__", cleanup), exc))
        if line:
            self.write(line % (" ".join(str(pid) for pid in workers) or "none"))
        self.exit(code)

    def idle_end(self, idle_for):
        self.end(2, "pytest leg idle for %d s with no case running (last case seen: %s); workers %%s ended\n"
                 % (idle_for, self.last_case or "none"))

    def watch(self):
        while not self.stopped.is_set():
            idle_for = self.clock() - self.last
            if idle_for >= self.idle:
                self.idle_end(int(idle_for))
                return
            self.pause(min(1.0, self.idle - idle_for))

    def start(self):
        self.last = self.clock()
        thread = threading.Thread(target=self.watch, name="pytest-leg-idle-watch", daemon=True)
        thread.start()
        return thread

    def stop(self):
        self.stopped.set()
