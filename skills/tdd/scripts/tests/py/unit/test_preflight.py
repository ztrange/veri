"""In-process cases for veri/preflight.py, the module preflight.sh is a shim over."""
import hashlib
import importlib
import os

import pytest


def test_3771_a_no_arguments_exit_2_with_the_usage_line_and_make_no_inner_call(monkeypatch, run_cli):
    preflight = importlib.import_module("veri.preflight")
    calls = []

    def run_script(name, *args, **kwargs):
        calls.append((name, args))
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    code, out, err = run_cli(preflight, [])

    assert code == 2
    assert "preflight.sh <n> <slug>" in err
    assert calls == []
    assert os.path.exists(os.path.join(os.path.dirname(preflight.__file__), "..", "preflight.sh"))


def test_3771_b_fresh_run_makes_front_calls_in_order_with_the_worktree_as_cwd(monkeypatch, run_cli, tmp_path):
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / "wt"
    (wt / ".tdd").mkdir(parents=True)
    (wt / ".tdd" / "ci-conflict-rebased").write_text("")
    calls = []

    def run_script(name, *args, **kwargs):
        calls.append((os.path.basename(name), args, kwargs.get("cwd")))
        if os.path.basename(name) == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    run_cli(preflight, ["12", "my-slug"])

    front = [(n, a) for n, a, _ in calls[:10]]
    assert front == [
        ("git", ("rev-parse", "--is-inside-work-tree")),
        ("git", ("status", "--porcelain")),
        ("gh", ("api", "user")),
        ("claude", ("auth", "status")),
        ("leaf-launchable.sh", ()),
        ("git", ("worktree", "list", "--porcelain")),
        ("ready-check.sh", ("--no-suites",)),
        ("issue-worktree.sh", ("12", "my-slug")),
        ("stop-requested.sh", ("--clear",)),
        ("unlabel-issue.sh", ("12",)),
    ]
    assert [str(c) for _, _, c in calls[8:10]] == [str(wt), str(wt)]
    assert not (wt / ".tdd" / "ci-conflict-rebased").exists()
    assert [n for n, _ in preflight.STEPS] == [1, 2, 3, 4, 5, 6, 7]
    assert all(isinstance(t, str) and t for _, t in preflight.STEPS)


def test_3771_c_each_inner_call_prints_a_line_naming_it_and_its_exit_then_its_stdout_and_stderr(monkeypatch, run_cli, tmp_path):
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / "wt"
    (wt / ".tdd").mkdir(parents=True)
    calls = []

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        calls.append(base)
        out = str(wt) + "\n" if base == "issue-worktree.sh" else ""
        return 0, out + "OUT<%d>\n" % len(calls), "ERR<%d>\n" % len(calls)

    monkeypatch.setattr(preflight, "run_script", run_script)

    code, out, err = run_cli(preflight, ["12", "my-slug"])

    lines = out.splitlines()
    heads = []
    for i, base in enumerate(calls, 1):
        idx = next(j for j, line in enumerate(lines) if base in line and "OUT<" not in line and line not in heads)
        heads.append(lines[idx])
        assert "0" in lines[idx]
        assert lines[idx + 1 + (base == "issue-worktree.sh")] == "OUT<%d>" % i
        assert "ERR<%d>" % i in err
    assert [lines.index(h) for h in heads] == sorted(lines.index(h) for h in heads)


def test_3771_d_leaf_launchable_exit_1_stops_with_no_later_call_and_a_stopped_at_last_line(monkeypatch, run_cli):
    preflight = importlib.import_module("veri.preflight")
    calls = []

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        calls.append(base)
        return (1, "", "") if base == "leaf-launchable.sh" else (0, "", "")

    monkeypatch.setattr(preflight, "run_script", run_script)

    code, out, err = run_cli(preflight, ["12", "my-slug"])

    assert code == 1
    assert calls[-1] == "leaf-launchable.sh"
    assert "issue-worktree.sh" not in calls and "unlabel-issue.sh" not in calls
    assert out.splitlines()[-1] == "stopped at 2 leaf-launchable.sh"


def test_3771_e_dirty_status_porcelain_stops_with_no_later_call_exit_1_and_a_stopped_at_last_line(monkeypatch, run_cli):
    preflight = importlib.import_module("veri.preflight")
    calls = []

    def run_script(name, *args, **kwargs):
        calls.append((os.path.basename(name), args))
        if os.path.basename(name) == "git" and args == ("status", "--porcelain"):
            return 0, " M some/file.py\n", ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    code, out, err = run_cli(preflight, ["12", "my-slug"])

    assert code == 1
    assert calls[-1] == ("git", ("status", "--porcelain"))
    assert ("gh", ("api", "user")) not in calls
    assert out.splitlines()[-1] == "stopped at 1 git status --porcelain"


def test_3771_f_claude_auth_status_logged_out_stops_with_no_later_call_exit_1_and_a_stopped_at_last_line(monkeypatch, run_cli):
    preflight = importlib.import_module("veri.preflight")
    calls = []

    def run_script(name, *args, **kwargs):
        calls.append((os.path.basename(name), args))
        if os.path.basename(name) == "claude" and args == ("auth", "status"):
            return 0, '{"loggedIn": false}\n', ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    code, out, err = run_cli(preflight, ["12", "my-slug"])

    assert code == 1
    assert calls[-1] == ("claude", ("auth", "status"))
    assert "leaf-launchable.sh" not in [n for n, _ in calls]
    assert out.splitlines()[-1] == "stopped at 2 claude auth status"


def test_3771_h_after_the_claim_step_3_runs_setup_body_detect_fast_baseline_full_tier_and_records_the_time(monkeypatch, run_cli, tmp_path):
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / "wt"
    (wt / ".tdd").mkdir(parents=True)
    calls = []

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        env = kwargs.get("env") or {}
        entry = [base, args, str(kwargs.get("cwd")), env.get("VERI_ISSUE")]
        if base == "requirements-preflight.sh":
            entry.append(open(args[0]).read())
        calls.append(entry)
        if base == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        if base == "gh" and args[:1] == ("api",) and "issues/12" in args[1]:
            return 0, "ISSUE BODY\n", ""
        if base == "git" and args == ("merge-base", "HEAD", "origin/HEAD"):
            return 0, "b45e\n", ""
        if base == "detect-test-command.sh":
            return 0, {"fast": "make unit\n", "all": "make test\n", "one test file": "make test TESTS=x\n"}[args[1]], ""
        if base == "baseline-full-tier.sh":
            return 0, "run\n", ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    code, out, err = run_cli(preflight, ["12", "my-slug"])

    names = [c[0] for c in calls]
    tail = calls[names.index("unlabel-issue.sh") + 1:]
    alone_calls = [c for c in tail if c[0] == "detect-test-command.sh" and c[1][:2] == ("--tier", "one test file")]
    tail = [c for c in tail if c not in alone_calls]
    # The green-record and CI reads (#4337) before the fast tier are pinned by their own cases.
    early = [c for c in tail if c[0] == "detect-test-command.sh" and c[1][:2] == ("--tier", "all")][:1]
    merge_base = [c for c in tail if c[1][:1] == ("merge-base",)]
    tail = [c for c in tail if c[1][:2] not in (("rev-parse", "HEAD"), ("run", "list"), ("rev-parse", "HEAD^{tree}"))
            and c not in merge_base
            and c[1][:1] != ("--green",) and not any(c is e for e in early)]
    body = tail[2][1][0] if len(tail) > 2 and tail[2][1] else None
    assert [(c[0], c[1][:1] if c[0] == "gh" else c[1][:2] if c[0] == "detect-test-command.sh" else c[1][:1]) for c in tail[:3]] == [
        ("worktree-setup.sh", ("12",)),
        ("gh", ("api",)),
        ("requirements-preflight.sh", (body,)),
    ]
    assert tail[1][1] == ("api", "repos/{owner}/{repo}/issues/12", "-q", ".body")
    assert body and not os.path.abspath(body).startswith(str(wt))
    assert tail[2][4] == "ISSUE BODY\n"
    assert [(c[0], c[1][:4]) for c in tail[3:4]] == [("detect-test-command.sh", ("--tier", "fast", "--issue", body))]
    # The fast command is read at the branch base, the merge base of HEAD and origin/HEAD (#4263).
    assert [c[:3] for c in merge_base] == [["git", ("merge-base", "HEAD", "origin/HEAD"), str(wt)]]
    assert calls.index(merge_base[0]) < calls.index(tail[3])
    assert tail[3][1][4:] == ("--at", "b45e", str(wt))
    fast_start, fast_wait = tail[4], tail[5]
    assert fast_start[0] == "detach-command.sh" and fast_start[1][0] == "start" and fast_start[1][2:] == ("make", "unit")
    assert fast_wait[0] == "detach-command.sh" and fast_wait[1] == ("wait", fast_start[1][1])
    assert tail[6][:2] == ["detect-test-command.sh", ("--tier", "all", "--issue", body, str(wt))]
    assert tail[7][:2] == ["baseline-full-tier.sh", ("12", "make test")]
    full_start, full_wait = tail[8], tail[9]
    assert full_start[0] == "detach-command.sh" and full_start[1][0] == "start" and full_start[1][2:] == ("make", "test")
    assert full_wait[0] == "detach-command.sh" and full_wait[1] == ("wait", full_start[1][1])
    assert tail[10][0] == "full-tier-time.sh" and tail[10][1][0] == "--record" and tail[10][1][1].isdigit()
    assert tail[10][1][2:] == ("make test",)
    assert [c[3] for c in (fast_start, fast_wait, full_start, full_wait)] == ["12"] * 4
    assert all(c[2] == str(wt) for c in tail[:11])
    assert all("--alone" not in c[1] for c in (fast_start, fast_wait, full_start, full_wait))
    assert len(tail) >= 11
    assert len(alone_calls) == 1
    assert alone_calls[0][1] == ("--tier", "one test file", "--issue", body, str(wt))
    assert alone_calls[0][2] == str(wt)


def test_3771_i_red_baseline_wait_exit_1_stops_at_3_with_no_later_call_no_flake_read_and_no_suite_flake_event(monkeypatch, run_cli, tmp_path):
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / "wt"
    (wt / ".tdd").mkdir(parents=True)
    calls = []

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        calls.append((base, args))
        if base == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        if base == "detect-test-command.sh":
            return 0, "make unit\n", ""
        if base == "detach-command.sh" and args[0] == "wait":
            return 1, "FAILED tests/test_x.py::test_y\n", ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    code, out, err = run_cli(preflight, ["12", "my-slug"])

    assert code == 1
    assert out.splitlines()[-1] == "stopped at 3 detach-command.sh wait"
    assert calls[-1][0] == "detach-command.sh" and calls[-1][1][0] == "wait"
    assert [c for c in calls if c[0] == "detach-command.sh"].__len__() == 2
    assert "baseline-full-tier.sh" not in [n for n, a in calls if a[:1] != ("--green",)]
    assert "event.sh" not in [n for n, _ in calls]
    assert all("--alone" not in a for _, a in calls)


def test_3771_j_baseline_wait_exit_3_makes_no_later_call_exits_3_and_ends_on_waiting_on_the_run_name(monkeypatch, run_cli, tmp_path):
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / "wt"
    (wt / ".tdd").mkdir(parents=True)
    calls = []

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        calls.append((base, args))
        if base == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        if base == "detect-test-command.sh":
            return 0, "make unit\n", ""
        if base == "detach-command.sh" and args[0] == "wait":
            return 3, "still running\n", ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    code, out, err = run_cli(preflight, ["12", "my-slug"])

    start = next(a for b, a in calls if b == "detach-command.sh" and a[0] == "start")
    assert code == 3
    assert calls[-1] == ("detach-command.sh", ("wait", start[1]))
    assert out.splitlines()[-1] == "waiting on " + start[1]


# The call preflight's step 5 makes last before the budget checks that follow it.
_REFACTOR_BUDGET_ISSUE = ("refactor-budget.sh", ("--issue", "0"))


def test_3771_k_after_the_full_tier_steps_4_to_7_run_in_order_with_the_tier_seconds_and_exit_0(monkeypatch, run_cli, tmp_path):
    import types
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / "wt"
    (wt / ".tdd").mkdir(parents=True)
    calls = []
    now = [1000.0]
    waits = []
    monkeypatch.setattr(preflight, "time", types.SimpleNamespace(monotonic=lambda: now[0]))

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        calls.append((base, args))
        if base == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        if base == "detect-test-command.sh":
            return 0, ("make unit\n" if args[1] == "fast" else "make test\n"), ""
        if base == "baseline-full-tier.sh":
            return 0, "run\n", ""
        if base == "detach-command.sh" and args[0] == "wait":
            waits.append(args)
            now[0] += 7.2 if len(waits) == 1 else 101.5
        if base == "gh" and args[-1] == ".default_branch":
            return 0, "main\n", ""
        if base == "refactor-budget.sh":
            return 3, "", ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    code, out, err = run_cli(preflight, ["12", "my-slug"])

    names = [c[0] for c in calls]
    tail = calls[names.index("full-tier-time.sh") + 1:]
    # The green record (#4337) written once the baseline passed is pinned by its own cases.
    tail = [c for c in tail if c[1][:2] != ("rev-parse", "HEAD^{tree}") and c[1][:1] != ("--record-green",)]
    assert tail == [
        ("gh", ("api", "repos/{owner}/{repo}", "-q", ".default_branch")),
        ("refactor-budget.sh", ("0",)),
        _REFACTOR_BUDGET_ISSUE,
        ("step-budget.sh", ()),
        ("adjudicate.sh", ("--check-budget",)),
        ("leaf-model.sh", ("develop-red",)),
        ("leaf-model.sh", ("revise-green",)),
        ("leaf-model.sh", ("verify-green",)),
        ("leaf-timeout.sh", ("8", "--full", "102")),
    ]
    assert code == 0


def test_3771_l_called_again_after_the_baseline_wait_exit_3_continues_from_that_wait_with_no_second_claim_or_start(monkeypatch, run_cli, tmp_path):
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    calls = []

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        calls.append((base, args))
        if base == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        if base == "detect-test-command.sh":
            return 0, "make unit\n", ""
        if base == "detach-command.sh" and args[0] == "wait":
            return 3, "still running\n", ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    first, _, _ = run_cli(preflight, ["12", "my-slug"], cwd=str(tmp_path))
    run_name = next(a[1] for b, a in calls if b == "detach-command.sh" and a[0] == "start")
    calls.clear()
    second, _, _ = run_cli(preflight, ["12", "my-slug"], cwd=str(tmp_path))

    assert first == 3
    assert calls[0] == ("detach-command.sh", ("wait", run_name))
    names = [b for b, _ in calls]
    assert "issue-worktree.sh" not in names and "unlabel-issue.sh" not in names
    assert not any(b == "detach-command.sh" and a[0] == "start" for b, a in calls)


def test_3771_m_resumed_baseline_wait_exit_0_refetches_the_issue_body_runs_the_full_tier_with_it_and_measures_the_baseline(monkeypatch, run_cli, tmp_path):
    import types
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    calls = []
    now = [1000.0]
    waits = []
    seen_body = []
    monkeypatch.setattr(preflight, "time", types.SimpleNamespace(monotonic=lambda: now[0]))

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        calls.append((base, args))
        if base == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        if base == "gh" and args[:2] == ("api", "repos/{owner}/{repo}/issues/12"):
            return 0, "the issue body\n", ""
        if base == "detect-test-command.sh":
            if args[1] == "all":
                seen_body.append(open(args[3]).read())
            return 0, {"fast": "make unit\n", "all": "make test\n", "one test file": "make test TESTS=x\n"}[args[1]], ""
        if base == "baseline-full-tier.sh":
            return 0, "run\n", ""
        if base == "detach-command.sh" and args[0] == "wait":
            waits.append(args)
            if len(waits) == 1:
                return 3, "still running\n", ""
            now[0] += 9.0 if len(waits) == 2 else 20.0
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    first, _, _ = run_cli(preflight, ["12", "my-slug"], cwd=str(tmp_path))
    calls.clear()
    seen_body.clear()
    second, _, _ = run_cli(preflight, ["12", "my-slug"], cwd=str(tmp_path))

    names = [b for b, _ in calls]
    assert first == 3 and second == 0
    assert calls[0][0] == "detach-command.sh" and calls[0][1][0] == "wait"
    assert names.index("gh") < names.index("detect-test-command.sh")
    assert sorted(a[:2] for b, a in calls if b == "detect-test-command.sh") == [("--tier", "all"), ("--tier", "one test file")]
    assert seen_body == ["the issue body\n"]
    assert ("leaf-timeout.sh", ("9", "--full", "20")) == next(c for c in calls if c[0] == "leaf-timeout.sh")


def test_3771_n_called_again_after_the_full_tier_wait_exit_3_continues_from_that_wait_with_no_start_and_the_first_baseline_seconds(monkeypatch, run_cli, tmp_path):
    import types
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    calls = []
    now = [1000.0]
    waits = []
    monkeypatch.setattr(preflight, "time", types.SimpleNamespace(monotonic=lambda: now[0]))

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        calls.append((base, args))
        if base == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        if base == "detect-test-command.sh":
            return 0, ("make unit\n" if args[1] == "fast" else "make test\n"), ""
        if base == "baseline-full-tier.sh":
            return 0, "run\n", ""
        if base == "detach-command.sh" and args[0] == "wait":
            waits.append(args)
            if len(waits) == 1:
                now[0] += 7.2
            elif len(waits) == 2:
                return 3, "still running\n", ""
            else:
                now[0] += 300.0
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    first, first_out, _ = run_cli(preflight, ["12", "my-slug"], cwd=str(tmp_path))
    calls.clear()
    now[0] += 5000.0
    second, _, _ = run_cli(preflight, ["12", "my-slug"], cwd=str(tmp_path))

    assert first == 3
    assert first_out.splitlines()[-1] == "waiting on preflight-full-12"
    assert calls[0] == ("detach-command.sh", ("wait", "preflight-full-12"))
    assert not any(b == "detach-command.sh" and a[0] == "start" for b, a in calls)
    assert second == 0
    assert next(a for b, a in calls if b == "leaf-timeout.sh")[0] == "8"


def test_3771_o_baseline_full_tier_reuse_starts_no_full_tier_run_records_nothing_and_passes_that_figure_to_leaf_timeout(monkeypatch, run_cli, tmp_path):
    import types
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / "wt"
    (wt / ".tdd").mkdir(parents=True)
    calls = []
    now = [1000.0]
    monkeypatch.setattr(preflight, "time", types.SimpleNamespace(monotonic=lambda: now[0]))

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        calls.append((base, args))
        if base == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        if base == "detect-test-command.sh":
            return 0, ("make unit\n" if args[1] == "fast" else "make test\n"), ""
        if base == "baseline-full-tier.sh":
            return 0, "reuse 55\n", ""
        if base == "detach-command.sh" and args[0] == "wait":
            now[0] += 7.2
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    code, out, err = run_cli(preflight, ["12", "my-slug"])

    starts = [a for b, a in calls if b == "detach-command.sh" and a[0] == "start"]
    assert len(starts) == 1
    assert not [a for b, a in calls if b == "full-tier-time.sh"]
    assert calls[-1] == ("leaf-timeout.sh", ("8", "--full", "55"))
    assert code == 0


def test_3771_p_empty_step_growth_stops_at_5_after_refactor_budget_issue_0_with_no_step_budget_call(monkeypatch, run_cli, tmp_path):
    import types
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / "wt"
    (wt / ".tdd").mkdir(parents=True)
    calls = []
    now = [1000.0]
    monkeypatch.setattr(preflight, "time", types.SimpleNamespace(monotonic=lambda: now[0]))
    monkeypatch.setenv("VERI_STEP_GROWTH", "")

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        calls.append((base, args))
        if base == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        if base == "detect-test-command.sh":
            return 0, ("make unit\n" if args[1] == "fast" else "make test\n"), ""
        if base == "baseline-full-tier.sh":
            return 0, "run\n", ""
        if base == "detach-command.sh" and args[0] == "wait":
            now[0] += 7.2
        if base == "gh" and args[-1] == ".default_branch":
            return 0, "main\n", ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    code, out, err = run_cli(preflight, ["12", "my-slug"])

    assert calls[-1] == _REFACTOR_BUDGET_ISSUE
    assert code == 2
    assert out.splitlines()[-1] == "stopped at 5 VERI_STEP_GROWTH"


@pytest.mark.parametrize("name, value, stop", [
    ("VERI_STEP_GROWTH", "5", "VERI_STEP_GROWTH"),
    ("VERI_STEP_GROWTH", "", "VERI_STEP_GROWTH"),
    ("VERI_STEP_GROWTH_PERCENT", "", "VERI_STEP_GROWTH_PERCENT"),
    ("VERI_STEP_GROWTH_PERCENT", "x", "VERI_STEP_GROWTH_PERCENT"),
    ("VERI_STEP_GROWTH_PERCENT", "-1", "VERI_STEP_GROWTH_PERCENT"),
])
def test_4075_a_set_retired_step_growth_or_a_refused_percent_stops_at_5_with_no_step_budget_call(
        monkeypatch, run_cli, tmp_path, name, value, stop):
    import types
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / "wt"
    (wt / ".tdd").mkdir(parents=True)
    calls = []
    now = [1000.0]
    monkeypatch.setattr(preflight, "time", types.SimpleNamespace(monotonic=lambda: now[0]))
    monkeypatch.setenv(name, value)

    def run_script(script, *args, **kwargs):
        base = os.path.basename(script)
        calls.append(base)
        if base == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        if base == "detect-test-command.sh":
            return 0, ("make unit\n" if args[1] == "fast" else "make test\n"), ""
        if base == "baseline-full-tier.sh":
            return 0, "run\n", ""
        if base == "detach-command.sh" and args[0] == "wait":
            now[0] += 7.2
        if base == "gh" and args[-1] == ".default_branch":
            return 0, "main\n", ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    code, out, err = run_cli(preflight, ["12", "my-slug"])

    assert (code, out.splitlines()[-1], out.splitlines()[-2].startswith("%s=%s: " % (name, value)),
            "VERI_STEP_GROWTH_PERCENT" in out, "step-budget.sh" in calls) == (2, "stopped at 5 " + stop, True, True, False)


def test_3771_q_non_numeric_missing_reroute_budget_stops_at_5_after_refactor_budget_issue_0_with_no_step_budget_call(monkeypatch, run_cli, tmp_path):
    import types
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / "wt"
    (wt / ".tdd").mkdir(parents=True)
    calls = []
    now = [1000.0]
    monkeypatch.setattr(preflight, "time", types.SimpleNamespace(monotonic=lambda: now[0]))
    monkeypatch.setenv("VERI_MISSING_REROUTE_BUDGET", "x")

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        calls.append((base, args))
        if base == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        if base == "detect-test-command.sh":
            return 0, ("make unit\n" if args[1] == "fast" else "make test\n"), ""
        if base == "baseline-full-tier.sh":
            return 0, "run\n", ""
        if base == "detach-command.sh" and args[0] == "wait":
            now[0] += 7.2
        if base == "gh" and args[-1] == ".default_branch":
            return 0, "main\n", ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    code, out, err = run_cli(preflight, ["12", "my-slug"])

    assert calls[-1] == _REFACTOR_BUDGET_ISSUE
    assert code == 2
    assert out.splitlines()[-1] == "stopped at 5 VERI_MISSING_REROUTE_BUDGET"


@pytest.mark.parametrize("value", ["x", "-1"])
def test_4760_bad_quality_repairs_stops_at_5_naming_it_exit_2_before_step_budget(monkeypatch, run_cli, tmp_path, value):
    import types
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / "wt"
    (wt / ".tdd").mkdir(parents=True)
    calls = []
    now = [1000.0]
    monkeypatch.setattr(preflight, "time", types.SimpleNamespace(monotonic=lambda: now[0]))
    monkeypatch.setenv("VERI_QUALITY_REPAIRS", value)

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        calls.append(base)
        if base == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        if base == "detect-test-command.sh":
            return 0, ("make unit\n" if args[1] == "fast" else "make test\n"), ""
        if base == "baseline-full-tier.sh":
            return 0, "run\n", ""
        if base == "detach-command.sh" and args[0] == "wait":
            now[0] += 7.2
        if base == "gh" and args[-1] == ".default_branch":
            return 0, "main\n", ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    code, out, err = run_cli(preflight, ["12", "my-slug"])

    assert (code, out.splitlines()[-1], "step-budget.sh" in calls) == (2, "stopped at 5 VERI_QUALITY_REPAIRS", False)


def test_3771_r_skip_verify_plan_stops_at_5_after_refactor_budget_issue_0_with_no_step_budget_call(monkeypatch, run_cli, tmp_path):
    import types
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / "wt"
    (wt / ".tdd").mkdir(parents=True)
    calls = []
    now = [1000.0]
    monkeypatch.setattr(preflight, "time", types.SimpleNamespace(monotonic=lambda: now[0]))
    monkeypatch.setenv("VERI_SKIP_VERIFY", "plan")

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        calls.append((base, args))
        if base == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        if base == "detect-test-command.sh":
            return 0, ("make unit\n" if args[1] == "fast" else "make test\n"), ""
        if base == "baseline-full-tier.sh":
            return 0, "run\n", ""
        if base == "detach-command.sh" and args[0] == "wait":
            now[0] += 7.2
        if base == "gh" and args[-1] == ".default_branch":
            return 0, "main\n", ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    code, out, err = run_cli(preflight, ["12", "my-slug"])

    assert calls[-1] == _REFACTOR_BUDGET_ISSUE
    assert code == 2
    assert out.splitlines()[-1] == "stopped at 5 VERI_SKIP_VERIFY"


@pytest.mark.parametrize("effort, stops", [("minimal", True), ("LOW", True), (" low", True), ("high", False),
                                           ("max", False), ("", False), (None, False)])
def test_4013_a_veri_effort_verifier_outside_the_five_levels_stops_at_5_before_the_leaf_model_checks(
        effort, stops, monkeypatch, run_cli, tmp_path):
    import types
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / "wt"
    (wt / ".tdd").mkdir(parents=True)
    calls = []
    now = [1000.0]
    monkeypatch.setattr(preflight, "time", types.SimpleNamespace(monotonic=lambda: now[0]))
    if effort is not None:
        monkeypatch.setenv("VERI_EFFORT_VERIFIER", effort)

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        calls.append(base)
        if base == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        if base == "detect-test-command.sh":
            return 0, ("make unit\n" if args[1] == "fast" else "make test\n"), ""
        if base == "baseline-full-tier.sh":
            return 0, "run\n", ""
        if base == "detach-command.sh" and args[0] == "wait":
            now[0] += 7.2
        if base == "gh" and args[-1] == ".default_branch":
            return 0, "main\n", ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    code, out, err = run_cli(preflight, ["12", "my-slug"])

    if stops:
        assert (code, out.splitlines()[-1], "leaf-model.sh" in calls) == (2, "stopped at 5 VERI_EFFORT_VERIFIER", False)
    else:
        assert (code, "VERI_EFFORT_VERIFIER" in out, "leaf-model.sh" in calls) == (0, False, True)


def test_3771_s_exit_0_writes_the_preflight_file_in_the_worktree_and_prints_the_same_lines_last(monkeypatch, run_cli, tmp_path):
    import types
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / "wt"
    (wt / ".tdd").mkdir(parents=True)
    now = [1000.0]
    monkeypatch.setattr(preflight, "time", types.SimpleNamespace(monotonic=lambda: now[0]))
    models = {"develop-red": "m-red", "revise-green": "m-rev", "verify-green": "m-ver"}

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        if base == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        if base == "detect-test-command.sh":
            return 0, {"fast": "make unit\n", "all": "make test\n", "one test file": "make test TESTS=x\n"}[args[1]], ""
        if base == "baseline-full-tier.sh":
            return 0, "run\n", ""
        if base == "detach-command.sh" and args[0] == "wait":
            now[0] += 7.2
        if base == "gh" and args[-1] == ".default_branch":
            return 0, "main\n", ""
        if base == "leaf-model.sh":
            return 0, models[args[0]] + "\n", ""
        if base == "leaf-timeout.sh":
            return 0, "1800\n", ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    code, out, err = run_cli(preflight, ["12", "my-slug"])

    expected = [
        "worktree=%s" % wt,
        "fast_cmd=make unit",
        "full_cmd=make test",
        "alone_cmd=make test TESTS=x",
        "baseline=8",
        "full=8",
        "full_tier_mode=run",
        "default_branch=main",
        "model_develop_red=m-red",
        "model_revise_green=m-rev",
        "model_verify_green=m-ver",
        "timeout=1800",
        "run=fresh",
    ]
    assert code == 0
    assert (wt / ".tdd" / "issue-12-preflight").read_text().splitlines() == expected
    assert out.splitlines()[-len(expected):] == expected


def test_3771_t_resumed_run_whose_baseline_full_tier_says_reuse_writes_the_real_commands_and_the_reuse_mode_and_figure(monkeypatch, run_cli, tmp_path):
    import types
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    now = [1000.0]
    monkeypatch.setattr(preflight, "time", types.SimpleNamespace(monotonic=lambda: now[0]))
    waits = []

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        if base == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        if base == "detect-test-command.sh":
            return 0, {"fast": "make unit\n", "all": "make test\n", "one test file": "make test TESTS=x\n"}[args[1]], ""
        if base == "baseline-full-tier.sh":
            return 0, "reuse 55\n", ""
        if base == "detach-command.sh" and args[0] == "wait":
            waits.append(args)
            if len(waits) == 1:
                return 3, "still running\n", ""
            now[0] += 7.2
        if base == "gh" and args[-1] == ".default_branch":
            return 0, "main\n", ""
        if base == "leaf-model.sh":
            return 0, "m-" + args[0] + "\n", ""
        if base == "leaf-timeout.sh":
            return 0, "1800\n", ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    first, _, _ = run_cli(preflight, ["12", "my-slug"], cwd=str(tmp_path))
    code, out, err = run_cli(preflight, ["12", "my-slug"], cwd=str(tmp_path))

    written = dict(line.split("=", 1) for line in (wt / ".tdd" / "issue-12-preflight").read_text().splitlines())
    assert first == 3
    assert code == 0
    assert written["fast_cmd"] == "make unit"
    assert written["full_cmd"] == "make test"
    assert written["alone_cmd"] == "make test TESTS=x"
    assert written["full_tier_mode"] == "reuse"
    assert written["full"] == "55"
    assert "full_tier_mode=reuse" in out.splitlines() and "full=55" in out.splitlines()


def test_3771_u_run_resumed_after_a_full_tier_wait_exit_3_writes_and_prints_the_original_fast_and_alone_commands(monkeypatch, run_cli, tmp_path):
    import types
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    now = [1000.0]
    monkeypatch.setattr(preflight, "time", types.SimpleNamespace(monotonic=lambda: now[0]))
    waits = []

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        if base == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        if base == "detect-test-command.sh":
            return 0, {"fast": "make unit\n", "all": "make test\n", "one test file": "make test TESTS=x\n"}[args[1]], ""
        if base == "baseline-full-tier.sh":
            return 0, "run\n", ""
        if base == "detach-command.sh" and args[0] == "wait":
            waits.append(args)
            if len(waits) == 2:
                return 3, "still running\n", ""
            now[0] += 7.2
        if base == "gh" and args[-1] == ".default_branch":
            return 0, "main\n", ""
        if base == "leaf-model.sh":
            return 0, "m-" + args[0] + "\n", ""
        if base == "leaf-timeout.sh":
            return 0, "1800\n", ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    first, _, _ = run_cli(preflight, ["12", "my-slug"], cwd=str(tmp_path))
    code, out, err = run_cli(preflight, ["12", "my-slug"], cwd=str(tmp_path))

    written = dict(line.split("=", 1) for line in (wt / ".tdd" / "issue-12-preflight").read_text().splitlines())
    assert first == 3
    assert code == 0
    assert written["fast_cmd"] == "make unit"
    assert written["alone_cmd"] == "make test TESTS=x"
    assert "fast_cmd=make unit" in out.splitlines() and "alone_cmd=make test TESTS=x" in out.splitlines()


def test_3771_v_never_prints_a_detached_run_output_file_and_a_test_run_appears_as_what_wait_printed(monkeypatch, run_cli, tmp_path):
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    for name in ("preflight-fast-12", "preflight-full-12"):
        for ext in (".out", ".log", ".txt", ""):
            (wt / ".tdd" / (name + ext)).write_text("SENTINEL-OUTPUT-FILE-CONTENTS\n")

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        if base == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        if base == "detect-test-command.sh":
            return 0, {"fast": "make unit\n", "all": "make test\n", "one test file": "make test TESTS=x\n"}[args[1]], ""
        if base == "baseline-full-tier.sh":
            return 0, "run\n", ""
        if base == "detach-command.sh" and args[0] == "wait":
            return 0, "WAIT-PRINTED-<%s>\n" % args[1], ""
        if base == "gh" and args[-1] == ".default_branch":
            return 0, "main\n", ""
        if base == "leaf-model.sh":
            return 0, "m-" + args[0] + "\n", ""
        if base == "leaf-timeout.sh":
            return 0, "1800\n", ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    code, out, err = run_cli(preflight, ["12", "my-slug"], cwd=str(tmp_path))

    assert code == 0
    assert "SENTINEL-OUTPUT-FILE-CONTENTS" not in out
    assert "WAIT-PRINTED-<preflight-fast-12>" in out.splitlines()
    assert "WAIT-PRINTED-<preflight-full-12>" in out.splitlines()


def test_3771_w_a_stop_handles_no_refusal_no_bail_event_no_comment_and_no_branch_reset(monkeypatch, run_cli, tmp_path):
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / "wt"
    (wt / ".tdd").mkdir(parents=True)

    def stop_run(stop):
        calls = []

        def run_script(name, *args, **kwargs):
            base = os.path.basename(name)
            calls.append((base, args))
            if base == "leaf-launchable.sh" and stop == "launchable":
                return 1, "", "not launchable\n"
            if base == "issue-worktree.sh":
                return 0, str(wt) + "\n", ""
            if base == "detect-test-command.sh":
                return 0, "make unit\n", ""
            if base == "detach-command.sh" and args[0] == "wait" and stop == "baseline":
                return 1, "FAILED tests/test_x.py::test_y\n", ""
            return 0, "", ""

        monkeypatch.setattr(preflight, "run_script", run_script)
        code, out, err = run_cli(preflight, ["12", "my-slug"])
        assert code == 1
        assert out.splitlines()[-1].startswith("stopped at ")
        return calls

    for stop in ("launchable", "baseline"):
        calls = stop_run(stop)
        names = [n for n, _ in calls]
        assert "preflight-refused.sh" not in names, stop
        assert "event.sh" not in names, stop
        assert "comment.sh" not in names, stop
        assert not [c for c in calls if c[0] == "gh" and any("comment" in a for a in c[1])], stop
        assert not [c for c in calls if c[0] == "git" and "reset" in c[1]], stop


def _drive(preflight, run_cli, tmp_path, failing, fail_code, monkeypatch):
    import types
    wt = tmp_path / "wt"
    (wt / ".tdd").mkdir(parents=True)
    calls = []
    now = [1000.0]
    waits = []
    monkeypatch.setattr(preflight, "time", types.SimpleNamespace(monotonic=lambda: now[0]))

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        calls.append((base, args))
        if failing(base, args, waits):
            return fail_code, "", "boom\n"
        if base == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        if base == "detect-test-command.sh":
            return 0, ("make unit\n" if args[1] == "fast" else "make test\n"), ""
        if base == "baseline-full-tier.sh":
            return 0, "run\n", ""
        if base == "detach-command.sh" and args[0] == "wait":
            waits.append(args)
            now[0] += 5
        if base == "gh" and args[-1] == ".default_branch":
            return 0, "main\n", ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)
    code, out, err = run_cli(preflight, ["12", "my-slug"])
    return wt, calls, code, out


def test_3771_x_a_red_full_tier_wait_exit_1_stops_at_3_with_no_later_call_and_no_preflight_file(monkeypatch, run_cli, tmp_path):
    preflight = importlib.import_module("veri.preflight")

    def failing(base, args, waits):
        return base == "detach-command.sh" and args[0] == "wait" and len(waits) == 1

    wt, calls, code, out = _drive(preflight, run_cli, tmp_path, failing, 1, monkeypatch)

    assert code == 1
    assert out.splitlines()[-1] == "stopped at 3 detach-command.sh wait"
    assert calls[-1][0] == "detach-command.sh" and calls[-1][1][0] == "wait"
    assert "full-tier-time.sh" not in [n for n, _ in calls]
    assert not (wt / ".tdd" / "issue-12-preflight").exists()


@pytest.mark.parametrize("bad, step, fail_code, only_args, last_line", [
    ("requirements-preflight.sh", 3, 2, None, None),
    ("worktree-setup.sh", 3, 2, None, None),
    ("issue-worktree.sh", 3, 2, None, None),
    ("unlabel-issue.sh", 3, 2, None, None),
    ("full-tier-time.sh", 3, 2, None, None),
    ("baseline-full-tier.sh", 3, 2, None, None),
    ("gh", 4, 1, ".default_branch", "stopped at 4 gh api repos/{owner}/{repo} -q .default_branch"),
    *[("refactor-budget.sh", 5, 2, argv, "stopped at 5 refactor-budget.sh " + " ".join(argv))
      for argv in (("0",), ("--issue", "0"))],
    ("step-budget.sh", 5, 2, None, None),
    ("adjudicate.sh", 5, 2, ("--check-budget",), "stopped at 5 adjudicate.sh --check-budget"),
    ("leaf-model.sh", 6, 2, None, None),
    ("leaf-timeout.sh", 7, 2, None, None),
])
def test_3771_y_a_failing_inner_call_stops_there_with_its_code_runs_no_later_call_and_writes_no_preflight_file(
        monkeypatch, run_cli, tmp_path, bad, step, fail_code, only_args, last_line):
    preflight = importlib.import_module("veri.preflight")

    def failing(base, args, waits):
        if base != bad:
            return False
        if only_args is None:
            return True
        return args[-1] == only_args if isinstance(only_args, str) else tuple(args) == only_args

    wt, calls, code, out = _drive(preflight, run_cli, tmp_path, failing, fail_code, monkeypatch)

    assert code == fail_code
    assert calls[-1][0] == bad
    if last_line is None:
        assert out.splitlines()[-1].startswith("stopped at %d %s" % (step, bad))
    else:
        assert out.splitlines()[-1] == last_line
    assert not (wt / ".tdd" / "issue-12-preflight").exists()


def test_3771_z_exit_3_of_worktree_setup_and_stop_requested_goes_on(monkeypatch, run_cli, tmp_path):
    preflight = importlib.import_module("veri.preflight")

    wt, calls, code, out = _drive(preflight, run_cli, tmp_path,
                                  lambda base, args, waits: base in ("worktree-setup.sh", "stop-requested.sh"), 3, monkeypatch)

    assert code == 0
    assert (wt / ".tdd" / "issue-12-preflight").exists()


def _front(monkeypatch, run_cli, tmp_path, answers=None):
    """Run preflight for #12 with every inner call answered 0 but those <answers> (basename → (code, out, err)) names;
    return (calls as (basename, args, cwd), exit code, stdout)."""
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / "wt"
    (wt / ".tdd").mkdir(parents=True, exist_ok=True)
    calls = []

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        calls.append((base, args, kwargs.get("cwd")))
        if answers and base in answers:
            return answers[base]
        if base == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)
    code, out, _ = run_cli(preflight, ["12", "my-slug"])
    return calls, code, out


def test_issue_4092_preflight_runs_ready_check_no_suites_after_step_2s_checks_and_before_step_3_creates_the_worktree(monkeypatch, run_cli, tmp_path):
    calls, _, out = _front(monkeypatch, run_cli, tmp_path)
    names = [n for n, _, _ in calls]

    assert names.index("leaf-launchable.sh") < names.index("ready-check.sh") < names.index("issue-worktree.sh"), names
    assert [args for n, args, _ in calls if n == "ready-check.sh"] == [("--no-suites",)], calls
    assert "ready-check.sh --no-suites exit 0" in out.splitlines(), out


@pytest.mark.parametrize("failing", ["leaf-launchable.sh", "gh", "claude"])
def test_issue_4092_a_failing_step_2_check_stops_preflight_before_ready_check_runs(monkeypatch, run_cli, tmp_path, failing):
    calls, code, out = _front(monkeypatch, run_cli, tmp_path, {failing: (1, "", "")})

    assert code == 1 and out.splitlines()[-1].startswith("stopped at 2 "), out
    assert "ready-check.sh" not in [n for n, _, _ in calls], calls


def _ready(*fails):
    """ready-check.sh's answer: every row ok but each of <fails> (a `fail  …` line)."""
    rows = ["ok    one test file", *fails, "ok    bash"]
    tail = f"not ready — {len(fails)} rows to fix" if fails else "ready"
    return (1 if fails else 0), "\n".join(rows + [tail]) + "\n", ""


REFUSING = ["fail  fast tier: add a `veri: fast tests:` line to CLAUDE.md",
            "fail  all tier: add a `veri: all tests:` line to CLAUDE.md",
            "fail  pull_request: add a workflow under .github/workflows/ that triggers on pull_request, add a `veri: ci on pr: 0|1` line to CLAUDE.md, or set VERI_CI_ON_PR",
            "fail  gh auth: run `gh auth login`",
            "fail  push access: ask for write access to the repository, or use an account that has it",
            "fail  label ready-for-agent:x: create the `ready-for-agent:x` label in the repository"]


@pytest.mark.parametrize("row", REFUSING)
def test_issue_4092_a_failing_refusing_row_stops_preflight_at_2_ready_check_with_exit_1_and_no_worktree(monkeypatch, run_cli, tmp_path, row):
    monkeypatch.setenv("VERI_LABEL", "ready-for-agent:x")
    calls, code, out = _front(monkeypatch, run_cli, tmp_path, {"ready-check.sh": _ready("fail  push: add a workflow", row)})
    lines = out.splitlines()

    assert code == 1, out
    assert row in lines, out
    assert lines[-1].startswith("stopped at 2 ready-check.sh"), out
    assert "issue-worktree.sh" not in [n for n, _, _ in calls], calls


WARNING = ["fail  push: add a workflow under .github/workflows/ that triggers on push to the default branch",
           "fail  label priority: gh label create priority", "fail  bypassPermissions: denied tools: `Bash`; look in …",
           "fail  one test file: add a `veri: one test file: <command>` line to CLAUDE.md"]


def test_issue_4092_any_other_failing_row_is_printed_and_preflight_goes_on_as_if_it_had_passed(monkeypatch, run_cli, tmp_path):
    calls, _, out = _front(monkeypatch, run_cli, tmp_path, {"ready-check.sh": _ready(*WARNING)})
    lines = out.splitlines()

    assert all(row in lines for row in WARNING), out
    assert not [line for line in lines if line.startswith("stopped at 2")], out
    assert "issue-worktree.sh" in [n for n, _, _ in calls], calls


def test_issue_4092_an_exit_2_from_ready_check_stops_preflight_at_2_ready_check_with_exit_2(monkeypatch, run_cli, tmp_path):
    calls, code, out = _front(monkeypatch, run_cli, tmp_path, {"ready-check.sh": (2, "", "ready-check.sh: not a git repository\n")})

    assert code == 2, out
    assert out.splitlines()[-1].startswith("stopped at 2 ready-check.sh"), out
    assert "issue-worktree.sh" not in [n for n, _, _ in calls], calls


@pytest.mark.parametrize("answer", [_ready(REFUSING[2]), (2, "", "ready-check.sh: not a git repository\n")])
def test_issue_4092_a_stop_at_2_ready_check_writes_no_event_and_posts_no_comment(monkeypatch, run_cli, tmp_path, answer):
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.chdir(repo)
    calls, code, out = _front(monkeypatch, run_cli, tmp_path, {"ready-check.sh": answer})
    names = [n for n, _, _ in calls]

    assert out.splitlines()[-1].startswith("stopped at 2 ready-check.sh"), out
    assert not {"preflight-refused.sh", "event.sh", "comment.sh"} & set(names), names
    assert not [args for n, args, _ in calls if n == "gh" and any("comment" in a for a in args)], calls
    assert not (repo / ".tdd" / "wt" / "12").exists()


PERMISSION_OK = ["not verifiable  token scopes", "ok    label priority", "ok    label bug", "skipped  actions read",
                 "ok    run-state ignore", "ok    push dry-run", "ok    bypassPermissions"]


class Clone:
    """The facts preflight reads of a clone whose main working tree is <main>: the gh login `gh api user` answers,
    origin's URL, and ready-check.sh's rows."""

    def __init__(self, tmp_path, login="octo", url="git@github.com:o/r.git", rows=PERMISSION_OK):
        self.main, self.login, self.url, self.rows, self.ready = tmp_path / "main", login, url, list(rows), None
        self.main.mkdir(exist_ok=True)

    @property
    def record(self):
        return self.main / ".tdd" / "permissions-checked"

    def answers(self, base, args):
        if base == "gh" and args == ("api", "user"):
            return 0, '{"login": "%s", "id": 1}\n' % self.login if self.login else "", ""
        if base == "git" and args == ("worktree", "list", "--porcelain"):
            return 0, "worktree %s\nHEAD c0ffee\nbranch refs/heads/main\n\nworktree %s/other\n" % (self.main, self.main), ""
        if base == "git" and args == ("remote", "get-url", "origin"):
            return (0, self.url + "\n", "") if self.url else (2, "", "error: No such remote 'origin'\n")
        if base == "ready-check.sh" and self.ready is not None:
            return self.ready
        if base == "ready-check.sh":
            fails = [row for row in self.rows if row.startswith("fail")]
            tail = f"not ready — {len(fails)} rows to fix" if fails else "ready"
            return (1 if fails else 0), "\n".join(["ok    gh auth", *self.rows, tail]) + "\n", ""
        return None


TODAY = "2026-03-04"  # preflight's one date reader is fixed here, so no case reads the wall clock


def _preflight(monkeypatch, run_cli, tmp_path, clone, env=None, seen=None):
    """Run preflight for #12 over <clone> on TODAY; return (ready-check.sh's args per call, exit code, stdout, call
    names); <seen>, when given, gets its stderr under "err"."""
    import datetime
    preflight = importlib.import_module("veri.preflight")
    monkeypatch.setattr(preflight, "today", lambda: datetime.date.fromisoformat(TODAY))
    wt = tmp_path / "wt"
    (wt / ".tdd").mkdir(parents=True, exist_ok=True)
    calls = []

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        calls.append((base, args))
        answer = clone.answers(base, args)
        if answer is not None:
            return answer
        return (0, str(wt) + "\n", "") if base == "issue-worktree.sh" else (0, "", "")

    monkeypatch.setattr(preflight, "run_script", run_script)
    for name, value in (env or {}).items():
        monkeypatch.setenv(name, value)
    code, out, err = run_cli(preflight, ["12", "my-slug"])
    if seen is not None:
        seen["err"] = err
    return [args for base, args in calls if base == "ready-check.sh"], code, out, [base for base, _ in calls]


def test_issue_4093_a_record_holding_the_current_login_url_and_version_skips_the_permission_rows_naming_its_date(monkeypatch, run_cli, tmp_path):
    clone = Clone(tmp_path)
    _preflight(monkeypatch, run_cli, tmp_path, clone)

    called, _, out, _ = _preflight(monkeypatch, run_cli, tmp_path, clone)

    assert called == [("--no-suites", "--no-permissions")], called
    assert f"permission rows skipped: checked {TODAY}" in out.splitlines(), out


def test_issue_4093_the_skip_line_names_the_date_as_the_record_holds_it(monkeypatch, run_cli, tmp_path):
    clone = Clone(tmp_path)
    _preflight(monkeypatch, run_cli, tmp_path, clone)
    clone.record.write_text(clone.record.read_text().replace(TODAY, "2026-01-02"))

    called, _, out, _ = _preflight(monkeypatch, run_cli, tmp_path, clone)

    assert called == [("--no-suites", "--no-permissions")], called
    assert "permission rows skipped: checked 2026-01-02" in out.splitlines(), out


def _stale(how, clone, monkeypatch):
    if how == "missing":
        clone.record.unlink()
    elif how == "login":
        clone.login = "someone-else"
    elif how == "url":
        clone.url = "https://github.com/o/r.git"
    elif how == "version":
        preflight = importlib.import_module("veri.preflight")
        monkeypatch.setattr(preflight.ready_check, "PERMISSIONS_CHECK_VERSION", preflight.ready_check.PERMISSIONS_CHECK_VERSION + 1)
    elif how == "malformed":
        clone.record.write_text("checked, trust me\n")
    elif how == "truncated":
        clone.record.write_text(clone.record.read_text().splitlines(keepends=True)[0])
    elif how == "future-dated":
        clone.record.write_text(clone.record.read_text().replace(TODAY, "2026-03-05"))
    elif how == "unreadable":
        clone.record.unlink()
        clone.record.mkdir()
    elif how == "no login answered":
        clone.login = ""
    elif how == "no origin":
        clone.url = ""


STALE = ["missing", "login", "url", "version", "malformed", "truncated", "future-dated", "unreadable", "no login answered",
         "no origin"]


@pytest.mark.parametrize("how", STALE)
def test_issue_4093_a_missing_stale_or_unusable_record_runs_the_permission_rows(monkeypatch, run_cli, tmp_path, how):
    clone = Clone(tmp_path)
    _, first, _, _ = _preflight(monkeypatch, run_cli, tmp_path, clone)
    _stale(how, clone, monkeypatch)

    seen = {}
    called, code, out, _ = _preflight(monkeypatch, run_cli, tmp_path, clone, seen=seen)

    assert called == [("--no-suites",)], called
    assert not [line for line in out.splitlines() if line.startswith("permission rows skipped")], out
    if how == "unreadable":
        assert code == first, (code, first, out, seen["err"])
        assert not [f for f in os.listdir(clone.record.parent) if f.startswith(".permissions-checked-")], os.listdir(clone.record.parent)
        said = [line for line in seen["err"].splitlines() if "permissions-checked" in line]
        assert len(said) == 1 and str(tmp_path) not in said[0], seen["err"]


def test_issue_4093_veri_recheck_permissions_1_runs_the_permission_rows_over_a_current_record(monkeypatch, run_cli, tmp_path):
    clone = Clone(tmp_path)
    _preflight(monkeypatch, run_cli, tmp_path, clone)

    called, _, out, _ = _preflight(monkeypatch, run_cli, tmp_path, clone, env={"VERI_RECHECK_PERMISSIONS": "1"})

    assert called == [("--no-suites",)], called


def test_issue_4093_veri_recheck_permissions_0_skips_over_a_current_record(monkeypatch, run_cli, tmp_path):
    clone = Clone(tmp_path)
    _preflight(monkeypatch, run_cli, tmp_path, clone)

    called, _, _, _ = _preflight(monkeypatch, run_cli, tmp_path, clone, env={"VERI_RECHECK_PERMISSIONS": "0"})

    assert called == [("--no-suites", "--no-permissions")], called


def test_issue_4093_a_check_whose_permission_rows_all_pass_writes_the_record_of_login_url_version_and_date(monkeypatch, run_cli, tmp_path):
    clone = Clone(tmp_path)

    _preflight(monkeypatch, run_cli, tmp_path, clone)

    held = clone.record.read_text()
    preflight = importlib.import_module("veri.preflight")
    origin = hashlib.sha256(b"git@github.com:o/r.git").hexdigest()
    for fact in ("octo", origin, str(preflight.ready_check.PERMISSIONS_CHECK_VERSION), TODAY):
        assert fact in held, held
    assert "git@github.com" not in held and str(tmp_path) not in held, held


def test_issue_4093_a_token_bearing_origin_url_leaves_no_trace_of_the_token_in_the_record_yet_still_keys_it(monkeypatch, run_cli, tmp_path):
    clone = Clone(tmp_path, url="https://someone:ghp_s3cretTok3nValue0123456789abcdefABCD@github.com/o/r.git")

    _preflight(monkeypatch, run_cli, tmp_path, clone)
    held = clone.record.read_bytes()
    called, _, _, _ = _preflight(monkeypatch, run_cli, tmp_path, clone)

    assert b"ghp_s3cretTok3nValue" not in held and b"someone" not in held and b"github.com" not in held, held
    assert called == [("--no-suites", "--no-permissions")], called


FAILING = [("ok    push dry-run", "fail  push dry-run: remote: Permission denied"),
           ("ok    bypassPermissions", "fail  bypassPermissions: denied tools: `Bash`"),
           ("ok    label bug", "fail  label bug: gh label create bug"),
           ("ok    push dry-run", None)]


@pytest.mark.parametrize("row, instead", FAILING)
def test_issue_4093_a_check_with_a_failing_or_missing_permission_row_writes_no_record_and_leaves_one_as_it_was(monkeypatch, run_cli, tmp_path, row, instead):
    clone = Clone(tmp_path, rows=[r for r in PERMISSION_OK if r != row] + ([instead] if instead else []))

    _preflight(monkeypatch, run_cli, tmp_path, clone)
    assert not clone.record.exists()

    clone.record.parent.mkdir(exist_ok=True)
    clone.record.write_bytes(b"login=someone-else\nkept as it was\n")
    _preflight(monkeypatch, run_cli, tmp_path, clone)
    assert clone.record.read_bytes() == b"login=someone-else\nkept as it was\n"


@pytest.mark.parametrize("answer", [(2, "", "ready-check.sh: not a git repository\n"), (3, "waiting on ready-fast\n", "")])
def test_issue_4093_a_check_with_no_answer_writes_no_record(monkeypatch, run_cli, tmp_path, answer):
    clone = Clone(tmp_path, rows=PERMISSION_OK + ["ok    bash"])
    clone.ready = answer

    _preflight(monkeypatch, run_cli, tmp_path, clone)

    assert not clone.record.exists()


@pytest.mark.parametrize("value", ["", "2", "yes", " 1"])
def test_issue_4093_a_bad_veri_recheck_permissions_stops_preflight_at_2_after_step_2s_checks_before_ready_check(monkeypatch, run_cli, tmp_path, value):
    clone = Clone(tmp_path)

    called, code, out, names = _preflight(monkeypatch, run_cli, tmp_path, clone, env={"VERI_RECHECK_PERMISSIONS": value})

    assert code == 2, out
    assert out.splitlines()[-1] == "stopped at 2 VERI_RECHECK_PERMISSIONS", out
    assert called == [] and "leaf-launchable.sh" in names and "issue-worktree.sh" not in names, names
    assert not (tmp_path / "wt" / ".tdd" / "wt").exists()


@pytest.mark.parametrize("baseline_wait, code", [(0, 0), (1, 1)], ids=["green baseline", "red baseline"])
def test_4228_preflight_runs_as_stage_preflight_and_its_baseline_suite_as_stage_baseline_each_ending_with_its_exit_code(
        monkeypatch, run_cli, tmp_path, baseline_wait, code):
    import json
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)  # as a conductor's launch leaves it, holding its pid file

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        if base == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        if base == "detect-test-command.sh":
            return 0, ("make unit\n" if args[1] == "fast" else "make test\n"), ""
        if base == "baseline-full-tier.sh":
            return 0, "run\n", ""
        if base == "detach-command.sh" and args[0] == "wait":
            return baseline_wait, "", ""
        if base == "gh" and args[-1] == ".default_branch":
            return 0, "main\n", ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    assert run_cli(preflight, ["12", "my-slug"], cwd=tmp_path)[0] == code
    lines = [json.loads(line) for line in (wt / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [(line["event"], line["stage"], line.get("status"), line["issue"]) for line in lines] == [
        ("stage-start", "preflight", None, "12"), ("stage-start", "baseline", None, "12"),
        ("stage-end", "baseline", str(code), "12"), ("stage-end", "preflight", str(code), "12")]
    assert all(line["secs"].isdigit() for line in lines if line["event"] == "stage-end")


def _staged_run(monkeypatch, run_cli, tmp_path, answers, saved=None):
    """Drive preflight for issue 12 from a worktree a conductor's launch made (its .tdd/ present), <saved> its
    preflight-wait file when given, <answers> overriding (script, first argument) -> (code, stdout); returns the exit
    code and the (event, stage, status) of each stage line."""
    import json
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    if saved is not None:
        (wt / ".tdd" / "issue-12-preflight-wait").write_text(
            json.dumps({"fields": saved.split("\n"), "carried": {"run": "fresh"}}))

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        for (script, first), (code, out) in answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                return code, out, ""
        if base == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        if base == "detect-test-command.sh":
            return 0, ("make unit\n" if args[1] == "fast" else "make test\n"), ""
        if base == "baseline-full-tier.sh":
            return 0, "run\n", ""
        if base == "gh" and args[-1] == ".default_branch":
            return 0, "main\n", ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)
    code = run_cli(preflight, ["12", "my-slug"], cwd=tmp_path)[0]
    lines = [json.loads(line) for line in (wt / ".tdd" / "events.jsonl").read_text().splitlines()]
    return code, [(line["event"], line["stage"], line.get("status")) for line in lines]


def test_4228_a_call_that_stops_preflight_inside_the_baseline_ends_both_stages_with_that_calls_own_code(
        monkeypatch, run_cli, tmp_path):
    code, lines = _staged_run(monkeypatch, run_cli, tmp_path, {("baseline-full-tier.sh", None): (1, "")})

    assert (code, lines) == (1, [("stage-start", "preflight", None), ("stage-start", "baseline", None),
                                 ("stage-end", "baseline", "1"), ("stage-end", "preflight", "1")])


def test_4228_a_preflight_whose_wait_ran_out_ends_both_stages_with_status_3(monkeypatch, run_cli, tmp_path):
    code, lines = _staged_run(monkeypatch, run_cli, tmp_path, {("detach-command.sh", "wait"): (3, "")})

    assert (code, lines) == (3, [("stage-start", "preflight", None), ("stage-start", "baseline", None),
                                 ("stage-end", "baseline", "3"), ("stage-end", "preflight", "3")])


@pytest.mark.parametrize("saved", ["fast\nmake unit", "full\n8\nmake test\nmake unit\nmake test TESTS=$1"],
                         ids=["a saved fast-tier wait", "a saved full-tier wait"])
def test_4228_a_preflight_called_again_after_a_wait_marks_both_stages_again_and_ends_them_with_its_code(
        monkeypatch, run_cli, tmp_path, saved):
    code, lines = _staged_run(monkeypatch, run_cli, tmp_path, {}, saved=saved)

    assert (code, lines) == (0, [("stage-start", "preflight", None), ("stage-start", "baseline", None),
                                 ("stage-end", "baseline", "0"), ("stage-end", "preflight", "0")])


SHA_4337 = "c" * 40


def _ci_answer_4337(**run):
    import json
    return json.dumps([dict({"headSha": SHA_4337, "status": "completed", "conclusion": "success", "event": "push"}, **run)]) + "\n"


TREE_4337 = "e" * 40


def _ci_run_4337(monkeypatch, run_cli, tmp_path, ci=None, gh_code=0, fast_code=0):
    """Preflight for issue 12 with `gh run list` answering <ci> (exit <gh_code>) and HEAD at SHA_4337:
    (exit code, stdout, the detach-command.sh starts, every call)."""
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / "wt"
    (wt / ".tdd").mkdir(parents=True)
    calls = []

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        calls.append((base, args))
        if base == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        if base == "git" and args == ("rev-parse", "HEAD"):
            return 0, SHA_4337 + "\n", ""
        if base == "git" and args == ("rev-parse", "HEAD^{tree}"):
            return 0, TREE_4337 + "\n", ""
        if base == "detach-command.sh" and args[:2] == ("wait", "preflight-fast-12"):
            return fast_code, "", ""
        if base == "gh" and args[:2] == ("run", "list"):
            return gh_code, ci if ci is not None else _ci_answer_4337(), ""
        if base == "detect-test-command.sh":
            return 0, ("make unit\n" if args[1] == "fast" else "make test\n"), ""
        if base == "baseline-full-tier.sh":
            return 0, "reuse 55\n", ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)
    code, out, err = run_cli(preflight, ["12", "my-slug"])
    starts = [a for b, a in calls if b == "detach-command.sh" and a[0] == "start"]
    return code, out, starts, calls


def test_4337_a_base_commit_whose_ci_run_concluded_success_starts_no_baseline_run_and_goes_on(
        monkeypatch, run_cli, tmp_path):
    code, out, starts, calls = _ci_run_4337(monkeypatch, run_cli, tmp_path)

    gh = [a for b, a in calls if b == "gh" and a[:2] == ("run", "list")]
    assert gh and "--commit" in gh[0] and gh[0][gh[0].index("--commit") + 1] == SHA_4337
    assert gh[0][gh[0].index("--workflow") + 1] == "CI"
    assert starts == []
    assert calls[-1][0] == "leaf-timeout.sh" and calls[-1][1][1:] == ("--full", "55")
    assert code == 0


@pytest.mark.parametrize("ci, gh_code", [
    (_ci_answer_4337(conclusion="failure"), 0),
    (_ci_answer_4337(status="in_progress", conclusion=""), 0),
    (_ci_answer_4337(status="queued", conclusion="success"), 0),
    ("[]\n", 0),
    ("not json\n", 0),
    (_ci_answer_4337(), 1),
    (_ci_answer_4337(headSha="d" * 40), 0),
    (_ci_answer_4337(event="pull_request"), 0),
], ids=["red", "pending", "not-completed", "absent", "unparseable", "gh-failure", "another-sha", "pull-request"])
def test_4337_a_ci_answer_that_is_not_success_on_the_sha_under_test_runs_the_baseline(
        monkeypatch, run_cli, tmp_path, ci, gh_code):
    code, out, starts, calls = _ci_run_4337(monkeypatch, run_cli, tmp_path, ci=ci, gh_code=gh_code)

    assert [s[2:] for s in starts] == [("make", "unit")]
    assert code == 0


@pytest.mark.parametrize("ci, fast_code, records", [("[]\n", 0, True), ("[]\n", 1, False), (None, 0, False)],
                         ids=["ran-green", "ran-red", "ci-skipped"])
def test_4337_a_baseline_that_ran_green_is_recorded_under_its_tree_and_commands_and_no_other_is(
        monkeypatch, run_cli, tmp_path, ci, fast_code, records):
    code, out, starts, calls = _ci_run_4337(monkeypatch, run_cli, tmp_path, ci=ci, fast_code=fast_code)

    recorded = [a for b, a in calls if b == "baseline-full-tier.sh" and a[:1] == ("--record-green",)]
    assert recorded == ([("--record-green", "12", TREE_4337, "make unit", "make test")] if records else [])


def test_4337_a_baseline_skipped_on_cis_word_whose_full_tier_was_waited_on_writes_no_record(
        monkeypatch, run_cli, tmp_path):
    """A skipped fast tier, then a full tier still running when the first call returns: the second call, which finds
    it green, must not record a baseline that never ran its fast tier."""
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    calls = []
    full_waits = iter([3, 0])

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        calls.append((base, args))
        if base == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        if base == "git" and args == ("rev-parse", "HEAD"):
            return 0, SHA_4337 + "\n", ""
        if base == "git" and args == ("rev-parse", "HEAD^{tree}"):
            return 0, TREE_4337 + "\n", ""
        if base == "detach-command.sh" and args[:2] == ("wait", "preflight-full-12"):
            return next(full_waits), "", ""
        if base == "gh" and args[:2] == ("run", "list"):
            return 0, _ci_answer_4337(), ""
        if base == "detect-test-command.sh":
            return 0, ("make unit\n" if args[1] == "fast" else "make test\n"), ""
        if base == "baseline-full-tier.sh":
            return 0, "run\n", ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)
    first = run_cli(preflight, ["12", "my-slug"], cwd=tmp_path)
    second = run_cli(preflight, ["12", "my-slug"], cwd=tmp_path)

    assert (first[0], first[1].splitlines()[-1], second[0]) == (3, "waiting on preflight-full-12", 0)
    assert [a for b, a in calls if b == "detach-command.sh" and a[:2] == ("start", "preflight-fast-12")] == []
    assert [a for b, a in calls if b == "baseline-full-tier.sh" and a[:1] == ("--record-green",)] == []


def test_4337_a_fast_tier_that_ran_and_was_waited_on_to_green_is_recorded(monkeypatch, run_cli, tmp_path):
    """A fast tier still running when the first call returns, found green by the second call: it ran, so it records."""
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    calls = []
    fast_waits = iter([3, 0])

    def run_script(name, *args, **kwargs):
        base = os.path.basename(name)
        calls.append((base, args))
        if base == "issue-worktree.sh":
            return 0, str(wt) + "\n", ""
        if base == "git" and args == ("rev-parse", "HEAD^{tree}"):
            return 0, TREE_4337 + "\n", ""
        if base == "detach-command.sh" and args[:2] == ("wait", "preflight-fast-12"):
            return next(fast_waits), "", ""
        if base == "gh" and args[:2] == ("run", "list"):
            return 0, "[]\n", ""
        if base == "detect-test-command.sh":
            return 0, ("make unit\n" if args[1] == "fast" else "make test\n"), ""
        if base == "baseline-full-tier.sh":
            return 0, "reuse 55\n", ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)
    first = run_cli(preflight, ["12", "my-slug"], cwd=tmp_path)
    second = run_cli(preflight, ["12", "my-slug"], cwd=tmp_path)

    assert (first[0], first[1].splitlines()[-1], second[0]) == (3, "waiting on preflight-fast-12", 0)
    assert [a for b, a in calls if b == "baseline-full-tier.sh" and a[:1] == ("--record-green",)] == [
        ("--record-green", "12", TREE_4337, "make unit", "make test")]
