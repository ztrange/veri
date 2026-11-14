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
