"""In-process cases for veri/ready_check.py, the module ready-check.sh is a shim over: only the gh, git and
detect-test-command.sh process boundaries are faked."""
import importlib
import json
import os
import re
import shlex

import pytest

WORKFLOW = "on:\n  pull_request:\n  push:\n    branches: [main]\n"
ONE_TEST_FILE = "detect-test-command.sh --tier one test file"


@pytest.fixture(autouse=True)
def outside_this_repository(monkeypatch, tmp_path):
    """A row run in-process reads the repository of the working directory: a scratch one, never veri's own."""
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def ready_check():
    return importlib.import_module("veri.ready_check")


def holding(**overrides):
    """The answers under which every row ready-check.sh prints holds, with <overrides> (command prefix → answer) on top."""
    table = {
        "git rev-parse --git-dir": (0, ".git\n", ""),
        "git symbolic-ref": (0, "origin/main\n", ""),
        "git ls-tree": (0, ".github/workflows/ci.yml\n", ""),
        "git show": (0, WORKFLOW, ""),
        "git ls-files": (0, "tests/test_x.py\n", ""),
        "git check-ignore": (0, "", ""),
        "gh auth status": (0, "", ""),
        "gh api repos/{owner}/{repo}": (0, '{"permissions": {"push": true}}', ""),
        "gh label list": (0, '[{"name": "ready-for-agent"}, {"name": "pr-ready"}, {"name": "bailed"}, {"name": "parked"}, '
                             '{"name": "stopped"}]', ""),
        "detect-test-command.sh": (0, "make test\n", ""),
        "gh api -i user": (0, "HTTP/2.0 200 OK\r\nX-Oauth-Scopes: repo, workflow\r\n\r\n{}", ""),
        "git remote get-url --push origin": (0, "git@github.com:o/r.git\n", ""),
        "gh api repos/{owner}/{repo}/labels/": (0, "{}", ""),
        "gh api repos/{owner}/{repo}/actions/runs?per_page=1": (0, "{}", ""),
        "git rev-parse --git-common-dir": (0, ".git\n", ""),
        "git push --dry-run --no-verify origin": (0, "", ""),
        "git config --get core.sshCommand": (1, "", ""),
        "git worktree": (0, "", ""),
        "git rev-parse --verify": (0, "c0ffee\n", ""),
        "detach-command.sh": (0, "", ""),
        "claude -p": lambda line, **kwargs: probe_answer()(line, **kwargs),
    }
    table.update(overrides)
    return table


def check(ready_check, run_cli, fake_processes, tmp_path, **overrides):
    """ready-check.sh run over <tmp_path> under holding(**overrides): (exit code, stdout lines)."""
    fake_processes.answers(holding(**overrides))
    home = tmp_path / "scratch-home"
    home.mkdir(exist_ok=True)
    (tmp_path / ".claude").mkdir(exist_ok=True)
    (tmp_path / ".claude" / "settings.json").write_text(json.dumps({"permissions": {"defaultMode": "bypassPermissions"}}))
    code, out, _ = run_cli(ready_check, [str(tmp_path)], env={"VERI_BASH_MAJOR": "5", "HOME": str(home)})
    return code, out.splitlines()


def test_issue_4087_ready_check_prints_an_ok_one_test_file_row_when_detect_test_command_finds_that_tier(ready_check, run_cli, fake_processes, tmp_path):
    code, lines = check(ready_check, run_cli, fake_processes, tmp_path, **{ONE_TEST_FILE: (0, 'pytest "$1"\n', "")})

    assert "ok    one test file" in lines, lines
    assert (code, lines[-1]) == (0, "ready")


def test_issue_4081_ready_check_prints_a_row_per_state_label_failing_with_the_create_fix_and_exits_1_when_gh_label_list_lacks_one(ready_check, run_cli, fake_processes, tmp_path):
    listed = '[{"name": "ready-for-agent"}, {"name": "pr-ready"}, {"name": "bailed"}, {"name": "parked"}]'
    code, lines = check(ready_check, run_cli, fake_processes, tmp_path, **{"gh label list": (0, listed, "")})

    for label in ("pr-ready", "bailed", "parked"):
        assert f"ok    label {label}" in lines, (label, lines)
    assert "fail  label stopped: create the `stopped` label in the repository" in lines, lines
    assert code == 1


def test_issue_4081_a_state_label_past_the_first_30_labels_reads_ok(ready_check, run_cli, fake_processes, tmp_path):
    names = ["ready-for-agent"] + ["area-%d" % i for i in range(40)] + ["pr-ready", "bailed", "parked", "stopped"]

    def gh_label_list(line, **kwargs):
        argv = line.split()
        limit = int(argv[argv.index("--limit") + 1]) if "--limit" in argv else 30
        return 0, json.dumps([{"name": n} for n in names[:limit]]), ""

    code, lines = check(ready_check, run_cli, fake_processes, tmp_path, **{"gh label list": gh_label_list})

    assert [l for l in lines if l.startswith("fail  label")] == [], lines


def one_test_file_row(lines):
    return next((line for line in lines if "one test file" in line), None)


def test_issue_4087_ready_check_fails_the_one_test_file_row_naming_the_claude_md_line_and_exits_1_when_that_tier_resolves_to_nothing(ready_check, run_cli, fake_processes, tmp_path):
    code, lines = check(ready_check, run_cli, fake_processes, tmp_path, **{ONE_TEST_FILE: (3, "", "")})

    row = one_test_file_row(lines)
    assert row is not None and row.startswith("fail  one test file:"), lines
    assert "veri: one test file: <command>" in row and "CLAUDE.md" in row and '"$1"' in row, row
    assert (code, lines[-1]) == (1, "not ready — 1 rows to fix")


def test_issue_4087_ready_check_fails_the_one_test_file_row_naming_exit_2_when_detect_test_command_gives_no_answer(ready_check, run_cli, fake_processes, tmp_path):
    code, lines = check(ready_check, run_cli, fake_processes, tmp_path, **{ONE_TEST_FILE: (2, "", "")})

    row = one_test_file_row(lines)
    assert row is not None and row.startswith("fail  one test file:"), lines
    assert 'exit 2 from detect-test-command.sh --tier "one test file"' in row, row
    assert (code, lines[-1]) == (1, "not ready — 1 rows to fix")


SSH_ORIGIN = (0, "git@github.com:o/r.git\n", "")
HTTPS_ORIGIN = (0, "https://github.com/o/r.git\n", "")


def user_headers(scopes=None):
    """`gh api -i user`'s answer: a status line and headers, X-Oauth-Scopes listing <scopes> unless None, then the body."""
    scope_line = "" if scopes is None else "X-Oauth-Scopes: %s\r\n" % scopes
    return 0, "HTTP/2.0 200 OK\r\nContent-Type: application/json\r\n%s\r\n{\"login\": \"o\"}" % scope_line, ""


def test_issue_4089_token_scopes_row_is_ok_when_the_header_lists_repo_and_origin_is_not_https(ready_check, fake_processes):
    fake_processes.answers({"gh api -i user": user_headers("gist, repo"), "git remote get-url --push origin": SSH_ORIGIN}, exact=True)

    assert ready_check.token_scopes_row() == ("token scopes", None)


def test_issue_4089_token_scopes_row_over_an_https_origin_fails_without_workflow_its_fix_refreshing_that_scope(ready_check, fake_processes):
    fake_processes.answers({"gh api -i user": user_headers("repo"), "git remote get-url --push origin": HTTPS_ORIGIN}, exact=True)

    assert ready_check.token_scopes_row() == ("token scopes", "gh auth refresh -s workflow")


def test_issue_4089_token_scopes_row_over_an_https_origin_lacking_both_scopes_names_each_in_its_fix(ready_check, fake_processes):
    fake_processes.answers({"gh api -i user": user_headers("gist"), "git remote get-url --push origin": HTTPS_ORIGIN}, exact=True)

    assert ready_check.token_scopes_row() == ("token scopes", "gh auth refresh -s repo,workflow")


def test_issue_4089_token_scopes_row_reads_https_from_origins_push_url_not_its_fetch_url(ready_check, fake_processes):
    fake_processes.answers({"gh api -i user": user_headers("repo"), "git remote get-url --push origin": HTTPS_ORIGIN,
                            "git remote get-url origin": SSH_ORIGIN}, exact=True)

    assert ready_check.token_scopes_row() == ("token scopes", "gh auth refresh -s workflow")


def test_issue_4089_token_scopes_row_with_no_x_oauth_scopes_header_reads_not_verifiable(ready_check, fake_processes):
    fake_processes.answers({"gh api -i user": user_headers(None), "git remote get-url --push origin": SSH_ORIGIN}, exact=True)

    name, verdict = ready_check.token_scopes_row()

    assert (name, verdict) == ("token scopes", "not verifiable")
    assert verdict is ready_check.NOT_VERIFIABLE


def test_issue_4089_token_scopes_row_fails_saying_no_answer_was_obtained_when_gh_api_user_itself_fails(ready_check, fake_processes):
    fake_processes.answers({"gh api -i user": (1, "", "error connecting to api.github.com\n"), "git remote get-url": SSH_ORIGIN})

    assert ready_check.token_scopes_row() == ("token scopes", "no answer was obtained (gh api -i user exited 1)")


def test_issue_4089_token_scopes_row_says_what_github_answered_when_gh_api_user_gets_a_non_2xx_status(ready_check, fake_processes):
    unauthorized = "HTTP/2.0 401 Unauthorized\r\nContent-Type: application/json\r\n\r\n{\"message\": \"Bad credentials\"}"
    fake_processes.answers({"gh api -i user": (1, unauthorized, "gh: Bad credentials (HTTP 401)\n"), "git remote get-url": SSH_ORIGIN})

    name, fix = ready_check.token_scopes_row()

    assert name == "token scopes" and "HTTP/2.0 401 Unauthorized" in fix and "no answer" not in fix, fix


NOT_FOUND = (1,'{"message": "Not Found", "status": "404"}', "gh: Not Found (HTTP 404)\n")


def test_issue_4089_the_label_row_for_veri_priority_label_is_ok_when_it_answers_and_fails_on_404_with_gh_label_create(ready_check, fake_processes, monkeypatch):
    monkeypatch.setenv("VERI_PRIORITY_LABEL", "urgent")
    fake_processes.answers({"gh api repos/{owner}/{repo}/labels/urgent": [(0, '{"name": "urgent"}', ""), NOT_FOUND]}, exact=True)

    assert ready_check.priority_label_row() == ("label urgent", None)
    assert ready_check.priority_label_row() == ("label urgent", "gh label create urgent")


def test_issue_4089_the_label_bug_row_is_ok_when_it_answers_and_fails_on_404_with_gh_label_create_bug(ready_check, fake_processes):
    fake_processes.answers({"gh api repos/{owner}/{repo}/labels/bug": [(0, '{"name": "bug"}', ""), NOT_FOUND]}, exact=True)

    assert ready_check.bug_label_row() == ("label bug", None)
    assert ready_check.bug_label_row() == ("label bug", "gh label create bug")


def test_issue_4089_a_label_row_whose_call_fails_other_than_404_says_no_answer_was_obtained_not_gh_label_create(ready_check, fake_processes):
    fake_processes.answers({"gh api repos/{owner}/{repo}/labels/bug": (1, "", "gh: Bad Gateway (HTTP 502)\n")}, exact=True)

    name, fix = ready_check.bug_label_row()

    assert name == "label bug" and fix.startswith("no answer was obtained") and "gh label create" not in fix, fix


def test_issue_4089_a_label_row_encodes_the_name_in_the_api_path_and_quotes_it_in_the_fix(ready_check, fake_processes, monkeypatch):
    monkeypatch.setenv("VERI_PRIORITY_LABEL", "needs triage/a")
    fake_processes.answers({"gh api repos/{owner}/{repo}/labels/needs%20triage%2Fa": [(0, "{}", ""), NOT_FOUND]}, exact=True)

    assert ready_check.priority_label_row() == ("label needs triage/a", None)
    assert ready_check.priority_label_row() == ("label needs triage/a", "gh label create 'needs triage/a'")


ACTIONS_RUNS = "gh api repos/{owner}/{repo}/actions/runs?per_page=1"
WITH_WORKFLOWS = {"git symbolic-ref": (0, "origin/main\n", ""), "git ls-tree": (0, ".github/workflows/ci.yml\n", "")}


def test_issue_4089_the_actions_read_row_is_ok_when_the_runs_call_exits_0_and_fails_otherwise(ready_check, fake_processes):
    fake_processes.answers({**WITH_WORKFLOWS, ACTIONS_RUNS: [(0, '{"workflow_runs": []}', ""), (1, "", "gh: Resource not accessible by integration (HTTP 403)\n")]})

    assert ready_check.actions_read_row() == ("actions read", None)
    name, fix = ready_check.actions_read_row()
    assert name == "actions read" and fix and "actions: read" in fix, fix


def test_issue_4089_the_actions_read_row_reads_skipped_with_no_workflows_at_the_default_branch_tip(ready_check, fake_processes):
    fake_processes.answers({"git symbolic-ref": (0, "origin/main\n", ""), "git ls-tree": (0, "", "")})

    name, verdict = ready_check.actions_read_row()

    assert (name, verdict) == ("actions read", "skipped")
    assert verdict is ready_check.SKIPPED


RUN_STATE_RULE = (".tdd/*\n!.tdd/issue-*.md\n.tdd/issue-*-*.md\n!.tdd/issue-*-added.md\n!.tdd/issue-*-mutations.md\n"
                  "!.tdd/issue-*-refactor-owed.md\n!.tdd/issue-*-metrics.md\n")


def unwritable(monkeypatch, denied):
    """os.access answering W_OK for a path in <denied> as a non-root user meets a read-only file (chmod is no proof,
    since uid 0 ignores it)."""
    real_access = os.access

    def access(path, mode, *rest, **kwargs):
        if mode & os.W_OK and os.path.realpath(path) in denied:
            return False
        return real_access(path, mode, *rest, **kwargs)
    monkeypatch.setattr(os, "access", access)


def test_issue_4089_the_run_state_ignore_row_is_ok_when_each_file_carries_the_rule_or_is_writable_and_fails_naming_the_one_that_is_neither(ready_check, fake_processes, tmp_path, monkeypatch):
    common = tmp_path / "common.git"
    (common / "info").mkdir(parents=True)
    exclude = common / "info" / "exclude"
    exclude.write_text("# git ls-files --others --exclude-from=.git/info/exclude\n")
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text(RUN_STATE_RULE)
    denied = {os.path.realpath(gitignore)}
    unwritable(monkeypatch, denied)
    fake_processes.answers({"git rev-parse --git-common-dir": (0, str(common) + "\n", "")}, exact=True)

    assert ready_check.run_state_ignore_row() == ("run-state ignore", None)
    denied.add(os.path.realpath(exclude))
    name, fix = ready_check.run_state_ignore_row()
    assert name == "run-state ignore" and fix and str(exclude) in fix and ".gitignore" not in fix, fix


def test_issue_4089_the_run_state_ignore_row_fails_naming_a_file_that_carries_the_rule_only_in_part(ready_check, fake_processes, tmp_path):
    common = tmp_path / "common.git"
    (common / "info").mkdir(parents=True)
    (common / "info" / "exclude").write_text(RUN_STATE_RULE)
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("!.tdd/issue-*-metrics.md\n")
    fake_processes.answers({"git rev-parse --git-common-dir": (0, str(common) + "\n", "")}, exact=True)

    name, fix = ready_check.run_state_ignore_row()

    assert name == "run-state ignore" and fix and str(gitignore) in fix and "in part" in fix.reason, (fix, fix.reason)


def test_4338_the_run_state_ignore_fix_for_a_partial_rule_names_the_rules_lines_without_counting_them(ready_check, fake_processes, tmp_path):
    (tmp_path / "common.git" / "info").mkdir(parents=True)
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("!.tdd/issue-*-metrics.md\n")
    fake_processes.answers({"git rev-parse --git-common-dir": (0, str(tmp_path / "common.git") + "\n", "")}, exact=True)

    name, fix = ready_check.run_state_ignore_row()

    assert (name, fix.reason) == ("run-state ignore", f"{gitignore} carries veri's run-state rule only in part, or out of "
                                                      "order: complete those lines, in that order, or remove them")


def test_issue_4089_the_run_state_ignore_row_writes_nothing_to_stderr_for_a_partial_rule(ready_check, fake_processes, tmp_path, capsys):
    (tmp_path / "common.git" / "info").mkdir(parents=True)
    (tmp_path / ".gitignore").write_text("!.tdd/issue-*-metrics.md\n")
    fake_processes.answers({"git rev-parse --git-common-dir": (0, str(tmp_path / "common.git") + "\n", "")}, exact=True)

    name, fix = ready_check.run_state_ignore_row()

    assert name == "run-state ignore" and fix.startswith("grep -nF"), fix
    assert capsys.readouterr().err == ""


def test_issue_4089_ready_check_prints_the_new_rows_and_counts_a_not_verifiable_or_skipped_row_as_no_fail(ready_check, run_cli, fake_processes, tmp_path, monkeypatch):
    monkeypatch.setenv("VERI_CI_ON_PR", "1")
    code, lines = check(ready_check, run_cli, fake_processes, tmp_path, **{
        "git ls-tree": (0, "", ""), "gh api -i user": user_headers(None), ONE_TEST_FILE: (0, 'pytest "$1"\n', "")})

    for row in ("not verifiable  token scopes", "ok    label priority", "ok    label bug", "skipped  actions read", "ok    run-state ignore"):
        assert row in lines, (row, lines)
    assert [line for line in lines if line.startswith("fail")] == [
        "fail  push: add a workflow under .github/workflows/ that triggers on push to the default branch"], lines
    assert (code, lines[-1]) == (1, "not ready — 1 rows to fix")


def tree_state(root):
    return {os.path.join(d, f): open(os.path.join(d, f), "rb").read() for d, _, files in os.walk(root) for f in files}


WRITING_FLAGS = ("-f", "-F", "--field", "--raw-field", "--input")


def test_issue_4089_the_new_rows_failing_make_only_rest_reads_through_gh_and_git_write_no_file_and_name_one_command_or_settings_key_each(ready_check, fake_processes, tmp_path, monkeypatch):
    repo = tmp_path / "my repo"
    common = repo / ".git"
    (common / "info").mkdir(parents=True)
    (common / "info" / "exclude").write_text("")
    (repo / ".gitignore").write_text("")
    monkeypatch.chdir(repo)
    unwritable(monkeypatch, {os.path.realpath(repo / ".gitignore"), os.path.realpath(common / "info" / "exclude")})
    fake = fake_processes.answers({
        "gh api -i user": user_headers("gist"), "git remote get-url --push origin": HTTPS_ORIGIN,
        "gh api repos/{owner}/{repo}/labels/": NOT_FOUND, **WITH_WORKFLOWS,
        ACTIONS_RUNS: (1, "", "gh: Resource not accessible by integration (HTTP 403)\n"),
        "git rev-parse --git-common-dir": (0, str(common) + "\n", "")})
    before = tree_state(tmp_path)

    rows = [row() for row in (ready_check.token_scopes_row, ready_check.priority_label_row, ready_check.bug_label_row,
                              ready_check.actions_read_row, ready_check.run_state_ignore_row)]

    assert tree_state(tmp_path) == before
    assert {argv[0] for argv in fake.argvs} == {"gh", "git"}, fake.calls
    for argv in (a for a in fake.argvs if a[0] == "gh"):
        assert argv[1] == "api" and "graphql" not in argv, argv
        assert not any(flag in argv for flag in WRITING_FLAGS), argv
        methods = [argv[i + 1] for i, arg in enumerate(argv[:-1]) if arg in ("-X", "--method")]
        assert set(methods) <= {"GET"}, argv
    (repo / ".gitignore").write_text("!.tdd/issue-*-metrics.md\n")
    partial = tree_state(tmp_path)
    rows.append(ready_check.run_state_ignore_row())
    assert tree_state(tmp_path) == partial
    assert all(fix for _, fix in rows), rows
    for name, fix in rows:
        words = shlex.split(fix) if "`" not in fix else []
        one_command = ("\n" not in fix and "—" not in fix and words and words[0] in ("gh", "chmod", "grep")
                       and not any(word in (";", "&&", "||", "|") for word in words))
        settings_key = "\n" not in fix and fix.count("`") == 2
        assert one_command or settings_key, (name, fix)
        if words and words[0] in ("chmod", "grep"):
            assert words[-1] == os.path.abspath(".gitignore"), (name, fix)


PROBE_PUSH = "git push --dry-run --no-verify origin HEAD:refs/heads/veri-permission-probe-"
SSH_CONFIG = "git config --get core.sshCommand"
NO_SSH_CONFIG = {SSH_CONFIG: (1, "", "")}


def push_calls(fake):
    """(argv, kwargs) of each `git push` the fake saw."""
    return [(argv, kwargs) for argv, kwargs in fake.seen if "push" in argv]


def test_issue_4090_the_push_dry_run_row_is_ok_when_a_dry_run_push_to_a_probe_branch_exits_0(ready_check, fake_processes):
    fake = fake_processes.answers({**NO_SSH_CONFIG, PROBE_PUSH: (0, "", "To github.com:o/r.git\n * [new branch]      HEAD -> veri-permission-probe-1a2b\n")})

    assert ready_check.push_dry_run_row() == ("push dry-run", None)
    pushes = [argv for argv, _ in push_calls(fake)]
    assert len(pushes) == 1 and re.fullmatch(r"HEAD:refs/heads/veri-permission-probe-\w+", pushes[0][-1]), fake.calls


REFUSED = (128, "", "remote: Permission to o/r.git denied to someone.\nfatal: unable to access 'https://github.com/o/r.git/': The requested URL returned error: 403\n\n")


def test_issue_4090_the_push_dry_run_row_fails_on_a_refused_dry_run_carrying_gits_last_non_empty_stderr_line(ready_check, fake_processes):
    fake_processes.answers({**NO_SSH_CONFIG, PROBE_PUSH: REFUSED})

    assert ready_check.push_dry_run_row() == (
        "push dry-run", "fatal: unable to access 'https://github.com/o/r.git/': The requested URL returned error: 403")


def test_issue_4090_the_dry_run_push_runs_with_git_terminal_prompt_0_so_missing_credentials_fail_instead_of_prompting(ready_check, fake_processes, monkeypatch):
    monkeypatch.setenv("GIT_TERMINAL_PROMPT", "1")
    fake = fake_processes.answers({**NO_SSH_CONFIG, PROBE_PUSH: (128, "", "fatal: could not read Username for 'https://github.com': terminal prompts disabled\n")})

    assert ready_check.push_dry_run_row() == ("push dry-run", "fatal: could not read Username for 'https://github.com': terminal prompts disabled")
    (argv, kwargs), = push_calls(fake)
    assert (kwargs.get("env") or {}).get("GIT_TERMINAL_PROMPT") == "0", kwargs


def test_issue_4090_the_push_dry_run_row_starts_only_git_and_every_push_is_a_dry_run_to_a_fresh_probe_name(ready_check, fake_processes):
    fake = fake_processes.answers({PROBE_PUSH: [(0, "", ""), REFUSED]}, default=(0, "", ""))

    ready_check.push_dry_run_row()
    ready_check.push_dry_run_row()

    assert {argv[0] for argv in fake.argvs} == {"git"}, fake.calls
    pushes = [argv for argv in fake.argvs if "push" in argv]
    assert len(pushes) == 2 and all("--dry-run" in argv and "--delete" not in argv for argv in pushes), fake.calls
    assert all(re.fullmatch(r"HEAD:refs/heads/veri-permission-probe-\w+", argv[-1]) for argv in pushes), fake.calls
    assert pushes[0][-1] != pushes[1][-1], fake.calls
    assert all(argv[1] in ("push", "config") for argv in fake.argvs), fake.calls


def test_issue_4090_every_push_the_push_dry_run_row_makes_carries_dry_run_and_no_verify_so_no_pre_push_hook_runs(ready_check, fake_processes):
    fake = fake_processes.answers({}, default=(0, "", ""))

    ready_check.push_dry_run_row()

    pushes = [argv for argv in fake.argvs if "push" in argv]
    assert pushes and all("--dry-run" in argv and "--no-verify" in argv for argv in pushes), fake.calls


def test_issue_4090_the_dry_run_push_runs_ssh_in_batch_mode_unless_git_ssh_command_is_set(ready_check, fake_processes, monkeypatch):
    fake = fake_processes.answers({**NO_SSH_CONFIG, PROBE_PUSH: (0, "", "")})
    monkeypatch.delenv("GIT_SSH_COMMAND", raising=False)
    monkeypatch.delenv("GIT_SSH", raising=False)
    ready_check.push_dry_run_row()
    monkeypatch.setenv("GIT_SSH_COMMAND", "ssh -i ~/.ssh/deploy")
    ready_check.push_dry_run_row()

    commands = [(kwargs.get("env") or {}).get("GIT_SSH_COMMAND") for _, kwargs in push_calls(fake)]
    assert commands == ["ssh -o BatchMode=yes", "ssh -i ~/.ssh/deploy"], commands


def test_issue_4090_the_dry_run_push_adds_no_batch_mode_ssh_command_when_git_ssh_is_set(ready_check, fake_processes, monkeypatch):
    fake = fake_processes.answers({**NO_SSH_CONFIG, PROBE_PUSH: (0, "", "")})
    monkeypatch.delenv("GIT_SSH_COMMAND", raising=False)
    monkeypatch.setenv("GIT_SSH", "/usr/local/bin/my-ssh")

    ready_check.push_dry_run_row()

    (_, kwargs), = push_calls(fake)
    assert "GIT_SSH_COMMAND" not in (kwargs.get("env") or {}), kwargs.get("env")


def test_issue_4090_the_dry_run_push_adds_no_batch_mode_ssh_command_when_core_ssh_command_is_configured(ready_check, fake_processes, monkeypatch):
    fake = fake_processes.answers({SSH_CONFIG: (0, "ssh -i ~/.ssh/deploy\n", ""), PROBE_PUSH: (0, "", "")})
    monkeypatch.delenv("GIT_SSH_COMMAND", raising=False)
    monkeypatch.delenv("GIT_SSH", raising=False)

    ready_check.push_dry_run_row()

    (_, kwargs), = push_calls(fake)
    assert "GIT_SSH_COMMAND" not in (kwargs.get("env") or {}), kwargs.get("env")


def test_issue_4090_a_dry_run_push_that_never_answers_fails_the_row_naming_the_veri_gh_timeout_limit(ready_check, fake_processes, monkeypatch):
    from process_fakes import HANGS
    monkeypatch.setenv("VERI_GH_TIMEOUT", "7")
    fake = fake_processes.answers({**NO_SSH_CONFIG, PROBE_PUSH: HANGS})
    monkeypatch.setattr(os, "killpg", lambda group, sig: [c.send_signal(sig) for c in fake.popens if c.pid == group])

    name, fix = ready_check.push_dry_run_row()

    assert name == "push dry-run" and fix and "no answer after 7s (VERI_GH_TIMEOUT)" in fix, fix


def test_issue_4090_ready_check_prints_a_failing_push_dry_run_row_and_exits_1_when_origin_refuses_the_dry_run(ready_check, run_cli, fake_processes, tmp_path):
    code, lines = check(ready_check, run_cli, fake_processes, tmp_path, **{PROBE_PUSH: REFUSED})

    assert [line for line in lines if line.startswith("fail")] == [
        "fail  push dry-run: fatal: unable to access 'https://github.com/o/r.git/': The requested URL returned error: 403"], lines
    assert (code, lines[-1]) == (1, "not ready — 1 rows to fix")


TIERS = {"detect-test-command.sh --tier fast": (0, "make unit\n", ""), "detect-test-command.sh --tier all": (0, "make test\n", "")}


def calls_in(fake, prefix):
    """(argv, cwd) of each call whose command line starts with <prefix>."""
    return [(argv, kwargs.get("cwd")) for argv, kwargs in fake.seen
            if " ".join([os.path.basename(argv[0]), *map(str, argv[1:])]).startswith(prefix)]


def test_issue_4088_each_resolved_tier_runs_in_a_detached_worktree_of_the_default_tip_through_detach_command_and_prints_an_ok_tier_run_row(ready_check, run_cli, fake_processes, tmp_path):
    fake = fake_processes.answers(holding(**TIERS))
    home = tmp_path / "scratch-home"
    home.mkdir()
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "settings.json").write_text(json.dumps({"permissions": {"defaultMode": "bypassPermissions"}}))
    code, out, _ = run_cli(ready_check, [str(tmp_path)], env={"VERI_BASH_MAJOR": "5", "HOME": str(home)})
    lines = out.splitlines()

    for tier, command in (("fast", ["make", "unit"]), ("all", ["make", "test"])):
        wt = str(tmp_path / ".tdd" / f"ready-{tier}")
        assert any(row.startswith(f"ok    {tier} tier run") for row in lines), (tier, lines)
        added = [argv for argv, _ in calls_in(fake, "git worktree add") if wt in argv]
        assert added and "--detach" in added[0] and added[0][-1] == "c0ffee", fake.calls
        assert "git rev-parse --verify --quiet refs/remotes/origin/main^{commit}" in fake.calls, fake.calls
        starts = calls_in(fake, f"detach-command.sh start ready-{tier} ")
        assert [(argv[3:], cwd) for argv, cwd in starts] == [(command, wt)], fake.calls
        assert [cwd for _, cwd in calls_in(fake, f"detach-command.sh wait ready-{tier}")] == [wt], fake.calls
    assert (code, lines[-1]) == (0, "ready")


def writing_output(tier, text):
    """A detach-command.sh start answer that leaves <text> as ready-<tier>'s output in its working directory."""
    def start(line, cwd=None, **kwargs):
        with open(os.path.join(cwd, ".tdd", f"ready-{tier}.out"), "w") as out:
            out.write(text)
        return 0, "", ""
    return start


def tier_run_line(lines, tier):
    return next((line for line in lines if f"{tier} tier run" in line), None)


def test_issue_4088_a_tier_exiting_non_zero_fails_its_row_carrying_the_exit_code_and_the_outputs_last_non_empty_line(ready_check, run_cli, fake_processes, tmp_path):
    code, lines = check(ready_check, run_cli, fake_processes, tmp_path, **TIERS, **{
        "detach-command.sh start ready-fast": writing_output("fast", "collected 3 items\nFAILED tests/test_x.py::test_y\n\n  \n"),
        "detach-command.sh wait ready-fast": (1, "7\n", "")})

    row = tier_run_line(lines, "fast")
    assert row is not None and row.startswith("fail  fast tier run"), lines
    assert "exit 7" in row and row.endswith("FAILED tests/test_x.py::test_y"), row
    assert tier_run_line(lines, "all").startswith("ok    all tier run"), lines
    assert (code, lines[-1]) == (1, "not ready — 1 rows to fix")


def test_issue_4088_each_tier_run_row_carries_its_wall_time_in_whole_seconds_whether_it_passed_or_failed(ready_check, run_cli, fake_processes, tmp_path, monkeypatch):
    import types
    clock = iter([1000.0, 1042.6, 2000.0, 2003.2])
    monkeypatch.setattr(ready_check, "time", types.SimpleNamespace(time=lambda: next(clock), monotonic=lambda: 0.0), raising=False)
    code, lines = check(ready_check, run_cli, fake_processes, tmp_path, **TIERS, **{
        "detach-command.sh wait ready-all": (1, "1\n", "")})

    assert tier_run_line(lines, "fast") == "ok    fast tier run (42s)", lines
    assert tier_run_line(lines, "all").startswith("fail  all tier run (3s): exit 1"), lines
    assert (code, lines[-1]) == (1, "not ready — 1 rows to fix")


@pytest.mark.parametrize("unresolved", [3, 2])
def test_issue_4088_a_tier_that_resolves_to_nothing_prints_no_tier_run_row_and_starts_no_worktree_or_command(ready_check, run_cli, fake_processes, tmp_path, unresolved):
    fake = fake_processes.answers(holding(**{**TIERS, "detect-test-command.sh --tier all": (unresolved, "", "")}))
    home = tmp_path / "scratch-home"
    home.mkdir()
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "settings.json").write_text(json.dumps({"permissions": {"defaultMode": "bypassPermissions"}}))
    code, out, _ = run_cli(ready_check, [str(tmp_path)], env={"VERI_BASH_MAJOR": "5", "HOME": str(home)})
    lines = out.splitlines()

    assert tier_run_line(lines, "all") is None, lines
    assert tier_run_line(lines, "fast").startswith("ok    fast tier run"), lines
    assert not [c for c in fake.calls if "ready-all" in c], fake.calls
    assert (code, lines[-1]) == (1, "not ready — 1 rows to fix")


def test_issue_4088_a_red_tiers_whole_output_is_kept_at_tdd_ready_tier_out_in_the_main_working_tree(ready_check, run_cli, fake_processes, tmp_path):
    output = "collected 3 items\n\nFAILED tests/test_x.py::test_y - assert 1 == 2\n1 failed\n"
    check(ready_check, run_cli, fake_processes, tmp_path, **TIERS, **{
        "detach-command.sh start ready-all": writing_output("all", output), "detach-command.sh wait ready-all": (1, "1\n", "")})

    assert (tmp_path / ".tdd" / "ready-all.out").read_text() == output
    assert not (tmp_path / ".tdd" / "ready-fast.out").exists()


def test_issue_4088_a_green_tier_leaves_no_tdd_ready_tier_out_in_the_main_working_tree_removing_an_older_one(ready_check, run_cli, fake_processes, tmp_path):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "ready-fast.out").write_text("an earlier red run\n")

    code, lines = check(ready_check, run_cli, fake_processes, tmp_path, **TIERS)

    assert (code, lines[-1]) == (0, "ready")
    assert not (tmp_path / ".tdd" / "ready-fast.out").exists()


def test_issue_4088_a_tier_still_running_at_waits_bound_prints_waiting_on_it_last_exits_3_and_leaves_its_worktree(ready_check, run_cli, fake_processes, tmp_path):
    fake = fake_processes.answers(holding(**TIERS, **{"detach-command.sh wait ready-fast": (3, "", "")}))
    code, out, _ = run_cli(ready_check, [str(tmp_path)], env={"VERI_BASH_MAJOR": "5"})
    lines = out.splitlines()

    assert (code, lines[-1]) == (3, "waiting on ready-fast"), lines
    assert not [line for line in lines if line == "ready" or line.startswith("not ready")], lines
    assert not [argv for argv, _ in calls_in(fake, "git worktree remove") if str(tmp_path / ".tdd" / "ready-fast") in argv], fake.calls


def test_issue_4088_a_re_run_while_a_tier_is_still_running_waits_on_that_run_and_reports_its_exit_and_wall_time(ready_check, run_cli, fake_processes, tmp_path, monkeypatch):
    import types
    clock = iter([1000.0, 1100.4, 1100.4, 1105.0])
    monkeypatch.setattr(ready_check, "time", types.SimpleNamespace(time=lambda: next(clock), monotonic=lambda: 0.0), raising=False)
    fake_processes.answers(holding(**TIERS, **{"detach-command.sh wait ready-fast": (3, "", ""), "git worktree list": listing(tmp_path),
                                               "detach-command.sh start ready-fast": running_suite("fast")}))
    home = tmp_path / "scratch-home"
    home.mkdir()
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "settings.json").write_text(json.dumps({"permissions": {"defaultMode": "bypassPermissions"}}))
    first, _, _ = run_cli(ready_check, [str(tmp_path)], env={"VERI_BASH_MAJOR": "5", "HOME": str(home)})
    fake = fake_processes.answers(holding(**TIERS, **{"detach-command.sh wait ready-fast": (1, "4\n", ""), "git worktree list": listing(tmp_path, "fast"),
                                                      LSTART: (0, STARTED + "\n", "")}))
    code, out, _ = run_cli(ready_check, [str(tmp_path)], env={"VERI_BASH_MAJOR": "5", "HOME": str(home)})
    lines = out.splitlines()

    assert first == 3
    assert not calls_in(fake, "detach-command.sh start ready-fast"), fake.calls
    assert not [argv for argv, _ in calls_in(fake, "git worktree add") if str(tmp_path / ".tdd" / "ready-fast") in argv], fake.calls
    assert calls_in(fake, "detach-command.sh wait ready-fast"), fake.calls
    assert tier_run_line(lines, "fast").startswith("fail  fast tier run (100s): exit 4"), lines
    assert tier_run_line(lines, "all") == "ok    all tier run (4s)", lines
    assert (code, lines[-1]) == (1, "not ready — 1 rows to fix")


def test_issue_4088_a_tier_whose_run_died_without_recording_an_exit_fails_its_row_saying_no_answer_was_obtained(ready_check, run_cli, fake_processes, tmp_path):
    code, lines = check(ready_check, run_cli, fake_processes, tmp_path, **TIERS, **{"detach-command.sh wait ready-all": (2, "", "")})

    row = tier_run_line(lines, "all")
    assert row.startswith("fail  all tier run (") and row.endswith(
        "s): no answer was obtained (exit 2 from detach-command.sh wait ready-all)"), row
    assert (code, lines[-1]) == (1, "not ready — 1 rows to fix")


def test_issue_4088_both_tiers_share_one_wait_bound_per_call_the_second_waiting_only_what_the_first_left(ready_check, run_cli, fake_processes, tmp_path, monkeypatch):
    import types
    import time
    ticks = iter([0.0, 0.0, 0.0, 0.0])
    monkeypatch.setattr(ready_check, "time", types.SimpleNamespace(time=time.time, monotonic=lambda: next(ticks, 400.0)), raising=False)
    fake = fake_processes.answers(holding(**TIERS))
    run_cli(ready_check, [str(tmp_path)], env={"VERI_BASH_MAJOR": "5"})

    assert [argv[3:] for argv, _ in calls_in(fake, "detach-command.sh wait ready-fast")] == [["560"]], fake.calls
    assert [argv[3:] for argv, _ in calls_in(fake, "detach-command.sh wait ready-all")] == [["160"]], fake.calls


def test_issue_4088_one_deadline_from_the_calls_start_bounds_the_permission_probe_and_both_tiers(ready_check, run_cli, fake_processes, tmp_path, monkeypatch):
    import types
    import time
    ticks = iter([0.0])
    monkeypatch.setattr(ready_check, "time", types.SimpleNamespace(time=time.time, monotonic=lambda: next(ticks, 400.0)), raising=False)
    timeouts = []

    def probe(line, **kwargs):
        timeouts.append(kwargs.get("timeout"))
        return probe_answer()(line, **kwargs)
    fake = fake_processes.answers(holding(**TIERS, **{PROBE: probe}))
    run_cli(ready_check, [str(tmp_path)], env={"VERI_BASH_MAJOR": "5"})

    assert timeouts == [160], timeouts
    assert [argv[3:] for argv, _ in calls_in(fake, "detach-command.sh wait ready-fast")] == [["160"]], fake.calls
    assert [argv[3:] for argv, _ in calls_in(fake, "detach-command.sh wait ready-all")] == [["160"]], fake.calls


def test_issue_4088_a_tiers_wall_time_ends_when_its_command_recorded_its_exit_not_when_a_later_call_read_it(ready_check, run_cli, fake_processes, tmp_path, monkeypatch):
    import types
    clock = iter([1000.0, 5000.0])
    monkeypatch.setattr(ready_check, "time", types.SimpleNamespace(time=lambda: next(clock, 5004.0), monotonic=lambda: 0.0), raising=False)

    def recorded_at_1030(line, cwd=None, **kwargs):
        exit_file = os.path.join(cwd, ".tdd", "ready-fast.exit")
        with open(exit_file, "w") as f:
            f.write("0\n")
        os.utime(exit_file, (1030.0, 1030.0))
        return 0, "", ""
    code, lines = check(ready_check, run_cli, fake_processes, tmp_path, **TIERS, **{"detach-command.sh wait ready-fast": recorded_at_1030})

    assert tier_run_line(lines, "fast") == "ok    fast tier run (30s)", lines
    assert tier_run_line(lines, "all") == "ok    all tier run (4s)", lines


@pytest.mark.parametrize("failing, said", [
    ({"git rev-parse --verify": (1, "", "")}, "refs/remotes/origin/main"),
    ({"git worktree add": (128, "", "fatal: invalid reference: c0ffee\n")}, "fatal: invalid reference: c0ffee")])
def test_issue_4088_a_default_tip_that_does_not_resolve_or_a_failing_worktree_add_fails_the_row_starting_and_creating_nothing(ready_check, run_cli, fake_processes, tmp_path, failing, said):
    fake = fake_processes.answers(holding(**TIERS, **failing))
    code, out, _ = run_cli(ready_check, [str(tmp_path)], env={"VERI_BASH_MAJOR": "5"})
    lines = out.splitlines()

    row = tier_run_line(lines, "fast")
    assert row is not None and row.startswith("fail  fast tier run: no answer was obtained") and said in row, lines
    assert not calls_in(fake, "detach-command.sh start"), fake.calls
    assert not (tmp_path / ".tdd" / "ready-fast").exists() and not (tmp_path / ".tdd" / "ready-all").exists()
    assert code == 1


def listing(tmp_path, *tiers):
    """`git worktree list --porcelain`'s answer: the main tree and a detached tier worktree per <tiers>."""
    text = f"worktree {tmp_path}\nHEAD c0ffee\nbranch refs/heads/main\n\n"
    for tier in tiers:
        text += f"worktree {tmp_path / '.tdd' / ('ready-' + tier)}\nHEAD c0ffee\ndetached\n\n"
    return 0, text, ""


def test_issue_4088_a_plain_directory_left_at_a_tier_worktrees_path_is_not_reused_and_fails_the_row_naming_it(ready_check, run_cli, fake_processes, tmp_path):
    left = tmp_path / ".tdd" / "ready-fast" / ".tdd"
    left.mkdir(parents=True)
    (left / "ready-fast.began").write_text("1000.0")
    (left / "ready-fast.exit").write_text("0\n")
    fake = fake_processes.answers(holding(**TIERS, **{"git worktree list": listing(tmp_path)}))
    code, out, _ = run_cli(ready_check, [str(tmp_path)], env={"VERI_BASH_MAJOR": "5"})
    lines = out.splitlines()

    row = tier_run_line(lines, "fast")
    assert row.startswith("fail  fast tier run:") and str(tmp_path / ".tdd" / "ready-fast") in row, lines
    assert not calls_in(fake, "detach-command.sh start ready-fast") and not calls_in(fake, "detach-command.sh wait ready-fast"), fake.calls
    assert not [argv for argv, _ in calls_in(fake, "git worktree remove") if str(tmp_path / ".tdd" / "ready-fast") in argv], fake.calls
    assert (left / "ready-fast.began").read_text() == "1000.0"
    assert code == 1


@pytest.mark.parametrize("changed", [{"git rev-parse --verify": (0, "beef00\n", "")},
                                     {"detect-test-command.sh --tier fast": (0, "make unit-fast\n", "")}])
def test_issue_4088_a_tier_worktree_left_for_another_tip_or_command_is_not_reused_but_replaced_by_a_fresh_run(ready_check, run_cli, fake_processes, tmp_path, changed):
    wt = str(tmp_path / ".tdd" / "ready-fast")
    fake_processes.answers(holding(**TIERS, **{"detach-command.sh wait ready-fast": (3, "", ""), "git worktree list": listing(tmp_path, "fast"),
                                               "detach-command.sh start ready-fast": ended_suite("fast")}))
    first, _, _ = run_cli(ready_check, [str(tmp_path)], env={"VERI_BASH_MAJOR": "5"})
    fake = fake_processes.answers(holding(**{**TIERS, "git worktree list": listing(tmp_path, "fast"), **changed}))
    code, out, _ = run_cli(ready_check, [str(tmp_path)], env={"VERI_BASH_MAJOR": "5"})

    assert first == 3
    removed = [i for i, (argv, _) in enumerate(fake.seen) if argv[:3] == ["git", "worktree", "remove"] and wt in argv]
    added = [i for i, (argv, _) in enumerate(fake.seen) if argv[:3] == ["git", "worktree", "add"] and wt in argv]
    assert removed and added and removed[0] < added[0], fake.calls
    assert calls_in(fake, "detach-command.sh start ready-fast"), fake.calls
    assert tier_run_line(out.splitlines(), "fast").startswith("ok    fast tier run"), out


def test_issue_4092_ready_check_no_suites_is_accepted_prints_no_tier_run_row_and_runs_no_tier(ready_check, run_cli, fake_processes, tmp_path):
    fake = fake_processes.answers(holding(**TIERS))
    home = tmp_path / "scratch-home"
    home.mkdir()
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "settings.json").write_text(json.dumps({"permissions": {"defaultMode": "bypassPermissions"}}))
    code, out, err = run_cli(ready_check, ["--no-suites", str(tmp_path)], env={"VERI_BASH_MAJOR": "5", "HOME": str(home)})
    lines = out.splitlines()

    assert (code, lines[-1]) == (0, "ready"), (out, err)
    assert "ok    fast tier" in lines and "ok    all tier" in lines, lines
    assert not [line for line in lines if "tier run" in line], lines
    assert not [c for c in fake.calls if "detach-command.sh" in c or "git worktree" in c], fake.calls


def test_issue_4088_an_exception_after_a_tier_started_exits_2_leaving_its_worktree_and_record_for_the_re_run(ready_check, run_cli, fake_processes, tmp_path):
    fake = fake_processes.answers(holding(**TIERS, **{"detach-command.sh wait ready-fast": OSError(7, "no detach")}))
    code, _, _ = run_cli(ready_check, [str(tmp_path)], env={"VERI_BASH_MAJOR": "5"})

    wt = tmp_path / ".tdd" / "ready-fast"
    assert code == 2
    assert not [argv for argv, _ in calls_in(fake, "git worktree remove") if str(wt) in argv], fake.calls
    assert (wt / ".tdd" / "ready-fast.record").exists()


def test_issue_4088_an_interrupt_during_a_tiers_start_leaves_its_worktree_and_record_since_the_suite_may_have_started(ready_check, run_cli, fake_processes, tmp_path):
    fake = fake_processes.answers(holding(**TIERS, **{"detach-command.sh start ready-fast": KeyboardInterrupt()}))
    with pytest.raises(KeyboardInterrupt):
        run_cli(ready_check, [str(tmp_path)], env={"VERI_BASH_MAJOR": "5"})

    wt = tmp_path / ".tdd" / "ready-fast"
    assert not [argv for argv, _ in calls_in(fake, "git worktree remove") if str(wt) in argv], fake.calls
    assert (wt / ".tdd" / "ready-fast.record").exists()


STARTED = "Mon Nov 16 10:00:00 2026"
LSTART = "ps -o lstart= -p"


def leave_tier(tmp_path, tier="fast", tip="c0ffee", command="make unit", pid=None, started=STARTED, exit_code=None):
    """A tier worktree an earlier call left: its record, and the pid file and exit file detach-command.sh writes."""
    tdd = tmp_path / ".tdd" / f"ready-{tier}" / ".tdd"
    tdd.mkdir(parents=True)
    (tdd / f"ready-{tier}.record").write_text(f"1000.0\n{tip}\n{command}\n")
    if pid is not None:
        (tdd / f"ready-{tier}.pid").write_text(f"{pid}\n{started}\n")
    if exit_code is not None:
        (tdd / f"ready-{tier}.exit").write_text(f"{exit_code}\n")
    return tmp_path / ".tdd" / f"ready-{tier}"


def test_issue_4088_a_stale_tier_worktree_whose_run_still_goes_is_not_removed_and_fails_the_row_naming_it(ready_check, run_cli, fake_processes, tmp_path):
    wt = leave_tier(tmp_path, tip="0ld0ld", pid=os.getpid())
    fake = fake_processes.answers(holding(**TIERS, **{"git worktree list": listing(tmp_path, "fast"), LSTART: (0, STARTED + "\n", "")}))
    code, out, _ = run_cli(ready_check, [str(tmp_path)], env={"VERI_BASH_MAJOR": "5"})

    row = tier_run_line(out.splitlines(), "fast")
    assert row.startswith("fail  fast tier run:") and str(wt) in row, out
    assert not [argv for argv, _ in calls_in(fake, "git worktree remove") if str(wt) in argv], fake.calls
    assert not calls_in(fake, "detach-command.sh start ready-fast"), fake.calls


def running_suite(tier):
    """A detach-command.sh start answer that leaves a pid file naming a live process, as a suite still running would."""
    def start(line, cwd=None, **kwargs):
        with open(os.path.join(cwd, ".tdd", f"ready-{tier}.pid"), "w") as pid_file:
            pid_file.write(f"{os.getpid()}\n{STARTED}\n")
        return 0, "", ""
    return start


def ended_suite(tier):
    """A detach-command.sh start answer whose suite has since ended: its pid file names a pid no process holds."""
    def start(line, cwd=None, **kwargs):
        with open(os.path.join(cwd, ".tdd", f"ready-{tier}.pid"), "w") as pid_file:
            pid_file.write(f"999999\n{STARTED}\n")
        return 0, "", ""
    return start


def test_issue_4088_a_wait_answering_2_while_the_suite_still_runs_leaves_its_worktree_and_record(ready_check, run_cli, fake_processes, tmp_path):
    fake = fake_processes.answers(holding(**TIERS, **{"detach-command.sh start ready-fast": running_suite("fast"),
                                                      "detach-command.sh wait ready-fast": (2, "", ""), LSTART: (0, STARTED + "\n", "")}))
    code, out, _ = run_cli(ready_check, [str(tmp_path)], env={"VERI_BASH_MAJOR": "5"})

    wt = tmp_path / ".tdd" / "ready-fast"
    assert tier_run_line(out.splitlines(), "fast").startswith("fail  fast tier run"), out
    assert not [argv for argv, _ in calls_in(fake, "git worktree remove") if str(wt) in argv], fake.calls
    assert (wt / ".tdd" / "ready-fast.record").exists()


def test_issue_4088_a_started_tier_with_no_pid_file_and_no_exit_may_be_running_so_it_is_kept_and_its_row_fails_naming_it(ready_check, run_cli, fake_processes, tmp_path):
    wt = leave_tier(tmp_path)
    fake = fake_processes.answers(holding(**TIERS, **{"git worktree list": listing(tmp_path, "fast")}))
    code, out, _ = run_cli(ready_check, [str(tmp_path)], env={"VERI_BASH_MAJOR": "5"})

    row = tier_run_line(out.splitlines(), "fast")
    assert row.startswith("fail  fast tier run:") and str(wt) in row, out
    assert not calls_in(fake, "detach-command.sh wait ready-fast"), fake.calls
    assert not [argv for argv, _ in calls_in(fake, "git worktree remove") if str(wt) in argv], fake.calls


def test_issue_4088_a_tier_whose_pid_was_reused_by_another_process_died_without_an_answer_and_its_worktree_is_removed(ready_check, run_cli, fake_processes, tmp_path):
    wt = leave_tier(tmp_path, pid=os.getpid(), started="Sun Nov 15 09:00:00 2026")
    fake = fake_processes.answers(holding(**TIERS, **{"git worktree list": listing(tmp_path, "fast"), LSTART: (0, STARTED + "\n", "")}))
    code, out, _ = run_cli(ready_check, [str(tmp_path)], env={"VERI_BASH_MAJOR": "5"})

    row = tier_run_line(out.splitlines(), "fast")
    assert row.startswith("fail  fast tier run") and "no answer was obtained" in row, out
    assert not calls_in(fake, "detach-command.sh wait ready-fast"), fake.calls
    assert [argv for argv, _ in calls_in(fake, "git worktree remove") if str(wt) in argv], fake.calls


def test_issue_4088_a_deadline_passed_before_the_tiers_starts_none_and_exits_3_naming_the_tiers_not_started(ready_check, run_cli, fake_processes, tmp_path, monkeypatch):
    import types
    import time
    ticks = iter([0.0])
    monkeypatch.setattr(ready_check, "time", types.SimpleNamespace(time=time.time, monotonic=lambda: next(ticks, 600.0)), raising=False)
    fake = fake_processes.answers(holding(**TIERS))
    code, out, _ = run_cli(ready_check, [str(tmp_path)], env={"VERI_BASH_MAJOR": "5"})
    lines = out.splitlines()

    assert code == 3, out
    assert lines[-1].startswith("waiting on ready-fast") and "ready-fast" in lines[-1] and "ready-all" in lines[-1], lines
    assert not calls_in(fake, "detach-command.sh start") and not calls_in(fake, "git worktree add"), fake.calls


PROBE = "claude -p --model haiku --permission-mode bypassPermissions --output-format json"
NO_DENIALS = '{"type": "result", "is_error": false, "permission_denials": []}'


def probe_answer(bash=True, write=True, result=NO_DENIALS, code=0, seen=None):
    """A `claude -p` answer that, as the model would, creates the Bash and the Write nonce file it was asked for in
    its working directory (each only when told to; a string writes that instead of the nonce), then prints <result>."""
    def answer(line, cwd=None, env=None, **kwargs):
        nonce = re.search(r"nonce ([0-9a-f]+)", line).group(1)
        if seen is not None:
            seen.append({"cwd": cwd, "env": env, "nonce": nonce})
        for wanted, path in ((bash, "bash-probe.txt"), (write, "write-probe.txt")):
            if wanted:
                with open(os.path.join(cwd, path), "w") as probe:
                    probe.write(nonce if wanted is True else wanted)
        return code, result, ""
    return answer


def test_issue_4091_the_bypass_permissions_row_is_ok_when_a_haiku_probe_in_a_scratch_directory_under_tdd_leaves_both_nonce_files_and_no_denial(ready_check, fake_processes, tmp_path):
    seen = []
    fake = fake_processes.answers({PROBE: probe_answer(seen=seen)})

    assert ready_check.bypass_permissions_row() == ("bypassPermissions", None)
    assert {argv[0] for argv in fake.argvs} == {"claude"}, fake.calls
    (probe,) = seen
    assert os.path.dirname(os.path.realpath(probe["cwd"])) == os.path.realpath(tmp_path / ".tdd"), probe


@pytest.mark.parametrize("files", [dict(bash=False), dict(write=False), dict(write="something else"), dict(bash=False, write=False)])
def test_issue_4091_an_exit_0_with_is_error_false_but_a_nonce_file_missing_or_wrong_fails_the_bypass_permissions_row(ready_check, fake_processes, files):
    fake_processes.answers({PROBE: probe_answer(**files)})

    name, verdict = ready_check.bypass_permissions_row()

    assert name == "bypassPermissions" and verdict, verdict


def test_issue_4091_a_listed_permission_denial_fails_the_bypass_permissions_row_though_both_nonce_files_hold_the_nonce(ready_check, fake_processes):
    denied = '{"type": "result", "is_error": false, "permission_denials": [{"tool_name": "Bash", "tool_use_id": "t1", "tool_input": {}}]}'
    fake_processes.answers({PROBE: probe_answer(result=denied)})

    name, verdict = ready_check.bypass_permissions_row()

    assert name == "bypassPermissions" and verdict, verdict


PLACES = ("/Library/Application Support/ClaudeCode/managed-settings.json", "/etc/claude-code/managed-settings.json",
          "permissions.deny")


def test_issue_4091_a_failing_bypass_permissions_row_quotes_the_denied_tools_and_names_where_to_look(ready_check, fake_processes):
    denied = ('{"type": "result", "is_error": false, "permission_denials": [{"tool_name": "Bash", "tool_use_id": "t1"}, '
              '{"tool_name": "Write", "tool_use_id": "t2"}]}')
    fake_processes.answers({PROBE: probe_answer(bash=False, write=False, result=denied)})

    _, verdict = ready_check.bypass_permissions_row()

    assert "`Bash`" in verdict and "`Write`" in verdict, verdict
    assert all(place in verdict for place in PLACES) and "user" in verdict and "project" in verdict, verdict


def test_issue_4091_the_probes_claude_starts_without_a_session_variable_strip_session_env_strips(ready_check, fake_processes, monkeypatch):
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "sess-123")
    monkeypatch.setenv("CLAUDECODE", "1")
    monkeypatch.setenv("SOME_HANDLE", "/tmp/sess-123/socket")
    monkeypatch.setenv("KEPT_VARIABLE", "kept")
    seen = []
    fake = fake_processes.answers({PROBE: probe_answer(seen=seen)})

    assert ready_check.bypass_permissions_row() == ("bypassPermissions", None)
    (probe,) = seen
    env = probe["env"]
    assert env is not None and env.get("KEPT_VARIABLE") == "kept", env
    assert not {"CLAUDE_CODE_SESSION_ID", "CLAUDECODE", "SOME_HANDLE"} & set(env), sorted(env)
    assert {argv[0] for argv in fake.argvs} == {"claude"}, fake.calls


def test_issue_4091_a_probe_that_never_answers_fails_the_bypass_permissions_row_saying_no_answer_was_obtained(ready_check, fake_processes, tmp_path):
    from process_fakes import HANGS
    fake_processes.answers({PROBE: HANGS})

    name, verdict = ready_check.bypass_permissions_row()

    assert name == "bypassPermissions" and verdict.startswith("no answer was obtained"), verdict
    assert os.listdir(tmp_path) == [], os.listdir(tmp_path)


@pytest.mark.parametrize("answer, exit_code", [(probe_answer(), 1), (probe_answer(bash=False), 1), (OSError(13, "no claude"), 2)])
def test_issue_4091_the_probes_scratch_directory_is_gone_on_exit_1_or_2_and_nothing_else_is_written(ready_check, run_cli, fake_processes, tmp_path, answer, exit_code):
    repo = tmp_path / "repo"
    (repo / "kept").mkdir(parents=True)
    (repo / "kept" / "file").write_text("as it was\n")
    before = tree_state(tmp_path)
    fake_processes.answers(holding(**{PROBE: answer, "detect-test-command.sh --tier": (3, "", "")}))

    code, _, _ = run_cli(ready_check, [str(repo)], env={"VERI_BASH_MAJOR": "5"})

    assert code == exit_code
    assert sorted(os.listdir(repo)) == ["kept"], os.listdir(repo)
    assert tree_state(tmp_path) == before


PERMISSION_ROWS = ("token scopes", "label priority", "label bug", "actions read", "run-state ignore", "push dry-run",
                   "bypassPermissions")


def test_issue_4093_ready_check_no_permissions_prints_no_permission_row_makes_none_of_their_probes_and_keeps_rd7s_rows(ready_check, run_cli, fake_processes, tmp_path):
    fake = fake_processes.answers(holding())
    home = tmp_path / "scratch-home"
    home.mkdir()
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "settings.json").write_text(json.dumps({"permissions": {"defaultMode": "bypassPermissions"}}))
    code, out, err = run_cli(ready_check, ["--no-suites", "--no-permissions", str(tmp_path)], env={"VERI_BASH_MAJOR": "5", "HOME": str(home)})
    lines = out.splitlines()

    assert (code, lines[-1]) == (0, "ready"), (out, err)
    assert not [line for line in lines if any(line.endswith("  " + row) or ("  " + row + ":") in line for row in PERMISSION_ROWS)], lines
    assert {"ok    gh auth", "ok    push access", "ok    label ready-for-agent"} <= set(lines), lines
    probes = ("gh api -i user", "gh api repos/{owner}/{repo}/labels/", ACTIONS_RUNS, "git rev-parse --git-common-dir",
              "git push", "git remote get-url --push origin", "claude")
    assert not [c for c in fake.calls if c.startswith(probes)], fake.calls
    assert not (tmp_path / ".tdd").exists()


def test_issue_4471_ready_check_with_a_claude_md_ci_on_pr_0_line_and_the_variable_unset_prints_an_ok_pull_request_row_in_a_tree_with_no_pull_request_workflow(ready_check, run_cli, fake_processes, tmp_path):
    (tmp_path / "CLAUDE.md").write_text("# notes\n\nveri: ci on pr: 0\n")
    code, lines = check(ready_check, run_cli, fake_processes, tmp_path, **{"git ls-tree": (0, "", "")})

    assert "ok    pull_request" in lines, lines


def test_issue_4471_ready_check_with_a_claude_md_ci_on_pr_line_that_is_neither_0_nor_1_and_the_variable_unset_exits_2_with_one_stderr_line_naming_the_line(ready_check, run_cli, fake_processes, tmp_path):
    (tmp_path / "CLAUDE.md").write_text("# notes\n\nveri: ci on pr: maybe\n")
    fake_processes.answers(holding())
    code, out, err = run_cli(ready_check, [str(tmp_path)], env={"VERI_BASH_MAJOR": "5"})

    assert (code, "veri: ci on pr:" in err and "maybe" in err, len(err.splitlines())) == (2, True, 1), (out, err)


def test_issue_4471_ready_check_with_no_pull_request_workflow_no_variable_and_no_claude_md_line_fails_the_pull_request_row_naming_the_line(ready_check, run_cli, fake_processes, tmp_path):
    code, lines = check(ready_check, run_cli, fake_processes, tmp_path, **{"git ls-tree": (0, "", "")})

    row = [line for line in lines if line.startswith("fail  pull_request:")]
    assert len(row) == 1 and "VERI_CI_ON_PR" in row[0] and "`veri: ci on pr: 0|1`" in row[0], lines


def test_issue_4529_a_repo_whose_settings_neither_bypass_permissions_nor_allow_git_the_test_command_and_scripts_fails_a_subagent_permissions_row_naming_the_allow_rules(ready_check, run_cli, fake_processes, tmp_path):
    fake_processes.answers(holding(**TIERS))
    home = tmp_path / "scratch-home"
    home.mkdir()
    code, out, _ = run_cli(ready_check, [str(tmp_path)], env={"VERI_BASH_MAJOR": "5", "HOME": str(home)})

    rows = [line for line in out.splitlines() if line.startswith("fail  subagent permissions")]
    assert code == 1, out
    assert len(rows) == 1, out
    assert "Bash(git *)" in rows[0] and "Bash(make test)" in rows[0] and "scripts" in rows[0], rows


def test_issue_4529_allow_rules_spread_over_the_user_and_project_and_local_settings_make_the_subagent_permissions_row_ok_with_no_rule_owed_for_an_unresolved_test_command(ready_check, run_cli, fake_processes, tmp_path):
    fake_processes.answers(holding(**{"detect-test-command.sh --tier all": (3, "", "")}))
    home = tmp_path / "scratch-home"
    (home / ".claude").mkdir(parents=True)
    (tmp_path / ".claude").mkdir()
    scripts = ready_check.paths.resolved_scripts_of(ready_check.__file__)
    (home / ".claude" / "settings.json").write_text(json.dumps({"permissions": {"allow": ["Bash(git *)"]}}))
    (tmp_path / ".claude" / "settings.json").write_text(json.dumps({"permissions": {"allow": ["Bash(ls)"]}}))
    (tmp_path / ".claude" / "settings.local.json").write_text(json.dumps({"permissions": {"allow": [f"Bash({scripts}/*)"]}}))
    _, out, _ = run_cli(ready_check, [str(tmp_path)], env={"VERI_BASH_MAJOR": "5", "HOME": str(home)})

    lines = out.splitlines()
    assert "ok    subagent permissions" in lines, out
    assert not [line for line in lines if line.startswith("fail  subagent permissions")], out


def test_issue_4529_allow_rules_for_git_and_the_all_tests_command_and_scripts_split_over_the_user_and_project_settings_with_no_default_mode_make_the_subagent_permissions_row_ok(ready_check, run_cli, fake_processes, tmp_path):
    fake_processes.answers(holding(**TIERS))
    home = tmp_path / "scratch-home"
    (home / ".claude").mkdir(parents=True)
    (tmp_path / ".claude").mkdir()
    scripts = ready_check.paths.resolved_scripts_of(ready_check.__file__)
    (home / ".claude" / "settings.json").write_text(json.dumps({"permissions": {"allow": ["Bash(git *)", "Bash(make test)"]}}))
    (tmp_path / ".claude" / "settings.json").write_text(json.dumps({"permissions": {"allow": [f"Bash({scripts}/*)"]}}))
    _, out, _ = run_cli(ready_check, [str(tmp_path)], env={"VERI_BASH_MAJOR": "5", "HOME": str(home)})

    lines = out.splitlines()
    assert "ok    subagent permissions" in lines, out
    assert not [line for line in lines if line.startswith("fail  subagent permissions")], out


def test_issue_4529_a_default_mode_of_bypass_permissions_set_only_in_the_local_settings_makes_the_subagent_permissions_row_ok_with_no_allow_rules(ready_check, run_cli, fake_processes, tmp_path):
    fake_processes.answers(holding(**TIERS))
    home = tmp_path / "scratch-home"
    home.mkdir()
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "settings.local.json").write_text(json.dumps({"permissions": {"defaultMode": "bypassPermissions"}}))
    _, out, _ = run_cli(ready_check, [str(tmp_path)], env={"VERI_BASH_MAJOR": "5", "HOME": str(home)})

    lines = out.splitlines()
    assert "ok    subagent permissions" in lines, out
    assert not [line for line in lines if line.startswith("fail  subagent permissions")], out
