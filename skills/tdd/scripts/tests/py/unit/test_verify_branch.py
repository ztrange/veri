"""In-process cases for veri/verify_branch.py, the module verify-branch.sh is a shim over (PRD 040.1, #4472)."""
import importlib

BASE = "abc1234def5678"


def test_4472_it_launches_the_verdict_branch_leaf_through_fused_launch_with_run_verdict_and_its_stderr_file(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    verify_branch = importlib.import_module("veri.verify_branch")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("spec\n")
    (tmp_path / ".tdd" / "issue-12-branch-base").write_text(BASE + "\n")
    launches = []

    def launch(where, wt_, name, command, *args, env, out, err, clear=()):
        launches.append((name, command, args, err))

    monkeypatch.setattr(fused, "launch", launch)
    monkeypatch.setattr(fused, "call", lambda *a, **kw: (0, "", ""))
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "", ""))
    run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    assert launches == [("verdict-branch", "run-verdict.sh",
                         ("--fast-cmd", "make unit", "--branch-base", BASE, "branch", ".tdd/issue-12-spec.md"),
                         ".tdd/verify-branch.err")]


def test_4472_the_verdict_branch_leaf_runs_with_veri_test_cmd_the_fast_command_and_veri_issue_the_issue_number(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    verify_branch = importlib.import_module("veri.verify_branch")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("spec\n")
    (tmp_path / ".tdd" / "issue-12-branch-base").write_text(BASE + "\n")
    envs = []

    def launch(where, wt_, name, command, *args, env, out, err, clear=()):
        envs.append((env.get("VERI_TEST_CMD"), env.get("VERI_ISSUE")))

    monkeypatch.setattr(fused, "launch", launch)
    monkeypatch.setattr(fused, "call", lambda *a, **kw: (0, "", ""))
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "", ""))
    monkeypatch.delenv("VERI_TEST_CMD", raising=False)
    monkeypatch.delenv("VERI_ISSUE", raising=False)
    run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    assert envs == [("make unit", "12")]


def test_4472_a_stop_requested_before_the_launch_ends_verify_branch_with_that_stops_code_and_launches_no_leaf(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    verify_branch = importlib.import_module("veri.verify_branch")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("spec\n")
    (tmp_path / ".tdd" / "issue-12-branch-base").write_text(BASE + "\n")
    named = []

    def call(name, *args, **kw):
        named.append(name.rsplit("/", 1)[-1])
        return (1, "", "") if name.endswith("stop-requested.sh") else (0, "", "")

    monkeypatch.setattr(fused, "call", call)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "", ""))
    code, _, _ = run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    assert (code, "detach-leaf.sh" in named) == (1, False)


def test_4472_called_again_while_the_verdict_branch_leaf_still_runs_it_launches_no_second_leaf_and_exits_3(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    verify_branch = importlib.import_module("veri.verify_branch")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("spec\n")
    (tmp_path / ".tdd" / "issue-12-branch-base").write_text(BASE + "\n")
    launches = []

    def launch(where, wt_, name, command, *args, env, out, err, clear=()):
        launches.append(name)

    def call(name, *args, **kw):
        return (3, "", "") if name.endswith("wait-leaf.sh") else (0, "", "")

    monkeypatch.setattr(fused, "launch", launch)
    monkeypatch.setattr(fused, "call", call)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "", ""))
    run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    launches.clear()
    code, _, _ = run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    assert (code, launches) == (3, [])


def test_4472_when_the_verdict_branch_leaf_passes_it_exits_0_and_adds_no_step_to_the_ledger(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    verify_branch = importlib.import_module("veri.verify_branch")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("spec\n")
    (tmp_path / ".tdd" / "issue-12-branch-base").write_text(BASE + "\n")
    named = []

    def call(name, *args, **kw):
        named.append(name.rsplit("/", 1)[-1])
        return (0, "", "")

    monkeypatch.setattr(fused, "launch", lambda *a, **kw: None)
    monkeypatch.setattr(fused, "call", call)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "", ""))
    code, _, _ = run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    assert (code, "add-ledger-step.sh" in named) == (0, False)


def test_4472_on_a_pass_it_writes_the_tips_head_sha_to_the_issues_branch_verified_file(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    verify_branch = importlib.import_module("veri.verify_branch")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("spec\n")
    (tmp_path / ".tdd" / "issue-12-branch-base").write_text(BASE + "\n")
    tip = "f" * 40

    def call(name, *args, **kw):
        if name == "git" and "rev-parse" in args:
            return (0, tip + "\n", "")
        return (0, "", "")

    monkeypatch.setattr(fused, "launch", lambda *a, **kw: None)
    monkeypatch.setattr(fused, "call", call)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, tip + "\n", "") if a[:2] == ("git", "rev-parse")
                        else (0, "", ""))
    code, _, _ = run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    written = [p.read_text().strip() for p in (wt / ".tdd" / "issue-12-branch-verified",
                                               tmp_path / ".tdd" / "issue-12-branch-verified") if p.exists()]
    assert (code, written) == (0, [tip])


def test_4472_with_head_equal_to_the_sha_in_the_issues_branch_verified_file_it_launches_no_leaf_and_exits_0(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    verify_branch = importlib.import_module("veri.verify_branch")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("spec\n")
    (tmp_path / ".tdd" / "issue-12-branch-base").write_text(BASE + "\n")
    tip = "f" * 40
    (wt / ".tdd" / "issue-12-branch-verified").write_text(tip + "\n")
    (tmp_path / ".tdd" / "issue-12-branch-verified").write_text(tip + "\n")
    launches = []

    def call(name, *args, **kw):
        if name == "git" and "rev-parse" in args:
            return (0, tip + "\n", "")
        return (0, "", "")

    monkeypatch.setattr(fused, "launch", lambda *a, **kw: launches.append(a[2]))
    monkeypatch.setattr(fused, "call", call)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, tip + "\n", "") if a[:2] == ("git", "rev-parse")
                        else (0, "", ""))
    code, _, _ = run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    assert (code, launches) == (0, [])


def test_4472_with_head_differing_from_the_sha_in_the_issues_branch_verified_file_it_launches_the_verdict_branch_leaf(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    verify_branch = importlib.import_module("veri.verify_branch")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("spec\n")
    (tmp_path / ".tdd" / "issue-12-branch-base").write_text(BASE + "\n")
    tip = "f" * 40
    (wt / ".tdd" / "issue-12-branch-verified").write_text("e" * 40 + "\n")
    (tmp_path / ".tdd" / "issue-12-branch-verified").write_text("e" * 40 + "\n")
    launches = []

    def call(name, *args, **kw):
        if name == "git" and "rev-parse" in args:
            return (0, tip + "\n", "")
        return (0, "", "")

    monkeypatch.setattr(fused, "launch", lambda *a, **kw: launches.append(a[2]))
    monkeypatch.setattr(fused, "call", call)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, tip + "\n", "") if a[:2] == ("git", "rev-parse")
                        else (0, "", ""))
    run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    assert launches == ["verdict-branch"]


def test_4472_on_a_reject_with_the_ledger_already_holding_veri_branch_repairs_steps_it_appends_none_bails_branch_rejected_and_exits_1(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    verify_branch = importlib.import_module("veri.verify_branch")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("spec\n")
    (tmp_path / ".tdd" / "issue-12-branch-base").write_text(BASE + "\n")
    (wt / ".tdd" / "issue-12.md").write_text(
        "- [x] a gear meshes ⟦criterion 1⟧\n"
        "- [ ] fix the branch: z ⟦diff-checked⟧ ⟦branch-repair⟧ ⟦criterion 1⟧\n")
    monkeypatch.delenv("VERI_BRANCH_REPAIRS", raising=False)
    calls = []

    def call(name, *args, **kw):
        calls.append((name.rsplit("/", 1)[-1], args))
        return (1, "", "") if name.endswith("wait-leaf.sh") else (0, "", "")

    monkeypatch.setattr(fused, "launch", lambda *a, **kw: None)
    monkeypatch.setattr(fused, "call", call)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "", ""))
    code, _, _ = run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    bails = [args[:2] for name, args in calls if name == "bail.sh"]
    added = [name for name, _ in calls if name == "add-ledger-step.sh"]
    assert (code, bails, added) == (1, [("12", "branch-rejected")], [])


def test_4472_the_branch_rejected_bail_hands_bail_the_verifiers_reason_file_as_its_note_file(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    verify_branch = importlib.import_module("veri.verify_branch")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("spec\n")
    (tmp_path / ".tdd" / "issue-12-branch-base").write_text(BASE + "\n")
    (wt / ".tdd" / "issue-12.md").write_text(
        "- [x] a gear meshes ⟦criterion 1⟧\n"
        "- [ ] fix the branch: z ⟦diff-checked⟧ ⟦branch-repair⟧ ⟦criterion 1⟧\n")
    monkeypatch.delenv("VERI_BRANCH_REPAIRS", raising=False)
    calls = []

    def call(name, *args, **kw):
        calls.append((name.rsplit("/", 1)[-1], list(args)))
        return (1, "", "") if name.endswith("wait-leaf.sh") else (0, "", "")

    monkeypatch.setattr(fused, "launch", lambda *a, **kw: None)
    monkeypatch.setattr(fused, "call", call)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "", ""))
    code, _, _ = run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    bails = [args for name, args in calls if name == "bail.sh"]
    assert code == 1 and len(bails) == 1
    args = bails[0]
    assert args[:2] == ["12", "branch-rejected"]
    assert args[args.index("--note-file") + 1:][:1] == [".tdd/verify-branch.reason"]


def test_4472_with_veri_branch_repairs_2_and_one_branch_repair_step_in_the_ledger_a_reject_appends_a_second_repair_step_instead_of_bailing(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    verify_branch = importlib.import_module("veri.verify_branch")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("spec\n")
    (tmp_path / ".tdd" / "issue-12-branch-base").write_text(BASE + "\n")
    (wt / ".tdd" / "issue-12.md").write_text(
        "- [x] a gear meshes ⟦criterion 1⟧\n"
        "- [ ] fix the branch: z ⟦diff-checked⟧ ⟦branch-repair⟧ ⟦criterion 1⟧\n")
    monkeypatch.setenv("VERI_BRANCH_REPAIRS", "2")
    calls = []

    def call(name, *args, **kw):
        calls.append(name.rsplit("/", 1)[-1])
        return (1, "", "") if name.endswith("wait-leaf.sh") else (0, "", "")

    monkeypatch.setattr(fused, "launch", lambda *a, **kw: None)
    monkeypatch.setattr(fused, "call", call)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "", ""))
    run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    ledger = (wt / ".tdd" / "issue-12.md").read_text()
    assert (ledger.count("⟦branch-repair⟧"), "bail.sh" in calls) == (2, False)


def test_4472_a_reject_commits_the_appended_repair_step_as_one_plan_commit_holding_the_ledger_and_its_added_file(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    verify_branch = importlib.import_module("veri.verify_branch")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("spec\n")
    (tmp_path / ".tdd" / "issue-12-branch-base").write_text(BASE + "\n")
    (wt / ".tdd" / "issue-12.md").write_text("- [x] a gear meshes ⟦criterion 1⟧\n")
    monkeypatch.delenv("VERI_BRANCH_REPAIRS", raising=False)
    gits = []

    def run_script(name, *args, **kw):
        if name == "git":
            gits.append(list(args))
        return (1, "", "") if name.endswith("wait-leaf.sh") else (0, "", "")

    monkeypatch.setattr(fused, "launch", lambda *a, **kw: None)
    monkeypatch.setattr(fused, "run_script", run_script)
    run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    commits = [a for a in gits if "commit" in a]
    named = {p.rsplit("/", 1)[-1] for a in gits if a[:1] in (["add"], ["commit"]) for p in a}
    messages = [a[a.index("-m") + 1] for a in commits if "-m" in a]
    assert (len(commits), [m.startswith("plan:") for m in messages],
            {"issue-12.md", "issue-12-added.md"} <= named) == (1, [True], True)


def test_4472_a_reject_with_budget_left_exits_1_after_committing_the_repair_step_so_run_pr_stops_at_rejected(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    verify_branch = importlib.import_module("veri.verify_branch")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("spec\n")
    (tmp_path / ".tdd" / "issue-12-branch-base").write_text(BASE + "\n")
    (wt / ".tdd" / "issue-12.md").write_text("- [x] a gear meshes ⟦criterion 1⟧\n")
    monkeypatch.delenv("VERI_BRANCH_REPAIRS", raising=False)

    monkeypatch.setattr(fused, "launch", lambda *a, **kw: None)
    monkeypatch.setattr(fused, "run_script",
                        lambda name, *a, **kw: (1, "", "") if name.endswith("wait-leaf.sh") else (0, "", ""))
    code, _, _ = run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    ledger = (wt / ".tdd" / "issue-12.md").read_text()
    assert (code, ledger.count("⟦branch-repair⟧")) == (1, 1)


def test_4472_a_verdict_branch_leaf_ending_with_no_verdict_exits_2_appends_no_step_and_records_no_branch_rejected_bail(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    verify_branch = importlib.import_module("veri.verify_branch")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("spec\n")
    (tmp_path / ".tdd" / "issue-12-branch-base").write_text(BASE + "\n")
    (wt / ".tdd" / "issue-12.md").write_text("- [x] a gear meshes ⟦criterion 1⟧\n")
    monkeypatch.delenv("VERI_BRANCH_REPAIRS", raising=False)
    calls = []

    def call(name, *args, **kw):
        calls.append(name.rsplit("/", 1)[-1])
        return (2, "", "") if name.endswith("wait-leaf.sh") else (0, "", "")

    monkeypatch.setattr(fused, "launch", lambda *a, **kw: None)
    monkeypatch.setattr(fused, "call", call)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "", ""))
    code, _, _ = run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    ledger = (wt / ".tdd" / "issue-12.md").read_text()
    assert (code, "bail.sh" in calls, "add-ledger-step.sh" in calls, ledger.count("⟦branch-repair⟧")) == (
        2, False, False, 0)


def test_4472_with_branch_in_the_pinned_skip_verify_it_launches_no_leaf_and_records_verify_branch_skipped_switched_off(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    verify_branch = importlib.import_module("veri.verify_branch")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("spec\n")
    (wt / ".tdd" / "issue-12-skip-verify").write_text("branch\n")
    (tmp_path / ".tdd" / "issue-12-branch-base").write_text(BASE + "\n")
    launches = []
    marks = []

    monkeypatch.setattr(fused, "launch", lambda *a, **kw: launches.append(a[2]))
    monkeypatch.setattr(fused, "mark", lambda where, wt_, n, step, *fields, **more: marks.append(fields))
    monkeypatch.setattr(fused, "call", lambda *a, **kw: (0, "", ""))
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "f" * 40 + "\n", "")
                        if a[:2] == ("git", "rev-parse") else (0, "", ""))
    run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    assert (launches, marks) == ([], [("verify-branch-skipped", "reason=switched-off")])


def test_4472_with_branch_in_the_pinned_skip_verify_it_writes_skipped_to_the_verdict_branch_exit_file_and_exits_0(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    verify_branch = importlib.import_module("veri.verify_branch")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("spec\n")
    (wt / ".tdd" / "issue-12-skip-verify").write_text("branch\n")
    (tmp_path / ".tdd" / "issue-12-branch-base").write_text(BASE + "\n")

    monkeypatch.setattr(fused, "launch", lambda *a, **kw: None)
    monkeypatch.setattr(fused, "mark", lambda *a, **kw: None)
    monkeypatch.setattr(fused, "call", lambda *a, **kw: (0, "", ""))
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "f" * 40 + "\n", "")
                        if a[:2] == ("git", "rev-parse") else (0, "", ""))
    code, _, _ = run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    exit_file = wt / ".tdd" / "verdict-branch.exit"
    assert (code, exit_file.read_text().strip() if exit_file.exists() else None) == (0, "skipped")


def test_4709_a_step_only_quoting_branch_repair_in_its_prose_does_not_count_toward_veri_branch_repairs(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    verify_branch = importlib.import_module("veri.verify_branch")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("spec\n")
    (tmp_path / ".tdd" / "issue-12-branch-base").write_text(BASE + "\n")
    (wt / ".tdd" / "issue-12.md").write_text(
        "- [x] a gear meshes ⟦criterion 1⟧\n"
        "- [ ] document the `⟦branch-repair⟧` mark in `a.md` ⟦criterion 2⟧\n")
    monkeypatch.delenv("VERI_BRANCH_REPAIRS", raising=False)
    calls = []

    def call(name, *args, **kw):
        calls.append(name.rsplit("/", 1)[-1])
        return (1, "", "") if name.endswith("wait-leaf.sh") else (0, "", "")

    monkeypatch.setattr(fused, "launch", lambda *a, **kw: None)
    monkeypatch.setattr(fused, "call", call)
    monkeypatch.setattr(fused, "run_script", lambda *a, **kw: (0, "", ""))
    run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    assert "bail.sh" not in calls


def test_4707_a_reject_whose_reason_holds_a_missing_test_line_appends_a_branch_repair_step_without_diff_checked(
        monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    verify_branch = importlib.import_module("veri.verify_branch")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12-spec.md").write_text("spec\n")
    (wt / ".tdd" / "verify-branch.reason").write_text(
        "criterion 3 has no case\nMISSING_TEST: a gear meshes\nVERDICT: REJECT\n")
    (tmp_path / ".tdd" / "issue-12-branch-base").write_text(BASE + "\n")
    (wt / ".tdd" / "issue-12.md").write_text("- [x] a gear meshes ⟦criterion 1⟧\n")
    monkeypatch.delenv("VERI_BRANCH_REPAIRS", raising=False)
    monkeypatch.setattr(fused, "launch", lambda *a, **kw: None)
    monkeypatch.setattr(fused, "call", lambda name, *a, **kw: (
        (1, "", "") if name.endswith("wait-leaf.sh") else (0, "", "")))
    monkeypatch.setattr(fused, "run_script",
                        lambda name, *a, **kw: (1, "", "") if name.endswith("wait-leaf.sh") else (0, "", ""))
    run_cli(verify_branch, ["12"], cwd=str(tmp_path))
    repairs = [l for l in (wt / ".tdd" / "issue-12.md").read_text().split("\n") if "⟦branch-repair⟧" in l]
    assert [("⟦diff-checked⟧" in l) for l in repairs] == [False]
