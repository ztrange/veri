"""veri/test_budget.py: the lane budget's entries under VERI_TEST_BUDGET_DIR (PRD 036.5)."""
import os
import time

import test_budget


def test_4453_an_unreadable_malformed_or_expired_entry_adds_nothing_and_fails_nothing_and_an_expired_one_is_removed():
    root = os.environ["VERI_TEST_BUDGET_DIR"]
    os.makedirs(os.path.join(root, "unreadable@0000000000000000"))
    now = time.time()
    for name, text in [("live@1111111111111111", "4\n%d\n" % (now + 3600)),
                       ("malformed@2222222222222222", "four\nsoon\n"),
                       ("short@3333333333333333", "4\n"),
                       ("expired@4444444444444444", "6\n%d\n" % (now - 1))]:
        with open(os.path.join(root, name), "w") as f:
            f.write(text)

    assert (test_budget.unexpired(), sorted(os.listdir(root))) == (
        [("live", 4)], ["live@1111111111111111", "malformed@2222222222222222", "short@3333333333333333",
                        "unreadable@0000000000000000"])
