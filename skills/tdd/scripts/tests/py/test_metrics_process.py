"""Process-starting cases split from unit/test_metrics.py, which holds the small cases of the same module."""
import importlib
import json

import pytest


@pytest.fixture
def metrics():
    return importlib.import_module("veri.metrics")


def write_log(root, events, raw=""):
    tdd = root / ".tdd"
    tdd.mkdir(exist_ok=True)
    (tdd / "events.jsonl").write_text("".join(json.dumps(event) + "\n" for event in events) + raw)


def render(metrics, capsys, argv=("108",)):
    code = metrics.main(list(argv))
    out, err = capsys.readouterr()
    assert code == 0, err
    return out


def table(out, heading):
    """The rows under <heading>, one dict per row keyed by the header cells."""
    lines = out.split("\n")
    at = lines.index(heading) + 2
    head = [cell.strip() for cell in lines[at].strip("|").split("|")]
    rows = []
    for line in lines[at + 2:]:
        if not line.startswith("|"):
            break
        rows.append(dict(zip(head, (cell.strip() for cell in line[1:-1].split("|")), strict=True)))
    return rows


def leaf(step, ts, actor, phase, attempt, secs, status="0", usage=None, verdict=None, retries=0):
    mark = {"issue": "108", "actor": actor, "phase": phase, "step": step, "attempt": str(attempt)}
    events = [dict(mark, ts=ts, event="launch", name="%s-%s" % (actor, phase))]
    events += [dict(mark, ts=ts + i + 1, event="retry", cause="no heartbeat") for i in range(retries)]
    events.append(dict(mark, ts=ts + secs, event="exit", status=status, secs=str(secs)))
    if usage is not None:
        events.append(dict(mark, ts=ts + secs, event="usage", **usage))
    if verdict is not None:
        events.append(dict(mark, ts=ts + secs, event="verdict", verdict=verdict))
    return events


def conductor(step, ts, event, phase="", **fields):
    return [{"ts": ts, "issue": "108", "actor": "conductor", "phase": phase, "step": step, "event": event,
             "attempt": "", **fields}]


def cells(out, heading, columns):
    rows = table(out, heading)
    key = next(iter(rows[0]))
    return {row[key]: [row[c] for c in columns] for row in rows}


@pytest.mark.process("git push and fetch of refs/veri/runs/<n> through a bare origin")
def test_main_with_no_local_events_for_the_issue_reports_from_the_events_in_origins_refs_veri_runs_n(tmp_path, monkeypatch, capsys, metrics):
    from repo_builder import commit_all, git, new_repo
    run_records = importlib.import_module("veri.run_records")
    origin = tmp_path / "origin.git"
    origin.mkdir()
    git(origin, "init", "-q", "--bare", "-b", "main")
    events = (conductor("s", 30000, "step-start") + leaf("s", 30010, "developer", "green", 1, 90)
              + conductor("s", 30200, "step-done"))
    first, second = tmp_path / "first", tmp_path / "second"
    for machine in (first, second):
        new_repo(machine)
        commit_all(machine, "initial", allow_empty=True)
        git(machine, "remote", "add", "origin", str(origin))
    write_log(first, events)
    run_records.push(str(first), "108")
    monkeypatch.chdir(first)
    local = render(metrics, capsys)
    write_log(second, [{"issue": "999", "event": "start"}])
    monkeypatch.chdir(second)

    assert render(metrics, capsys) == local


def test_main_reports_relaunches_triage_stops_budget_crossings_splits_tier_seconds_and_stop_outcomes(tmp_path, monkeypatch, capsys, metrics):
    def report(name, events):
        root = tmp_path / name
        root.mkdir()
        write_log(root, events)
        monkeypatch.chdir(root)
        return render(metrics, capsys)

    def relaunch(ts):
        return [dict(leaf("s", ts, "verifier", "green", 1, 20)[1], event="relaunch", cause="no-verdict")]

    relaunched = report("relaunched", conductor("s", 30000, "step-start")
                        + leaf("s", 30010, "developer", "green", 1, 90)
                        + leaf("s", 30110, "verifier", "green", 1, 20) + relaunch(30110)
                        + leaf("s", 30140, "verifier", "green", 1, 20) + relaunch(30140)
                        + leaf("s", 30170, "verifier", "green", 1, 20, verdict="REJECT")
                        + conductor("s", 30200, "revise", phase="green", attempt="1", budget="3")
                        + leaf("s", 30210, "developer", "green", 2, 120, retries=1)
                        + leaf("s", 30340, "verifier", "green", 2, 20, verdict="PASS")
                        + conductor("s", 30370, "step-done"))
    assert cells(relaunched, "#### By step", ["attempts", "PASS", "REJECT", "kills", "retries", "no-verdict"]) == {"s": ["6", "1", "1", "0", "1", "2"]}

    def triaged(step, ts, transforms, stopped):
        return (conductor(step, ts, "step-start") + leaf(step, ts + 2, "developer", "refactor", 1, 6)
                + conductor(step, ts + 10, "refactor", phase="refactor", transforms=transforms, budget="5", stopped=stopped)
                + conductor(step, ts + 20, "step-done"))

    triage = report("triage", triaged("tidied", 40000, "1", "nothing-structural")
                    + triaged("owing", 41000, "3", "structural-owed"))
    assert cells(triage, "#### By step", ["stopped"]) == {"tidied": ["nothing-structural"], "owing": ["structural-owed"]}

    def worked(step, ts, *marks):
        return conductor(step, ts, "step-start") + leaf(step, ts + 2, "developer", "green", 1, 6) + list(marks)

    crossing = report("crossing", worked("crossed", 42000, *conductor("crossed", 42010, "step-over-budget",
                                                                      spent="12.40", budget="10.00"))
                      + conductor("crossed", 42020, "step-done")
                      + worked("under", 43000) + conductor("under", 43020, "step-done"))
    assert cells(crossing, "#### By step", ["crossed at"]) == {"crossed": ["12.40"], "under": [""]}

    exhausted = report("exhausted", worked("split", 44000, *conductor("split", 44010, "step-split", at="exhausted")))
    over = report("over", worked("split", 44000, *conductor("split", 44010, "step-split", at="over-budget")))
    assert exhausted != over
    assert cells(exhausted, "#### By step", ["split"]) == {"split": ["exhausted"]}
    assert cells(over, "#### By step", ["split"]) == {"split": ["over-budget"]}

    def ran_tests(step, ts, actor, *runs):
        return [dict(conductor(step, ts + i, "test-run")[0], actor=actor, phase="green", attempt="1",
                     tier=tier, suites="metrics.test.sh", seconds=seconds) for i, (tier, seconds) in enumerate(runs)]

    tiers = report("tiers", conductor("t", 50000, "step-start")
                   + ran_tests("t", 50010, "developer", ("fast", "4"), ("all", "120"))
                   + ran_tests("t", 50050, "verifier", ("fast", "6"), ("all", "100"), ("fast", "5"), ("all", "140"))
                   + conductor("t", 50950, "step-done"))
    assert cells(tiers, "#### Test-command seconds, by tier", ["run 1 s", "run 2 s", "run 3 s"]) == {
        "fast": ["4", "6", "5"], "all": ["120", "100", "140"]}

    stopped = report("stopped", conductor("h", 60000, "step-start") + conductor("h", 60200, "step-done")
                     + conductor("h", 60340, "stop", phase="green", mode="at-ledger", at="green"))
    assert "Outcome: the run was stopped — mode at-ledger, at green." in stopped
    assert "Wall time for the issue: 340 s," in stopped

    resumed = report("resumed", conductor("r", 70000, "step-start")
                     + conductor("r", 70100, "stop", phase="red", mode="at-leaf", at="red")
                     + conductor("r", 70200, "resume") + conductor("r", 70300, "step-start"))
    outcome = [line for line in resumed.split("\n") if line.startswith("Outcome:")]
    assert outcome == ["Outcome: unknown — the log carries no mark ending the run."]


LANDED_EVENTS = [
    {"ts": 13000, "issue": "108", "actor": "conductor", "phase": "", "step": "opener", "event": "step-start", "attempt": "", "skill_commit": "c0ffee1"},
    {"ts": 13100, "issue": "108", "actor": "conductor", "phase": "", "step": "opener", "event": "step-done", "attempt": "", "skill_commit": "c0ffee1"},
    {"ts": 13200, "issue": "108", "actor": "conductor", "phase": "", "step": "closer", "event": "step-start", "attempt": "", "skill_commit": "c0ffee1"},
    {"ts": 13300, "issue": "108", "actor": "conductor", "phase": "", "step": "closer", "event": "step-done", "attempt": "", "skill_commit": "c0ffee1"},
    {"ts": 13400, "issue": "108", "actor": "conductor", "phase": "", "step": "closer", "event": "done", "attempt": "", "skill_commit": "c0ffee1",
     "pr": "https://github.com/ztrange/veri/pull/999"},
]


@pytest.mark.process("metrics.sh's shim run through a symlink to the skill directory from another working directory")
def test_metrics_sh_run_through_a_symlink_to_the_skill_directory_from_another_working_directory_answers_with_the_same_stdout_and_exit_code_as_run_in_place_reading_that_directorys_tdd_and_never_the_skills(tmp_path):
    import pathlib
    import subprocess

    skill = pathlib.Path(__file__).resolve().parents[3]
    work = tmp_path / "work"
    work.mkdir()
    write_log(work, LANDED_EVENTS)
    (work / ".tdd" / "issue-108.md").write_text("- [x] opener\n- [x] closer\n")
    (tmp_path / "link").mkdir()
    (tmp_path / "link" / "skill").symlink_to(skill, target_is_directory=True)

    def answer(script):
        ran = subprocess.run([str(script), "108"], cwd=work, capture_output=True, text=True)
        return ran.returncode, ran.stdout

    in_place = answer(skill / "scripts" / "metrics.sh")
    via_link = answer(tmp_path / "link" / "skill" / "scripts" / "metrics.sh")

    assert via_link == in_place
    assert via_link[0] == 0
    assert "Steps done: 2 of 2 planned." in via_link[1]
