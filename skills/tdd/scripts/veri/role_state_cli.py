"""role-state.sh's entry point: role_state's verbs, a written `set n` also writing the lane's test budget entry and
printing the T it leaves (PRD 036.5). Apart from role_state so that the state file's readers (status, dispatch) never
import watch_runs, which imports status."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys

import budget_entries
import entry
import full_run_lock
import leg_budget
import leg_registry
import role_state
import tunables
import watch_runs

USAGE = role_state.USAGE


def lane_budget(path, n):
    """Writes the lane's entry under VERI_TEST_BUDGET_DIR as dispatch.sh does (max(N, live conductors) x d) and returns
    the line naming N, the lane's need, the other lanes' needs, C with its source and the T a leg reads now."""
    main = os.path.dirname(os.path.dirname(path))
    match = re.fullmatch(r"role-dev-(.+)\.state", os.path.basename(path))
    lane = match.group(1) if match else "main"
    live = len(watch_runs.live_conductors())
    d = int(tunables.get("VERI_CONDUCTOR_TEST_WORKERS"))
    if n == role_state.AUTO_N:
        return _auto_line(main, lane, live, d)
    need = max(n, live) * d
    budget_entries.write(main, lane, need)
    own = budget_entries.entry_name(main, lane)
    others = ", ".join("%s=%d" % (name.partition("@")[0], value) for name, value in budget_entries.unexpired_entries() if name != own)
    total, source = leg_budget.capacity(say=False)
    return "N=%d; lane %s needs %d (max(N, %d live conductors) x %d); other lanes: %s; C=%d from %s; T=%d\n" % (
        n, lane, need, live, d, others or "none", total, source, leg_budget.budget(say=False)[0])


def _auto_line(main, lane, live, d):
    """n=auto: writes C as the lane's need and returns the line naming the target dispatch.sh would take now, from T,
    W_other, d and the queue cap (the live conductors plus the queue's issues no open run draft PR overlaps); an
    unreadable queue leaves the target uncapped and names the cap `unread`."""
    import dispatch
    c = leg_budget.capacity(say=False)[0]
    budget_entries.write(main, lane, c)
    t = leg_budget.budget(say=False)[0]
    w = leg_registry.other_workers(full_run_lock.legs_dir())
    world = dispatch.World()
    try:
        changed = world.run_pr_paths()
        cap = live + sum(1 for issue in world.solvable() if not world.overlap(issue, changed))
    except watch_runs.QueueUnreadable:
        cap = None
    return "N=auto (%d now: floor((T=%d - W_other=%d)/%d), queue cap %s); lane %s needs C=%d\n" % (
        dispatch.auto_target(t, w, d, cap), t, w, d, "unread" if cap is None else cap, lane, c)


def main(argv):
    return role_state.run_verbs(argv, after_set_n=lane_budget)


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
