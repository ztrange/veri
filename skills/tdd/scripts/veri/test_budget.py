"""The lane budget's entries (PRD 036.5): one file per (main working tree, lane) under VERI_TEST_BUDGET_DIR, its lane's
need on line 1 and its expiry in epoch seconds on line 2; every leg reads the unexpired ones to narrow T."""
import os
import time

import tunables


def budget_dir():
    return tunables.get("VERI_TEST_BUDGET_DIR") or os.path.join(os.path.expanduser("~"), ".veri-test-budget")


def unexpired():
    """[(lane, need)] for every entry whose expiry is still ahead; no directory is no entry."""
    root = budget_dir()
    try:
        names = sorted(os.listdir(root))
    except FileNotFoundError:
        return []
    now = time.time()
    found = []
    for name in names:
        with open(os.path.join(root, name)) as f:
            need, expiry = f.read().split("\n")[:2]
        if int(expiry) > now:
            found.append((name.partition("@")[0], int(need)))
    return found
