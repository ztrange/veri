"""The leg's watchdog (#4254): a leg in which no case starts or reports for VERI_PYTEST_IDLE seconds ends itself.

xdist's controller waits for its workers' events with no deadline (`DSession.pytest_runtestloop`), and a per-case timeout
fires only while a case runs, so a worker that stops reporting outside a case held its leg for hours. The leg loads this
module as a plugin (PYTEST_PLUGINS, so its workers load it too) and makes a `Watch` the CURRENT one while its passes run:
the hooks below record, in the leg, each worker it started (by pid) and the time and node id of the last case that
started or reported; in a worker, where no Watch is current, they do nothing. The Watch's thread, once the leg has been
idle for the window, writes the stacks of all the leg's threads, sends each worker SIGUSR1 (on which this plugin has the
worker write all its threads' stacks), ends the workers (TERM, then KILL by pid after VERI_PYTEST_TERM_GRACE seconds, reaping the killed ones within that grace more), runs the leg's
cleanups, prints one line and exits 2. `end` is also what
the leg's TERM and HUP handler calls, so a signalled leg never waits on xdist's worker teardown.

PYTEST_DONT_REWRITE: the leg imports this module before pytest loads it as a plugin."""
import faulthandler
import os
import signal
import threading
import time

import pytest

import tunables

STACK_WAIT = 1
# The stderr this process started with, taken at import: pytest loads its PYTEST_PLUGINS before it starts capturing, and
# a worker's later fd 2 is pytest's capture file.
STDERR = os.dup(2)


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


def pytest_configure(config):
    if os.environ.get("PYTEST_XDIST_WORKER"):
        faulthandler.register(signal.SIGUSR1, file=STDERR, all_threads=True)


@pytest.hookimpl(optionalhook=True)
def pytest_xdist_newgateway(gateway):
    pid = worker_pid(gateway)
    if CURRENT[0] is not None and pid is not None:
        CURRENT[0].workers.append(pid)


@pytest.hookimpl(optionalhook=True)
def pytest_testnodedown(node, error):
    """A worker xdist reports down (finished, crashed, or replaced by a restart) is never signalled again: its pid may be
    reused by then."""
    pid = worker_pid(getattr(node, "gateway", None))
    if CURRENT[0] is not None and pid in CURRENT[0].workers:
        CURRENT[0].workers.remove(pid)


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
        self.grace = float(tunables.get("VERI_PYTEST_TERM_GRACE"))
        self.clock, self.sleep, self.kill, self.gone, self.exit, self.dump = clock, sleep, kill, gone, exit, dump
        self.stopped = threading.Event()
        self.pause = pause or self.stopped.wait
        self.last, self.last_case = clock(), None
        self.workers, self.cleanups = [], []
        self.claim_lock, self.claimed = threading.Lock(), None
        self.finished = threading.Event()  # set once an end that claimed the leg is past its exit (only in tests)

    def seen(self, nodeid):
        self.last, self.last_case = self.clock(), nodeid

    def write(self, text):
        try:
            os.write(self.out, text.encode())
        except OSError:
            pass

    def end_workers(self):
        """TERM to each worker this leg started, KILL by pid to any still alive the grace (VERI_PYTEST_TERM_GRACE) later, then wait up to the
        grace more until each is gone, reaped (#4278: a killed worker is still dying or a zombie until then, and would outlive
        the leg's exit); their pids."""
        workers = [pid for pid in self.workers if pid > 1 and pid != os.getpid()]
        for pid in workers:
            self.signal(pid, signal.SIGTERM)
        self.wait_gone(workers)
        for pid in workers:
            if not self.gone(pid):
                self.signal(pid, signal.SIGKILL)
        self.wait_gone(workers)
        return workers

    def wait_gone(self, workers):
        deadline = self.clock() + self.grace
        while any(not self.gone(pid) for pid in workers) and self.clock() < deadline:
            self.sleep(0.1)

    def signal(self, pid, signum):
        try:
            self.kill(pid, signum)
        except OSError:
            pass

    def claim(self, who):
        """The leg ends once, by an end or by its own return, whichever claims it first.

        Never waits on the lock: a TERM handler runs on the main thread, which may be inside the return's own claim, and
        waiting there would be the hang this module ends. A claim that finds the lock held loses: whoever holds it is
        claiming the leg."""
        if not self.claim_lock.acquire(blocking=False):
            return False
        try:
            if self.claimed is not None:
                return False
            self.claimed = who
            return True
        finally:
            self.claim_lock.release()

    def end(self, code, line=None):
        """Ends the workers, runs the leg's cleanups, writes `line(<the workers' pids>)` and exits `code`; False, doing
        nothing, when the leg has already returned or another end runs."""
        if not self.claim("end"):
            return False
        self.finish(code, line)
        return True

    def finish(self, code, line):
        """The end of a leg this thread has claimed: whatever raises on the way, it still exits `code`."""
        try:
            workers = self.end_workers()
            for cleanup in self.cleanups:
                try:
                    cleanup()
                except Exception as exc:
                    self.write("the leg's cleanup %s failed: %s\n" % (getattr(cleanup, "__name__", cleanup), exc))
            if line:
                self.write(line(" ".join(str(pid) for pid in workers) or "none"))
        finally:
            try:
                self.exit(code)
            finally:
                self.finished.set()

    def idle_end(self, idle_for):
        # The claim comes first: once the watch holds it, the leg's return yields (it neither closes `out` nor reaps a
        # worker this thread signals); a leg that has returned already is never written to or signalled.
        if not self.claim("end"):
            return
        last = self.last_case or "none"
        def line(workers):
            return ("pytest leg idle for " + str(idle_for) + " s with no case running (last case seen: "
                    + last + "); workers " + workers + " ended\n")
        try:
            self.dump(file=self.out, all_threads=True)
            for pid in list(self.workers):
                if pid in self.workers and pid > 1 and pid != os.getpid():  # still listed: not reported down meanwhile
                    self.signal(pid, signal.SIGUSR1)
                    self.sleep(STACK_WAIT)  # one worker at a time: dumps sharing one stderr would interleave
        finally:
            self.finish(2, line)

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
        """Called as the leg returns: True when the return claimed the leg, so its own teardown runs; False when an end
        did, which then runs the cleanups and exits."""
        self.stopped.set()
        return self.claim("return")
