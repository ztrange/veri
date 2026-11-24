"""In-process cases for veri/status.py, the module status.sh is a shim over."""
import ast
import importlib
import json
import pathlib
import time
import pytest
from conftest import live_conductor


@pytest.fixture(autouse=True)
def text_mode(monkeypatch):
    monkeypatch.delenv("STATUS_JSON", raising=False)


@pytest.fixture
def graphql_driver(monkeypatch):
    monkeypatch.setenv("VERI_GH_DRIVER", "graphql")


@pytest.fixture
def status():
    return importlib.import_module("veri.status")


def write_events(path, events):
    path.write_text("".join(json.dumps(event) + "\n" for event in events))


def ledger_run(root, issue, text, number=None):
    """<root>/.tdd/wt/<issue> holding <text> as issue-<number>.md (default: its own)."""
    run = root / ".tdd" / "wt" / issue
    (run / ".tdd").mkdir(parents=True, exist_ok=True)
    (run / ".tdd" / ("issue-%s.md" % (number or issue))).write_text(text)
    return run


def lamp_run(tmp_path, issue, ledgers=None):
    """.tdd/wt/<issue> holding a ledger per number in <ledgers> (default: its own), each '# Plan for #<n> — lamps glow'."""
    for number in ledgers if ledgers is not None else [issue]:
        run = ledger_run(tmp_path, issue, "# Plan for #%s — lamps glow\n\n- [ ] a lamp glows\n" % number, number)
    return run


def lamp_ev(ts, issue, event, **rest):
    line = {"ts": ts, "issue": issue, "actor": "developer", "phase": "red", "step": "a lamp glows",
            "event": event, "attempt": "1", "skill_commit": "abc"}
    line.update(rest)
    return line


def at_ten_thousand(monkeypatch):
    monkeypatch.delenv("VERI_TIMEOUT", raising=False)
    monkeypatch.setattr(time, "time", lambda: 10000)


def git_answering(main_tree, branches=None):
    """A fake_processes answer: `git worktree list` is <main_tree>, `symbolic-ref` is looked up in <branches>."""
    def answer(line, **kwargs):
        if line.startswith("git worktree list"):
            return 0, "worktree %s\nHEAD abc\nbranch refs/heads/main\n\n" % main_tree, ""
        if " symbolic-ref " in line:
            return 0, branches[line.split()[2]] + "\n", ""
        raise AssertionError("unexpected command: %s" % line)
    return answer


def test_status_with_no_run_under_the_main_working_tree_prints_no_runs_and_exits_3(tmp_path, fake_processes, run_cli, status):
    fake_processes(git_answering(tmp_path))

    assert run_cli(status, []) == (3, "no runs\n", "")


@pytest.mark.usefixtures("graphql_driver")
def test_status_lists_a_run_under_tdd_wt_with_its_issue_number_title_branch_and_step_n_of_m(tmp_path, fake_processes, run_cli, status):
    run = ledger_run(tmp_path, "7", "# Plan for #7 \u2014 widgets spin when clicked\n\n- [x] a widget exists\n"
                                    "- [ ] a clicked widget spins\n- [ ] a spinning widget stops\n")
    git = git_answering(tmp_path, {str(run): "tdd/7-widgets-spin"})
    github = json.dumps([{"number": 7, "state": "OPEN"}])
    fake_processes(lambda line, **kwargs: (0, github, "") if line.startswith("gh ") else git(line, **kwargs))

    assert run_cli(status, []) == (0, "#7  widgets spin when clicked  tdd/7-widgets-spin  step 2 of 3\n", "")


@pytest.mark.usefixtures("graphql_driver")
def test_4671_an_open_human_owed_check_before_a_ticked_step_is_not_the_current_step(
        tmp_path, fake_processes, run_cli, status):
    run = ledger_run(tmp_path, "7", "# Plan for #7 — widgets spin when clicked\n\n"
                                    "- [ ] a person spins a widget by hand ⟦human-owed⟧\n"
                                    "- [x] a clicked widget spins\n")
    git = git_answering(tmp_path, {str(run): "tdd/7-widgets-spin"})
    github = json.dumps([{"number": 7, "state": "OPEN"}])
    fake_processes(lambda line, **kwargs: (0, github, "") if line.startswith("gh ") else git(line, **kwargs))

    assert run_cli(status, []) == (0, "#7  widgets spin when clicked  tdd/7-widgets-spin  step 2 of 2\n", "")


@pytest.mark.usefixtures("graphql_driver")
def test_status_shows_a_runs_state_running_done_with_its_pr_url_bailed_with_phase_and_classification_or_stale(
        tmp_path, monkeypatch, fake_processes, run_cli, status):
    runs = {issue: lamp_run(tmp_path, issue) for issue in ("11", "12", "13", "14")}
    launches = {"11": 9990, "12": 9980, "13": 9970, "14": 9000}
    endings = {"12": [lamp_ev(9985, "12", "done", actor="conductor", phase="", step="", attempt="",
                              pr="https://github.com/o/r/pull/12")],
               "13": [lamp_ev(9975, "13", "bail", actor="conductor", phase="green", attempt="", classification="system")]}
    for issue, run in runs.items():
        write_events(run / ".tdd" / "events.jsonl",
                     [lamp_ev(launches[issue], issue, "launch", name="develop-red")] + endings.get(issue, []))
    # #14 names a pid no process can hold (above every pid_max), so os.kill rejects it, not open.
    (runs["14"] / ".tdd" / "conductor.pid").write_text("%d\n" % (2 ** 31 - 1))
    git = git_answering(tmp_path, {str(run): "tdd/%s-lamps" % issue for issue, run in runs.items()})
    github = json.dumps([{"number": int(issue), "state": "CLOSED" if issue == "14" else "OPEN"} for issue in runs])
    fake_processes(lambda line, **kwargs: (0, github, "") if line.startswith("gh ") else git(line, **kwargs))
    live_conductor(monkeypatch, runs["11"] / ".tdd", "11")
    at_ten_thousand(monkeypatch)

    code, out, err = run_cli(status, [], env={"VERI_TIMEOUT": "600"})

    head = "  step 1 of 1  red  developer  develop-red "
    assert (code, err, out) == (0, "",
        "#11  lamps glow  tdd/11-lamps" + head + "10s  attempt 1  $0.00  0 tokens  running\n"
        "#12  lamps glow  tdd/12-lamps" + head + "20s  attempt 1  $0.00  0 tokens  done https://github.com/o/r/pull/12\n"
        "#13  lamps glow  tdd/13-lamps" + head + "30s  attempt 1  $0.00  0 tokens  bailed green system\n"
        "#14  lamps glow  tdd/14-lamps" + head + "1000s  attempt 1  $0.00  0 tokens  closed\n")


@pytest.mark.usefixtures("graphql_driver")
def test_status_watch_redraws_in_place_recomputing_every_run_from_disk_on_each_render(
        tmp_path, monkeypatch, fake_processes, run_cli, status):
    run = lamp_run(tmp_path, "41")
    events = run / ".tdd" / "events.jsonl"
    write_events(events, [lamp_ev(9990, "41", "launch", name="develop-red")])
    git = git_answering(tmp_path, {str(run): "tdd/41-lamps"})
    github = json.dumps([{"number": 41, "state": "OPEN"}])
    fake_processes(lambda line, **kwargs: (0, github, "") if line.startswith("gh ") else git(line, **kwargs))
    live_conductor(monkeypatch, run / ".tdd", "41")
    at_ten_thousand(monkeypatch)
    sleeps = []

    def sleep(seconds):
        sleeps.append(seconds)
        if len(sleeps) == 1:
            write_events(events, [lamp_ev(9990, "41", "launch", name="develop-red"),
                                  lamp_ev(9995, "41", "done", actor="conductor", phase="", step="", attempt="",
                                          pr="https://github.com/o/r/pull/41")])
        else:
            raise SystemExit(0)

    monkeypatch.setattr(time, "sleep", sleep)

    code, out, err = run_cli(status, ["--watch", "0"])

    line = "#41  lamps glow  tdd/41-lamps  step 1 of 1  red  developer  develop-red 10s  attempt 1  $0.00  0 tokens  "
    assert (code, err, sleeps, out) == (0, "", [0, 0], "\033[H\033[2J" + line + "running\n"
                                                        "\033[H\033[2J" + line + "done https://github.com/o/r/pull/41\n")


@pytest.mark.usefixtures("graphql_driver")
def test_status_exits_2_naming_the_failure_when_a_ledger_cannot_be_read_as_text(tmp_path, fake_processes, run_cli, status):
    run = ledger_run(tmp_path, "9", "")
    (run / ".tdd" / "issue-9.md").write_bytes(b"# Plan for #9 \xe2\x80\x94 locked\n\n- [ ] a \xff lock\n")
    git = git_answering(tmp_path, {str(run): "tdd/9-locked"})
    github = json.dumps([{"number": 9, "state": "OPEN"}])
    fake_processes(lambda line, **kwargs: (0, github, "") if line.startswith("gh ") else git(line, **kwargs))

    code, out, err = run_cli(status, [])

    assert (code, out, err.startswith("status.sh: UnicodeDecodeError: ")) == (2, "", True)


def test_status_given_a_bad_argument_names_it_on_stderr_and_exits_2(tmp_path, fake_processes, run_cli, status):
    fake_processes(git_answering(tmp_path))

    code, out, err = run_cli(status, ["--bogus"])

    assert (code, out, err.splitlines()[0], "--report" in err.splitlines()[1]) == (
        2, "", "status.sh: unknown option '--bogus'", True)


def test_no_case_in_this_suite_calls_a_function_of_veri_status_other_than_main():
    tree = ast.parse(pathlib.Path(__file__).read_text())

    calls = sorted({node.func.attr for node in ast.walk(tree)
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name) and node.func.value.id == "status"
                    and node.func.attr != "main"})

    assert calls == []


def report_tree(tmp_path, monkeypatch, status, journals):
    """A main tree at <tmp_path> for --report, its runs' journals {issue: [event, ...]}, each opened by a
    conductor-start."""
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    monkeypatch.setenv("VERI_HOME", str(tmp_path / "home"))
    runs = tmp_path / "home" / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    (tmp_path / ".tdd").mkdir()
    for issue, events in journals.items():
        start = {"ts": 1793600000, "awake": 0, "event": "conductor-start", "pid": 2 ** 22 + 7, "started": "x"}
        write_events(runs / ("%s.jsonl" % issue), [start] + events)


def logs_answer(logs):
    """A fake_processes answer: `git ... log <ref> ...` reads logs[<ref>] ("" for a ref it does not name); any other
    command reads nothing."""
    def answer(line, **_):
        words = line.split()
        if line.startswith("git ") and "log" in words:
            return 0, next((text for ref, text in logs.items() if ref in words), ""), ""
        return 0, "", ""
    return answer


def section(out, name):
    """The lines of the --report section headed <name>, up to the blank line that ends it."""
    lines = out.splitlines()
    start = lines.index(name) + 1
    return lines[start:lines.index("", start)] if "" in lines[start:] else lines[start:]


def test_report_lists_no_run_as_ready_to_merge_whose_done_pr_subject_is_on_the_stack_branch_only_issue_4320(
        tmp_path, monkeypatch, fake_processes, run_cli, status):
    report_tree(tmp_path, monkeypatch, status, {"2750": [{"ts": 1793600050, "awake": 50, "event": "done", "pr": 99}]})
    stack_reads(monkeypatch, status, span=("stacky", "main", []))
    fake_processes.answers({"": logs_answer({"main": "fix: elsewhere (#1)\n",
                                             "origin/stacky": "feat: joined (#2750)\nfix: elsewhere (#1)\n"})})

    code, out, err = run_cli(status, ["--report"])

    assert (code, [line for line in section(out, "Waiting") if line.startswith("#")]) == (0, []), err


@pytest.mark.parametrize("failure", ["span", "log"])
def test_report_lists_a_done_run_as_merge_state_unknown_when_the_stack_subjects_cannot_be_read_issue_4320(
        tmp_path, monkeypatch, fake_processes, run_cli, status, failure):
    report_tree(tmp_path, monkeypatch, status, {"2750": [{"ts": 1793600050, "awake": 50, "event": "done", "pr": 99}]})

    stack_reads(monkeypatch, status, span=status.stack_branch.Refused("git fetch origin got no answer (exit 128)")
                if failure == "span" else ("stacky", "main", []))
    log = logs_answer({"main": "fix: elsewhere (#1)\n"})
    fake_processes.answers({"": lambda line, **kw: (128, "", "fatal: bad object\n") if "origin/stacky" in line.split()
                            else log(line, **kw)})

    code, out, err = run_cli(status, ["--report"])

    waiting = [line for line in section(out, "Waiting") if line.startswith("#")]
    assert (code, [line.split(":")[0] for line in waiting]) == (0, ["#2750 PR 99 merge state unknown"]), (out, err)


def test_report_lists_a_done_run_as_ready_to_merge_when_the_named_stack_is_not_yet_on_origin_issue_4320(
        tmp_path, monkeypatch, fake_processes, run_cli, status):
    report_tree(tmp_path, monkeypatch, status, {"2750": [{"ts": 1793600050, "awake": 50, "event": "done", "pr": 99}]})
    stack_reads(monkeypatch, status, span=("stacky", "main", []))
    log = logs_answer({"main": "fix: elsewhere (#1)\n"})

    def answer(line, **kw):
        if "origin/stacky" in line.split():
            return 128, "", "fatal: ambiguous argument 'origin/stacky': unknown revision\n"
        if "rev-parse" in line.split():
            return 1, "", ""
        return log(line, **kw)
    fake_processes.answers({"": answer})

    code, out, err = run_cli(status, ["--report"])

    assert (code, [line for line in section(out, "Waiting") if line.startswith("#")]) == (
        0, ["#2750 PR 99 ready to merge"]), err


STACK = [("a1" * 20, "feat: one (#11)"), ("a2" * 20, "test: one more (#11)"), ("b1" * 20, "feat: two (#12)"),
         ("c1" * 20, "feat: three (#13)")]


def stack_reads(monkeypatch, status, span=("stacky", "main", STACK), scripts=None, tracking=None, landed=("7", "8")):
    """Injects the stack's three reads: git (stack_span answers <span>), the scripts (stack_script answers
    scripts[<name>], by default stack-green.sh at the third commit and stack-red.sh exit 3) and GitHub (tracking_pull
    answers <tracking>, landed_slices <landed>); a value that is an exception is raised instead."""
    scripts = {"stack-green.sh": (0, STACK[2][0] + "\n"), "stack-red.sh": (3, ""), **(scripts or {})}

    def answering(value):
        def read(*args):
            if isinstance(value, Exception):
                raise value
            return value
        return read
    monkeypatch.setattr(status, "stack_span", answering(span), raising=False)
    monkeypatch.setattr(status, "stack_script", lambda root, name: answering(scripts[name])(), raising=False)
    monkeypatch.setattr(status, "tracking_pull", answering(tracking), raising=False)
    monkeypatch.setattr(status, "landed_slices", answering(set(landed) if isinstance(landed, tuple) else landed),
                        raising=False)


def test_report_prints_a_stack_section_between_landed_and_running_with_its_joined_tested_and_landed_counts_issue_4320(
        tmp_path, monkeypatch, fake_processes, run_cli, status):
    report_tree(tmp_path, monkeypatch, status, {})
    stack_reads(monkeypatch, status)
    fake_processes.answers({"": logs_answer({})})

    code, out, err = run_cli(status, ["--report"])

    heads = [line for line in out.splitlines() if line in ("Landed", "Stack", "Running")]
    assert (code, heads, section(out, "Stack")) == (
        0, ["Landed", "Stack", "Running"], ["stacky: joined 3, tested 2, landed 2 in 24h"]), (out, err)


def test_report_stack_section_names_the_open_tracking_pull_request_and_a_freeze_issue_4320(
        tmp_path, monkeypatch, fake_processes, run_cli, status):
    report_tree(tmp_path, monkeypatch, status, {})
    red = "d4" * 20
    stack_reads(monkeypatch, status, tracking="https://github.com/acme/widgets/pull/500",
                scripts={"stack-red.sh": (0, "%s https://github.com/acme/widgets/actions/runs/9 failure\n" % red)})
    fake_processes.answers({"": logs_answer({})})

    code, out, err = run_cli(status, ["--report"])

    assert (code, section(out, "Stack")) == (0, [
        "stacky: joined 3, tested 2, landed 2 in 24h", "tracking: https://github.com/acme/widgets/pull/500",
        "frozen: %s https://github.com/acme/widgets/actions/runs/9" % red]), (out, err)


def test_report_has_no_stack_section_and_reads_no_stack_where_no_stack_branch_is_named_issue_4320(
        tmp_path, monkeypatch, fake_processes, run_cli, status):
    report_tree(tmp_path, monkeypatch, status, {})
    unasked = AssertionError("a stack read with no stack named")
    stack_reads(monkeypatch, status, span=None, scripts={"stack-green.sh": unasked, "stack-red.sh": unasked},
                tracking=unasked, landed=unasked)
    fake_processes.answers({"": logs_answer({})})

    code, out, err = run_cli(status, ["--report"])

    assert (code, [line for line in out.splitlines() if line in ("Landed", "Stack", "Running")]) == (
        0, ["Landed", "Running"]), (out, err)


@pytest.mark.parametrize("unread", ["figures", "stack"])
def test_report_stack_section_prints_a_figure_it_could_not_read_as_a_question_mark_and_keeps_its_exit_code_issue_4320(
        tmp_path, monkeypatch, fake_processes, run_cli, status, unread):
    report_tree(tmp_path, monkeypatch, status, {})
    lost = status.github.NoAnswer("", "HTTP 502")
    stack_reads(monkeypatch, status, scripts={"stack-green.sh": (2, ""), "stack-red.sh": (2, "")}, tracking=lost,
                landed=lost, **({"span": status.stack_branch.Refused("git fetch origin got no answer")}
                                if unread == "stack" else {}))
    fake_processes.answers({"": logs_answer({})})

    code, out, err = run_cli(status, ["--report"])

    assert (code, section(out, "Stack")) == (0, [
        ("stacky: joined 3" if unread == "figures" else "?: joined ?") + ", tested ?, landed ? in 24h",
        "tracking: ?", "frozen: ?"]), (out, err)


@pytest.mark.parametrize("stack", ["named", "unread", "none"])
def test_status_json_carries_the_stack_figures_null_for_an_unread_one_and_no_key_where_no_stack_is_named_issue_4320(
        tmp_path, monkeypatch, fake_processes, run_cli, status, stack):
    report_tree(tmp_path, monkeypatch, status, {})
    red, run = "d4" * 20, "https://github.com/acme/widgets/actions/runs/9"
    span = {"named": ("stacky", "main", STACK), "unread": status.stack_branch.Refused("git fetch origin got no answer"),
            "none": None}[stack]
    stack_reads(monkeypatch, status, span=span, tracking="https://github.com/acme/widgets/pull/500",
                scripts={"stack-red.sh": (0, "%s %s failure\n" % (red, run))})
    fake_processes.answers({"": logs_answer({})})

    code, out, err = run_cli(status, ["--json"])

    expected = {"named": {"branch": "stacky", "joined": 3, "tested": 2, "landed": 2,
                          "tracking_pr": "https://github.com/acme/widgets/pull/500", "frozen": {"sha": red, "run_url": run}},
                "unread": dict.fromkeys(["branch", "joined", "tested", "landed", "tracking_pr", "frozen"])}
    document = json.loads(out)
    assert (code, document.get("stack", "absent")) == (3, expected.get(stack, "absent")), (out, err)


def pull_record(number, head, merged, updated, base="main", fork=False):
    """A closed pull request as GitHub's REST list gives it, `Closes #<number>` its body."""
    return {"number": number, "body": "Closes #%d\n" % number, "merged_at": merged, "updated_at": updated,
            "head": {"ref": head, "repo": {"full_name": "%s/widgets" % ("stranger" if fork else "acme")}},
            "base": {"ref": base, "repo": {"full_name": "acme/widgets"}}}


def test_report_landed_count_names_only_this_repositorys_slices_merged_into_the_default_branch_in_24_hours_issue_4320(
        tmp_path, monkeypatch, fake_processes, run_cli, status):
    report_tree(tmp_path, monkeypatch, status, {})
    read = status.landed_slices
    stack_reads(monkeypatch, status)
    monkeypatch.setattr(status, "landed_slices", read)
    monkeypatch.setattr(status.time, "time", lambda: 1793600000)
    inside, before = "2026-11-02T09:00:00Z", "2026-10-31T09:00:00Z"
    first = ([pull_record(21, "stacky-slice-a1a1a1a1a1", inside, inside),
              pull_record(22, "stacky-slice-b1b1b1b1b1", before, inside),
              pull_record(23, "tdd/23-other", inside, inside),
              pull_record(24, "stacky-slice-c1c1c1c1c1", inside, inside, fork=True),
              pull_record(25, "stacky-slice-d1d1d1d1d1", inside, inside, base="dev")]
             + [pull_record(100 + n, "tdd/%d-filler" % n, inside, inside) for n in range(95)])
    second = [pull_record(26, "stacky-slice-e1e1e1e1e1", inside, inside), pull_record(27, "stacky-slice-f1", None, before)]
    pages = {"page=1": first, "page=2": second}
    log = logs_answer({})

    def answer(line, **kw):
        if line.startswith("gh api"):
            return 0, json.dumps(next(page for key, page in pages.items() if line.split()[2].endswith(key))), ""
        return log(line, **kw)
    fake_processes.answers({"": answer})

    code, out, err = run_cli(status, ["--report"])

    assert (code, section(out, "Stack")[0]) == (0, "stacky: joined 3, tested 2, landed 2 in 24h"), (out, err)


def test_report_counts_tested_as_0_when_stack_green_finds_no_tested_issue_end_issue_4320(
        tmp_path, monkeypatch, fake_processes, run_cli, status):
    report_tree(tmp_path, monkeypatch, status, {})
    stack_reads(monkeypatch, status, scripts={"stack-green.sh": (3, "")})
    fake_processes.answers({"": logs_answer({})})

    code, out, err = run_cli(status, ["--report"])

    assert (code, section(out, "Stack")[0]) == (0, "stacky: joined 3, tested 0, landed 2 in 24h"), (out, err)


@pytest.mark.parametrize("mode", ["--report", "--json"])
def test_stack_figures_read_unknown_not_zero_or_unfrozen_when_a_stack_script_is_killed_at_its_bound_issue_4320(
        tmp_path, monkeypatch, fake_processes, run_cli, status, mode):
    report_tree(tmp_path, monkeypatch, status, {})
    script = status.stack_script
    stack_reads(monkeypatch, status)
    monkeypatch.setattr(status, "stack_script", script)
    monkeypatch.setattr(status.github, "bounded_group", lambda argv, **kw: status.github.TimedOut(argv, 124, "", "said"))
    fake_processes.answers({"": logs_answer({})})

    code, out, err = run_cli(status, [mode])

    if mode == "--report":
        assert (code, section(out, "Stack")[0], section(out, "Stack")[-1]) == (
            0, "stacky: joined 3, tested ?, landed 2 in 24h", "frozen: ?"), (out, err)
    else:
        stack = json.loads(out)["stack"]
        assert (stack["tested"], stack["frozen"]) == (None, None), (out, err)


@pytest.mark.parametrize("mode", ["--report", "--json"])
def test_no_stack_section_nor_key_where_the_cwd_is_no_main_tree_though_its_claude_md_names_a_stack_issue_4320(
        tmp_path, monkeypatch, fake_processes, run_cli, status, mode):
    report_tree(tmp_path, monkeypatch, status, {})
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: "")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (elsewhere / "CLAUDE.md").write_text("%s`stacky`\n" % status.stack_branch.MARKER)
    monkeypatch.chdir(elsewhere)
    fake_processes.answers({"": logs_answer({})})

    code, out, err = run_cli(status, [mode])

    assert "Stack" not in out.splitlines() and '"stack"' not in out, (code, out, err)


def test_report_prints_the_tracking_pull_request_as_unknown_when_two_are_open_issue_4320(
        tmp_path, monkeypatch, fake_processes, run_cli, status):
    report_tree(tmp_path, monkeypatch, status, {})
    read = status.tracking_pull
    stack_reads(monkeypatch, status)
    monkeypatch.setattr(status, "tracking_pull", read)
    pulls = [status.github._pull({"html_url": "https://github.com/acme/widgets/pull/%d" % n}) for n in (500, 501)]
    monkeypatch.setattr(status.github, "stack_pulls", lambda stack, default: pulls)
    fake_processes.answers({"": logs_answer({})})

    code, out, err = run_cli(status, ["--report"])

    assert (code, section(out, "Stack")[1], "2 open pull requests track stacky" in err) == (0, "tracking: ?", True), (
        out, err)


def test_report_lists_a_done_run_as_merge_state_unknown_when_rev_parse_cannot_tell_the_stack_branch_absent_issue_4320(
        tmp_path, monkeypatch, fake_processes, run_cli, status):
    report_tree(tmp_path, monkeypatch, status, {"2750": [{"ts": 1793600050, "awake": 50, "event": "done", "pr": 99}]})
    stack_reads(monkeypatch, status, span=("stacky", "main", []))
    log = logs_answer({"main": "fix: elsewhere (#1)\n"})

    def answer(line, **kw):
        if "origin/stacky" in line.split():
            return 128, "", "fatal: bad object\n"
        if "rev-parse" in line.split():
            return 128, "", "fatal: not a git repository\n"
        return log(line, **kw)
    fake_processes.answers({"": answer})

    code, out, err = run_cli(status, ["--report"])

    assert (code, [line.split(":")[0] for line in section(out, "Waiting") if line.startswith("#")]) == (
        0, ["#2750 PR 99 merge state unknown"]), err


def test_report_names_on_stderr_why_the_stack_could_not_be_read_issue_4320(
        tmp_path, monkeypatch, fake_processes, run_cli, status):
    report_tree(tmp_path, monkeypatch, status, {})
    stack_reads(monkeypatch, status, span=status.stack_branch.Refused("git fetch origin got no answer (exit 128)"))
    fake_processes.answers({"": logs_answer({})})

    code, out, err = run_cli(status, ["--report"])

    assert (code, "the stack could not be read: git fetch origin got no answer (exit 128)" in err) == (0, True), err


def test_report_prints_landed_as_unknown_when_the_slices_run_past_the_pages_it_reads_issue_4320(
        tmp_path, monkeypatch, fake_processes, run_cli, status):
    report_tree(tmp_path, monkeypatch, status, {})
    read = status.landed_slices
    stack_reads(monkeypatch, status)
    monkeypatch.setattr(status, "landed_slices", read)
    monkeypatch.setattr(status.github, "PULL_PAGES", 1)
    monkeypatch.setattr(status.time, "time", lambda: 1793600000)
    page = [pull_record(n, "stacky-slice-%d" % n, "2026-11-02T09:00:00Z", "2026-11-02T09:00:00Z") for n in range(100)]
    log = logs_answer({})
    fake_processes.answers({"": lambda line, **kw: (0, json.dumps(page), "") if line.startswith("gh api")
                            else log(line, **kw)})

    code, out, err = run_cli(status, ["--report"])

    assert (code, section(out, "Stack")[0]) == (0, "stacky: joined 3, tested 2, landed ? in 24h"), (out, err)


def test_status_json_under_watch_reads_no_stack_issue_4320(tmp_path, monkeypatch, fake_processes, run_cli, status):
    report_tree(tmp_path, monkeypatch, status, {})
    unasked = AssertionError("a stack read under --watch")
    stack_reads(monkeypatch, status, span=unasked, scripts={"stack-green.sh": unasked, "stack-red.sh": unasked},
                tracking=unasked, landed=unasked)
    fake_processes.answers({"": logs_answer({})})

    def sleep(seconds):
        raise SystemExit(0)
    monkeypatch.setattr(time, "sleep", sleep)

    code, out, err = run_cli(status, ["--watch", "0", "--json"])

    assert (code, json.loads(out.replace("\033[H\033[2J", ""))) == (0, {"runs": [], "scope": None}), err


def test_report_passes_on_a_stack_scripts_reason_when_it_gives_no_answer_issue_4320(
        tmp_path, monkeypatch, fake_processes, run_cli, status):
    report_tree(tmp_path, monkeypatch, status, {})
    read = status.stack_script
    stack_reads(monkeypatch, status)
    monkeypatch.setattr(status, "stack_script", read)
    log = logs_answer({})

    def answer(line, **kw):
        name = line.split()[0].rsplit("/", 1)[-1]
        if name == "stack-green.sh":
            return 2, "", "stack-green: the check runs of a1: HTTP 502\n"
        if name == "stack-red.sh":
            return 3, "", "stack-red: not red\n"
        return log(line, **kw)
    fake_processes.answers({"": answer})

    code, out, err = run_cli(status, ["--report"])

    assert (code, section(out, "Stack")[0], "HTTP 502" in err, "not red" in err) == (
        0, "stacky: joined 3, tested ?, landed 2 in 24h", True, False), (out, err)


@pytest.mark.parametrize("driver", [None, "rest", "auto"])
def test_4663_status_json_reads_every_issue_state_lower_cased_through_the_rest_listing(tmp_path, monkeypatch, fake_processes, run_cli, status, driver):
    if driver is None:
        monkeypatch.delenv("VERI_GH_DRIVER", raising=False)
    else:
        monkeypatch.setenv("VERI_GH_DRIVER", driver)
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    runs = {issue: ledger_run(tmp_path, issue, "# Plan for #%s \u2014 widgets spin\n\n- [ ] a widget exists\n" % issue)
            for issue in ("4", "5")}
    git = git_answering(tmp_path, {str(run): "tdd/%s-widgets" % issue for issue, run in runs.items()})
    path = "gh api repos/{owner}/{repo}/issues?state=all&per_page=100&page="
    pages = {path + "1": '[{"number":4,"state":"open"},{"number":5,"state":"closed"}]', path + "2": "[]"}
    fake_processes(lambda line, **kwargs: ((0, pages[line], "") if line in pages else (1, "", "refused: " + line))
                   if line.startswith("gh ") else git(line, **kwargs))

    code, out, err = run_cli(status, ["--json"])

    assert code == 0
    assert {r["issue"]: r["issue_state"] for r in json.loads(out)["runs"]} == {"4": "open", "5": "closed"}
