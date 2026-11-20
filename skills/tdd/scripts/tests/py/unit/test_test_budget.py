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


def test_4453_an_entry_is_replaced_whole_through_a_temporary_file_beside_it_its_need_then_its_expiry_now_plus_the_ttl(monkeypatch, tmp_path):
    import hashlib
    monkeypatch.setenv("VERI_TEST_BUDGET_TTL", "60")
    monkeypatch.setattr(test_budget.time, "time", lambda: 1000.0)
    root = os.environ["VERI_TEST_BUDGET_DIR"]
    name = "main@" + hashlib.sha256(os.path.realpath(str(tmp_path)).encode()).hexdigest()[:16]
    os.makedirs(root)
    with open(os.path.join(root, name), "w") as f:
        f.write("2\n900\n")
    replaced = []
    real_replace = os.replace
    monkeypatch.setattr(test_budget.os, "replace", lambda src, dst: replaced.append((os.path.dirname(src), dst)) or real_replace(src, dst))

    test_budget.write(str(tmp_path), "main", 8)

    assert (replaced, os.listdir(root), open(os.path.join(root, name)).read()) == (
        [(root, os.path.join(root, name))], [name], "8\n1060\n")
