"""The lane budget's entries (PRD 036.5): one file per (main working tree, lane) under VERI_TEST_BUDGET_DIR, its lane's
need on line 1 and its expiry in epoch seconds on line 2; every leg reads the unexpired ones to narrow T."""
import hashlib
import os
import time

import tunables


def budget_dir():
    return tunables.get("VERI_TEST_BUDGET_DIR") or os.path.join(os.path.expanduser("~"), ".veri-test-budget")


def unexpired():
    """[(lane, need)] for every entry whose expiry is still ahead; no directory is no entry. An entry that is unreadable or
    malformed adds nothing and fails nothing; an expired one is removed."""
    root = budget_dir()
    try:
        names = sorted(os.listdir(root))
    except FileNotFoundError:
        return []
    now = time.time()
    found = []
    for name in names:
        path = os.path.join(root, name)
        try:
            with open(path) as f:
                need, expiry = (int(field) for field in f.read().split("\n")[:2])
        except (OSError, ValueError):
            continue
        if expiry > now:
            found.append((name.partition("@")[0], need))
        else:
            try:
                os.remove(path)
            except OSError:
                pass
    return found


def entry_name(main_tree, lane):
    """<lane>@<the first 16 hex digits of the sha256 of the main working tree's real path>."""
    return "%s@%s" % (lane, hashlib.sha256(os.path.realpath(main_tree).encode()).hexdigest()[:16])


def write(main_tree, lane, need):
    """Replaces <lane>'s entry for <main_tree> whole through a temporary file beside it: <need> on line 1, its expiry
    (now + VERI_TEST_BUDGET_TTL seconds) on line 2, so a reader never sees it half-written."""
    root = budget_dir()
    os.makedirs(root, exist_ok=True)
    path = os.path.join(root, entry_name(main_tree, lane))
    temporary = "%s.%d.tmp" % (path, os.getpid())
    with open(temporary, "w") as f:
        f.write("%d\n%d\n" % (need, int(time.time()) + int(tunables.get("VERI_TEST_BUDGET_TTL"))))
    os.replace(temporary, path)
