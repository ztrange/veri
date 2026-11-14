"""In-process cases for veri/preflight.py, the module preflight.sh is a shim over."""
import importlib
import os


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

    front = [(n, a) for n, a, _ in calls[:8]]
    assert front == [
        ("git", ("rev-parse", "--is-inside-work-tree")),
        ("git", ("status", "--porcelain")),
        ("gh", ("api", "user")),
        ("claude", ("auth", "status")),
        ("leaf-launchable.sh", ()),
        ("issue-worktree.sh", ("12", "my-slug")),
        ("stop-requested.sh", ("--clear",)),
        ("unlabel-issue.sh", ("12",)),
    ]
    assert [str(c) for _, _, c in calls[6:8]] == [str(wt), str(wt)]
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
        idx = next(j for j, l in enumerate(lines) if base in l and "OUT<" not in l and l not in heads)
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


def test_3771_g_a_branch_already_holding_a_ledger_exits_2_before_any_inner_call_and_names_resume_md(monkeypatch, run_cli, tmp_path):
    preflight = importlib.import_module("veri.preflight")
    ledger = tmp_path / ".tdd" / "wt" / "12" / ".tdd" / "issue-12.md"
    ledger.parent.mkdir(parents=True)
    ledger.write_text("- [ ] step\n")
    calls = []

    def run_script(name, *args, **kwargs):
        calls.append((os.path.basename(name), args))
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    code, out, err = run_cli(preflight, ["12", "my-slug"], cwd=str(tmp_path))

    assert code == 2
    assert calls == []
    assert "RESUME.md" in err


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
    assert tail[3][1][4:] == (str(wt),)
    fast_start, fast_wait = tail[4], tail[5]
    assert fast_start[0] == "detach-command.sh" and fast_start[1][0] == "start" and fast_start[1][2:] == ("make unit",)
    assert fast_wait[0] == "detach-command.sh" and fast_wait[1] == ("wait", fast_start[1][1])
    assert tail[6][:2] == ["detect-test-command.sh", ("--tier", "all", "--issue", body, str(wt))]
    assert tail[7][:2] == ["baseline-full-tier.sh", ("12", "make test")]
    full_start, full_wait = tail[8], tail[9]
    assert full_start[0] == "detach-command.sh" and full_start[1][0] == "start" and full_start[1][2:] == ("make test",)
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
    assert "baseline-full-tier.sh" not in [n for n, _ in calls]
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
    assert tail == [
        ("gh", ("api", "repos/{owner}/{repo}", "-q", ".default_branch")),
        ("refactor-budget.sh", ("0",)),
        ("refactor-budget.sh", ("--issue", "0")),
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

    assert calls[-1] == ("refactor-budget.sh", ("--issue", "0"))
    assert code == 2
    assert out.splitlines()[-1] == "stopped at 5 VERI_STEP_GROWTH"


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

    assert calls[-1] == ("refactor-budget.sh", ("--issue", "0"))
    assert code == 2
    assert out.splitlines()[-1] == "stopped at 5 VERI_MISSING_REROUTE_BUDGET"


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

    assert calls[-1] == ("refactor-budget.sh", ("--issue", "0"))
    assert code == 2
    assert out.splitlines()[-1] == "stopped at 5 VERI_SKIP_VERIFY"


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

    written = dict(l.split("=", 1) for l in (wt / ".tdd" / "issue-12-preflight").read_text().splitlines())
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

    written = dict(l.split("=", 1) for l in (wt / ".tdd" / "issue-12-preflight").read_text().splitlines())
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
