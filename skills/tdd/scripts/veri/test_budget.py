"""The lane budget's entries (PRD 036.5): one file per (main working tree, lane) under VERI_TEST_BUDGET_DIR, its lane's
need on line 1 and its expiry in epoch seconds on line 2; every leg reads the unexpired ones to narrow T."""
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
