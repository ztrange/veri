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
            return 0, ("make unit\n" if args[1] == "fast" else "make test\n"), ""
        if base == "baseline-full-tier.sh":
            return 0, "run\n", ""
        return 0, "", ""

    monkeypatch.setattr(preflight, "run_script", run_script)

    code, out, err = run_cli(preflight, ["12", "my-slug"])

    names = [c[0] for c in calls]
    tail = calls[names.index("unlabel-issue.sh") + 1:]
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
    assert len(tail) == 11


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
