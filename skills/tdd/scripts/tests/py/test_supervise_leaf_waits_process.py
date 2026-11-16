"""Process case split from unit/test_supervise_leaf_waits.py: it forks a parent whose exited child stays a zombie."""
import pytest

from leaf_waits import leaf_left


@pytest.mark.process("a forked parent whose exited child stays an unreaped zombie that the test process cannot wait on")
def test_a_zombie_leaf_orphaned_to_a_parent_that_never_reaps_it_reads_as_gone_3431():
    import os
    import time

    told, tell = os.pipe()
    hold_read, hold_write = os.pipe()
    parent = os.fork()
    if parent == 0:
        try:
            os.close(told)
            os.close(hold_write)
            child = os.fork()
            if child == 0:
                os._exit(0)
            os.write(tell, b"%d\n" % child)
            os.read(hold_read, 1)
        finally:
            os._exit(0)
    os.close(tell)
    os.close(hold_read)
    try:
        leaf = int(os.read(told, 32))
        left = leaf_left(leaf, lambda pid: os.kill(pid, 0) is None, time.sleep, time.monotonic, bound=1.0)
    finally:
        os.close(hold_write)
        os.waitpid(parent, 0)
        os.close(told)

    assert left is False
