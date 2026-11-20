"""veri/role_state_cli.py: role-state.sh's entry point, a written `set n` writing the lane's test budget entry (PRD 036.5)."""
import importlib


def test_4453_dev_set_n_writes_the_lanes_entry_and_prints_n_its_need_the_other_lanes_c_with_its_source_and_the_t_a_leg_reads_now(tmp_path, monkeypatch, run_cli):
    import hashlib
    import os
    import time
    import watch_runs
    role_state = importlib.import_module("veri.role_state")
    role_state_cli = importlib.import_module("veri.role_state_cli")
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    monkeypatch.setattr(watch_runs, "live_conductors", lambda: ["41"])
    ceiling = os.environ["VERI_TEST_CEILING_FILE"]
    with open(ceiling, "w") as f:
        f.write("10\n2026-11-19\n")
    root = os.environ["VERI_TEST_BUDGET_DIR"]
    os.makedirs(root)
    with open(os.path.join(root, "main@0123456789abcdef"), "w") as f:
        f.write("4\n%d\n" % (time.time() + 3600))
    own = "mu@" + hashlib.sha256(os.path.realpath(str(tmp_path)).encode()).hexdigest()[:16]

    code, out, err = run_cli(role_state_cli, ["dev", "--lane", "mu", "set", "n", "1"])

    with open(os.path.join(root, own)) as f:
        written = f.read().split("\n")[0]
    assert (code, out, written) == (0, "N=1; lane mu needs 2 (max(N, 1 live conductors) x 2); other lanes: main=4; "
                                       "C=10 from the ceiling record %s; T=6\n" % ceiling, "2"), err
