"""The one-full-run lock: at most one full `make test` runs per machine, and a waiter names the holder."""
import fcntl
import os
import sys

import pid_file
import tunables


def legs_dir():
    return tunables.get("VERI_PYTEST_LEGS") or os.path.join(os.path.expanduser("~"), ".veri-pytest-legs")


def waiters_dir():
    """Where a leg waiting for T registers its wait (PRD 036.9): VERI_PYTEST_WAITERS, else the legs registry's path with
    `.waiting` appended, so a registry moved for a test moves its waiters too."""
    return tunables.get("VERI_PYTEST_WAITERS") or legs_dir().rstrip("/") + ".waiting"


def path():
    return legs_dir().rstrip("/") + "-full.lock"


def wait_marker(key):
    return "%s.wait-%d" % (path(), key)


def enabled():
    return tunables.get("VERI_TEST_LOCK") != "0"


def held_by_ancestor():
    holder = os.environ.get("PYTEST_LEG_FULL_LOCK_HOLDER", "")
    try:
        with open(path()) as lock:
            recorded = lock.readline().split("\t")[0]
    except OSError:
        return False
    if not holder.isdigit() or recorded != "pid " + holder:
        return False
    try:
        os.kill(int(holder), 0)
    except PermissionError:
        pass
    except OSError:
        return False
    return True


class Lock:
    def __init__(self, lock, outer_holder):
        self.lock = lock
        self.outer_holder = outer_holder

    def release(self):
        if self.outer_holder is None:
            os.environ.pop("PYTEST_LEG_FULL_LOCK_HOLDER", None)
        else:
            os.environ["PYTEST_LEG_FULL_LOCK_HOLDER"] = self.outer_holder
        self.lock.seek(0)
        self.lock.truncate()
        self.lock.close()


def acquire():
    outer_holder = os.environ.get("PYTEST_LEG_FULL_LOCK_HOLDER")
    lock = open(path(), "a+")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        lock.seek(0)
        sys.stderr.write("waiting for the full run holding the lock: %s\n"
                         % " ".join(lock.read().split("\n")[0].split("\t")))
        sys.stderr.flush()
        waitfile = os.environ.get("PYTEST_LEG_LOCK_WAIT_MARKER", "")
        try:
            if waitfile:
                pid_file.record(waitfile, os.getpid(), atomic=True)
        except OSError as error:
            sys.stderr.write("cannot mark the lock wait, so it counts toward the leaf's timeout: %s\n" % error)
            waitfile = ""
        try:
            fcntl.flock(lock, fcntl.LOCK_EX)
        finally:
            try:
                if waitfile:
                    os.remove(waitfile)
            except OSError:
                pass
    lock.seek(0)
    lock.truncate()
    lock.write("pid %d\ttree %s\n" % (os.getpid(), os.path.realpath(os.getcwd())))
    lock.flush()
    os.environ["PYTEST_LEG_FULL_LOCK_HOLDER"] = str(os.getpid())
    return Lock(lock, outer_holder)
