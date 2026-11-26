"""In-process cases for veri/stack_recover.py, the module stack-recover.sh is a shim over (PRD 033.3): git (git.out,
git.network), GitHub (github.gh_api), the stack branch stack-branch.sh names (stack_branch.named) and the sibling scripts
it runs (stack_fix.script) are injected in-process, so no case starts a process."""
import importlib
import json
import os
import re
import subprocess

import pytest

BASE = "1" * 40  # origin/<stack> as fetched
TIP = "9" * 40  # the local <stack>'s tip
URL = "https://github.com/owner/repo/pull/50"  # the stack's tracking pull request


@pytest.fixture
def stack_recover():
    return importlib.import_module("veri.stack_recover")


class World:
    """A repository at <tmp_path> (a main working tree, so no outage file but the one a case writes) whose stack
    branch is <named> (stack_branch.named; an exception is raised). Its refs are <refs> (a ref name to a sha), by default
    the local stack at TIP and origin's at BASE, plus origin's run branches <branches> (a name to a sha). A sha is an
    ancestor of another when the pair is in <ancestors> (by default BASE of TIP), or the two are equal. `git log` of a
    range answers <commits>, newest first as git does, oldest first with --reverse, and fails when <log_fails>; `git show` of a commit's Veri-Joined trailer answers <trailers>' entry, else
    nothing. origin (git.network) fetches with <fetch>, an (exit code, stderr) pair, and answers every push with
    <pushes>' entry for the ref it writes (`refs/heads/<name>`, or the name a delete names), else (0, ""). GitHub reads
    each pull request of <pulls> (its number to its record, or to a list of raw answers given in turn), every other one
    as merged. The sibling scripts answer
    <answers>' entry, (exit code, stdout): merge-lock.sh (0, ""), stack-pr.sh (0, URL), any other (0, ""). Every git,
    script and GitHub call is kept, in order, in <log>: ("git", *args), (script, *args) and ("gh", path); the pushes,
    deletes among them, in <pushed>, and the scripts in <scripts>."""

    def __init__(self, monkeypatch, tmp_path, named="stack", refs=None, branches=None, ancestors=((BASE, TIP),),
                 commits=(), trailers=None, fetch=(0, ""), pushes=None, pulls=None, answers=None, log_fails=False):
        (tmp_path / ".git").mkdir(exist_ok=True)
        monkeypatch.chdir(tmp_path)
        self.log, self.pushed, self.scripts = [], [], []
        refs = dict({"refs/heads/stack": TIP, "refs/remotes/origin/stack": BASE} if refs is None else refs)
        refs.update({"refs/remotes/origin/" + name: sha for name, sha in (branches or {}).items()})
        trailers, pushes, pulls = trailers or {}, pushes or {}, pulls or {}
        answers = dict({"stack-pr.sh": (0, URL + "\n")}, **(answers or {}))
        git, github = importlib.import_module("veri.git"), importlib.import_module("veri.github")

        def out(*args, cwd=None):
            self.log.append(("git",) + args)
            if args[:1] == ("rev-parse",):
                if args[-1] in refs:
                    return refs[args[-1]]
                raise git.GitFailed(args, 1, "")
            if args[:2] == ("merge-base", "--is-ancestor"):
                if args[2] == args[3] or (args[2], args[3]) in ancestors:
                    return ""
                raise git.GitFailed(args, 1, "")
            if args[:1] == ("log",):
                if log_fails:
                    raise git.GitFailed(args, 128, "fatal: bad revision")
                return "\n".join(commits if "--reverse" in args else reversed(commits))
            if args[:1] == ("show",):
                return trailers.get(args[-1], "")
            raise git.GitFailed(args, 128, "not faked")

        def network(*args, cwd=None):
            self.log.append(("git",) + args)
            if args[:1] == ("fetch",):
                return subprocess.CompletedProcess(["git", *args], fetch[0], "", fetch[1])
            self.pushed.append(args)
            if "--delete" in args:
                written = args[args.index("--delete") + 1]
            else:
                written = args[-1].split(":", 1)[1]
            code, said = pushes.get(written, (0, ""))
            return subprocess.CompletedProcess(["git", *args], code, "", said)

        def gh_api(path, stderr=None):
            self.log.append(("gh", path))
            number = re.fullmatch(r"repos/[^/]+/[^/]+/pulls/(\d+)", path)
            said = pulls.get(int(number[1]), {"state": "closed", "merged": True}) if number else {}
            raw = said.pop(0) if isinstance(said, list) else json.dumps(said)
            return subprocess.CompletedProcess(["gh", "api", path], 0, raw, "")

        def answer(root):
            if isinstance(named, BaseException):
                raise named
            return named

        def script(name, *args, limit=None):
            self.log.append((name,) + args)
            self.scripts.append((name,) + args)
            return answers.get(name, (0, ""))

        monkeypatch.setattr(git, "out", out)
        monkeypatch.setattr(git, "network", network)
        monkeypatch.setattr(github, "gh_api", gh_api)
        monkeypatch.setattr(importlib.import_module("veri.stack_branch"), "named", answer)
        monkeypatch.setattr(importlib.import_module("veri.stack_fix"), "script", script)


def test_an_argument_exits_2_with_the_usage_line_and_the_shim_execs_the_module(monkeypatch, tmp_path, run_cli,
                                                                               stack_recover):
    world = World(monkeypatch, tmp_path)
    shim = os.path.join(os.path.dirname(os.path.dirname(stack_recover.__file__)), "stack-recover.sh")

    code, out, err = run_cli(stack_recover, ["--now"])

    with open(shim, encoding="utf-8") as f:
        text = f.read()
    assert (code, out, err, world.log) == (2, "", "usage: stack-recover.sh\n", []), err
    assert text.split("\n", 1)[0] == "#!" + "/bin/sh" and '"$(dirname "$0")/veri/stack_recover.py"' in text, text


def test_while_the_outage_file_exists_it_exits_2_in_one_stderr_line_before_any_read_or_lock(
        monkeypatch, tmp_path, run_cli, stack_recover):
    world = World(monkeypatch, tmp_path, named=AssertionError("stack-branch.sh was read"))
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "github-outage").write_text("")

    code, out, err = run_cli(stack_recover, [])

    assert (code, out, err.count("\n"), world.log) == (2, "", 1, []), err
    assert "outage" in err and err.startswith("stack-recover: "), err


LINE = "CLAUDE.md: the line 'veri: stack branch:' names no branch"


@pytest.mark.parametrize("refused, code, said", [
    (False, 3, "stack-branch.sh exits 3"),
    (True, 2, "stack-branch.sh exits 2: " + LINE),
])
def test_stack_branch_sh_exiting_3_exits_3_and_exiting_2_exits_2_naming_it_locking_nothing(
        monkeypatch, tmp_path, run_cli, stack_recover, refused, code, said):
    named = importlib.import_module("veri.stack_branch").Refused(LINE) if refused else None
    world = World(monkeypatch, tmp_path, named=named)

    got, out, err = run_cli(stack_recover, [])

    assert (got, out, err.count("\n"), said in err, world.log) == (code, "", 1, True, []), err


@pytest.mark.parametrize("failing", ["take", "fetch"])
def test_takes_the_merge_lock_then_fetches_and_a_failed_take_or_fetch_exits_2_naming_it_the_lock_freed(
        monkeypatch, tmp_path, run_cli, stack_recover, failing):
    pid = str(os.getpid())
    world = World(monkeypatch, tmp_path, answers={"merge-lock.sh": (2, "")} if failing == "take" else None,
                  fetch=(128, "fatal: unable to access origin") if failing == "fetch" else (0, ""))

    code, out, err = run_cli(stack_recover, [])

    take, fetch, release = ("merge-lock.sh", "take", "--pid", pid), ("git", "fetch", "--prune", "origin"), (
        "merge-lock.sh", "release", "--pid", pid)
    assert (code, out, err.count("\n"), world.log) == (
        2, "", 1, [take] if failing == "take" else [take, fetch, release]), err
    assert ("merge-lock.sh take" if failing == "take" else "unable to access origin") in err, err


@pytest.mark.parametrize("refs", [
    {"refs/remotes/origin/stack": BASE},
    {"refs/heads/stack": BASE, "refs/remotes/origin/stack": BASE},
    {"refs/heads/stack": BASE, "refs/remotes/origin/stack": TIP},
], ids=["absent", "at-origin", "behind-origin"])
def test_a_local_stack_absent_at_origin_or_behind_it_exits_3_in_one_line_nothing_pushed_the_lock_freed(
        monkeypatch, tmp_path, run_cli, stack_recover, refs):
    world = World(monkeypatch, tmp_path, refs=refs)

    code, out, err = run_cli(stack_recover, [])

    assert (code, out, err.count("\n"), "nothing to push" in err, world.pushed, world.scripts[-1][:2]) == (
        3, "", 1, True, [], ("merge-lock.sh", "release")), err


@pytest.mark.parametrize("moved", ["diverged", "deleted"])
def test_origin_stack_not_an_ancestor_of_the_local_stack_or_gone_exits_1_naming_it_nothing_pushed_the_lock_freed(
        monkeypatch, tmp_path, run_cli, stack_recover, moved):
    if moved == "diverged":
        world = World(monkeypatch, tmp_path, ancestors=())
    else:
        world = World(monkeypatch, tmp_path, refs={"refs/heads/stack": TIP})

    code, out, err = run_cli(stack_recover, [])

    named = [TIP in err, BASE in err] if moved == "diverged" else [TIP in err, "origin/stack" in err]
    assert (code, out, err.count("\n"), named, world.pushed, world.scripts[-1][:2]) == (
        1, "", 1, [True, True], [], ("merge-lock.sh", "release")), err


A, B, C = "a" * 40, "b" * 40, "c" * 40  # origin/<stack>..<stack>, oldest first: A and C joined offline, B not
OA = "0" * 40  # origin/tdd/11-a as fetched; origin has no tdd/12-b
PR11, PR12 = "https://github.com/owner/repo/pull/11", "https://github.com/owner/repo/pull/12"
JOINED = {A: PR11 + " tdd/11-a\n", C: PR12 + " tdd/12-b\n"}


def joined_world(monkeypatch, tmp_path, trailers=JOINED, **kwargs):
    """A local stack three commits above origin's, A, B and C, two of them joined offline: A for tdd/11-a, on origin at
    OA, and C for tdd/12-b, which origin lacks."""
    return World(monkeypatch, tmp_path, commits=(A, B, C), trailers=trailers, branches={"tdd/11-a": OA}, **kwargs)


@pytest.mark.parametrize("case", ["pushed", "refused", "garbled"])
def test_each_joined_commit_is_pushed_to_its_branch_oldest_first_leased_on_origin_as_fetched_and_a_refused_lease_or_a_garbled_trailer_exits_1_the_stack_not_pushed(
        monkeypatch, tmp_path, run_cli, stack_recover, case):
    trailers = dict(JOINED, **{B: "not-a-url tdd/13-c\n"}) if case == "garbled" else JOINED
    pushes = {"refs/heads/tdd/11-a": (1, " ! [rejected]  a -> tdd/11-a (stale info)\n")} if case == "refused" else None
    world = joined_world(monkeypatch, tmp_path, trailers=trailers, pushes=pushes)

    code, out, err = run_cli(stack_recover, [])

    first = ("push", "--force-with-lease=tdd/11-a:" + OA, "origin", A + ":refs/heads/tdd/11-a")
    second = ("push", "--force-with-lease=tdd/12-b:", "origin", C + ":refs/heads/tdd/12-b")
    if case == "pushed":
        assert world.pushed[:2] == [first, second], err
    else:
        named = "tdd/11-a" if case == "refused" else B
        assert (code, out, err.count("\n"), named in err, world.pushed, world.scripts[-1][:2]) == (
            1, "", 1, True, [first] if case == "refused" else [], ("merge-lock.sh", "release")), err


@pytest.mark.parametrize("case, code", [("pushed", None), ("no joins", None), ("refused", 1), ("failed", 2)])
def test_then_the_stack_is_pushed_leased_on_origin_stack_as_fetched_never_forced_a_refused_lease_exit_1_another_failure_exit_2(
        monkeypatch, tmp_path, run_cli, stack_recover, case, code):
    said = {"refused": (1, " ! [rejected]  stack -> stack (stale info)\n"), "failed": (128, "fatal: the remote hung up\n")}
    world = joined_world(monkeypatch, tmp_path, trailers={} if case == "no joins" else JOINED,
                         pushes={"refs/heads/stack": said[case]} if case in said else None)

    got, out, err = run_cli(stack_recover, [])

    stack = ("push", "--force-with-lease=stack:" + BASE, "origin", TIP + ":refs/heads/stack")
    pushes = [args for args in world.pushed if "--delete" not in args]
    assert (pushes[-1], [arg for args in pushes for arg in args if arg in ("--force", "-f")]) == (stack, []), err
    if code:
        assert (got, out, err.count("\n"), "stack" in err, len(pushes)) == (code, "", 1, True, 3), err


def test_a_joined_pull_request_not_reading_merged_over_the_settle_window_exits_2_naming_it_and_its_last_state_the_stack_left_as_pushed(
        monkeypatch, tmp_path, run_cli, stack_recover):
    world = joined_world(monkeypatch, tmp_path, pulls={12: {"state": "open", "merged": False}})

    code, out, err = run_cli(stack_recover, [], env={"VERI_MERGE_SETTLE_READS": "2", "VERI_MERGE_SETTLE_SLEEP": "0"})

    reads = [call for call in world.log if call[0] == "gh"]
    assert (code, out, err.count("\n"), PR12 in err, "'open'" in err, reads) == (
        2, "", 1, True, True, [("gh", "repos/owner/repo/pulls/11"), ("gh", "repos/owner/repo/pulls/12"),
                               ("gh", "repos/owner/repo/pulls/12")]), err
    assert ([args for args in world.pushed if "--delete" in args], world.pushed[-1][-1], world.scripts[-1][:2]) == (
        [], TIP + ":refs/heads/stack", ("merge-lock.sh", "release")), err


def deletes(n, branch, sha):
    """The two deletes a joined run's cleanup pushes: its branch, leased on the commit pushed to it, and its records."""
    return [("git", "push", "--force-with-lease=%s:%s" % (branch, sha), "origin", "--delete", branch),
            ("git", "push", "origin", "--delete", "refs/veri/runs/%d" % n)]


def test_once_every_joined_pull_request_reads_merged_frees_the_lock_deletes_each_runs_branch_and_records_runs_stack_pr_sh_and_prints_the_tip_and_its_url(
        monkeypatch, tmp_path, run_cli, stack_recover):
    world = joined_world(monkeypatch, tmp_path)

    code, out, err = run_cli(stack_recover, [])

    release = ("merge-lock.sh", "release", "--pid", str(os.getpid()))
    tail = world.log[world.log.index(release):]
    assert (code, out, tail) == (
        0, "%s %s\n" % (TIP, URL), [release] + deletes(11, "tdd/11-a", A) + deletes(12, "tdd/12-b", C) + [
            ("stack-pr.sh",)]), err


@pytest.mark.parametrize("exit", [2, 3])
def test_stack_pr_sh_exiting_2_or_3_exits_2_naming_it_printing_nothing_the_pushes_and_deletes_kept(
        monkeypatch, tmp_path, run_cli, stack_recover, exit):
    world = joined_world(monkeypatch, tmp_path, answers={"stack-pr.sh": (exit, "")})

    code, out, err = run_cli(stack_recover, [])

    removed = [("git",) + args for args in world.pushed if "--delete" in args]
    assert (code, out, err.count("\n"), "stack-pr.sh exits %d" % exit in err, removed) == (
        2, "", 1, True, deletes(11, "tdd/11-a", A) + deletes(12, "tdd/12-b", C)), err


GONE = "error: unable to delete '%s': remote ref does not exist\n"


@pytest.mark.parametrize("pushes, code, named", [
    ({"tdd/11-a": (1, "error: failed to push some refs\n")}, 2, "tdd/11-a"),
    ({"refs/veri/runs/12": (128, "fatal: the remote end hung up\n")}, 2, "refs/veri/runs/12"),
    ({"tdd/11-a": (1, GONE % "tdd/11-a"), "refs/veri/runs/12": (1, GONE % "refs/veri/runs/12")}, 0, None),
], ids=["branch", "records", "already-gone"])
def test_a_failed_delete_exits_2_naming_it_printing_nothing_and_still_runs_stack_pr_sh_while_a_ref_already_gone_is_deleted(
        monkeypatch, tmp_path, run_cli, stack_recover, pushes, code, named):
    world = joined_world(monkeypatch, tmp_path, pushes=pushes)

    got, out, err = run_cli(stack_recover, [])

    assert (got, out, world.scripts[-1]) == (code, "" if code else "%s %s\n" % (TIP, URL), ("stack-pr.sh",)), err
    if named:
        assert [line for line in err.splitlines() if named in line] != [], err


NAMED = re.compile(r"ztrange|mario|ferreira|github\.com/\w|#[0-9]+|[\"'/](main|master)\b|[\"']stack[\"']"
                   r"|ready-for-agent|refactor-owed|author-read|[\"'](priority|bug|legacy|refactor)[\"']|gates",
                   re.IGNORECASE)


def test_stack_recover_and_its_shim_name_no_repository_issue_branch_label_or_person(stack_recover):
    shim = os.path.join(os.path.dirname(os.path.dirname(stack_recover.__file__)), "stack-recover.sh")
    named = []
    for path in (stack_recover.__file__, shim):
        with open(path, encoding="utf-8") as f:
            named += ["%s:%d: %s" % (os.path.basename(path), n, line) for n, line in enumerate(f, 1)
                      if NAMED.search(line)]

    assert named == []


@pytest.mark.parametrize("trailer", ["https://example.test/pull/11 tdd/11-a", PR11 + " tdd/11-a extra", PR11,
                                     PR11 + " tdd/11-a\n" + PR12 + " tdd/12-b"])
def test_a_trailer_whose_url_is_no_repositorys_pull_request_or_that_is_not_two_words_exits_1_naming_the_commit_nothing_pushed(
        monkeypatch, tmp_path, run_cli, stack_recover, trailer):
    world = joined_world(monkeypatch, tmp_path, trailers=dict(JOINED, **{A: trailer + "\n"}))

    code, out, err = run_cli(stack_recover, [])

    assert (code, out, err.count("\n"), A in err, world.pushed) == (1, "", 1, True, []), err


def test_a_joined_branch_naming_no_run_has_its_branch_deleted_and_no_records_ref(
        monkeypatch, tmp_path, run_cli, stack_recover):
    world = World(monkeypatch, tmp_path, commits=(A,), trailers={A: PR11 + " feature-a\n"})

    code, out, err = run_cli(stack_recover, [])

    assert (code, [args for args in world.pushed if "--delete" in args]) == (
        0, [("push", "--force-with-lease=feature-a:" + A, "origin", "--delete", "feature-a")]), err


def test_an_unusable_settle_window_tunable_exits_2_naming_it_before_any_read_or_lock(
        monkeypatch, tmp_path, run_cli, stack_recover):
    world = World(monkeypatch, tmp_path, named=AssertionError("stack-branch.sh was read"))

    code, out, err = run_cli(stack_recover, [], env={"VERI_MERGE_SETTLE_READS": "zero"})

    assert (code, out, err.count("\n"), "VERI_MERGE_SETTLE_READS" in err, world.log) == (2, "", 1, True, []), err


def test_a_failed_read_of_the_joined_range_exits_2_naming_it_nothing_pushed_the_lock_freed(
        monkeypatch, tmp_path, run_cli, stack_recover):
    world = joined_world(monkeypatch, tmp_path, log_fails=True)

    code, out, err = run_cli(stack_recover, [])

    assert (code, out, err.count("\n"), "origin/stack..stack" in err and "nothing pushed" in err, world.pushed,
            world.scripts[-1][:2]) == (2, "", 1, True, [], ("merge-lock.sh", "release")), err


@pytest.mark.parametrize("interrupt", [KeyboardInterrupt, SystemExit])
def test_an_interrupt_after_the_merge_lock_was_taken_frees_the_lock_before_it_ends_the_recovery(
        monkeypatch, tmp_path, stack_recover, interrupt):
    world = joined_world(monkeypatch, tmp_path)

    def interrupted(*args, cwd=None):
        raise interrupt()

    monkeypatch.setattr(importlib.import_module("veri.git"), "network", interrupted)

    with pytest.raises(interrupt):
        stack_recover.main([])

    assert [ran[:2] for ran in world.scripts] == [("merge-lock.sh", "take"), ("merge-lock.sh", "release")]


def test_a_pull_request_read_answering_no_json_or_no_json_object_is_read_again_within_the_settle_window(
        monkeypatch, tmp_path, run_cli, stack_recover):
    world = joined_world(monkeypatch, tmp_path, pulls={11: ["not json", "[1]", json.dumps({"merged": True})]})

    code, out, err = run_cli(stack_recover, [], env={"VERI_MERGE_SETTLE_READS": "3", "VERI_MERGE_SETTLE_SLEEP": "0"})

    reads = [call[1].rsplit("/", 1)[1] for call in world.log if call[0] == "gh"]
    assert (code, out, reads) == (0, "%s %s\n" % (TIP, URL), ["11", "11", "11", "12"]), err
