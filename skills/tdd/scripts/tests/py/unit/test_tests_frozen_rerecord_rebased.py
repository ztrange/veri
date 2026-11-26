"""In-process rerecord-rebased cases on a history committed through fed_commits (PRD 017.10).

A process case cloned origin, branched, committed upstream, pushed and ran `git rebase origin/main`. Here the branch
is committed, `checkout` returns to the fork point (the branch's commits stay readable, as the pre-rebase sha does),
upstream is committed and `ref("origin/main")` names it, and the branch's commits are committed again as the rebase
left them: a commit whose patch upstream already holds is gone, the others carry upstream's lines they did not touch.
"""
import importlib

import pytest


@pytest.fixture
def tests_frozen():
    return importlib.import_module("veri.tests_frozen")


# Names, not literals, in calls: a literal suite path reads as a nested run.
SUITE = "tests/test_suite.py"
GO_SUITE = "tests/suite_test.go"
LEDGER = ".tdd/ledger.md"
CASE = "def test_config_2552():\n    assert f() == %d\n"
WIDE = "def test_config_2552():\n    a = %d\n    b = 0\n    c = 0\n    d = 0\n    assert f() == %d\n"
EARLIER, CURRENT = "step one pins the config", "step two adds another"


def _write(root, files):
    for path, text in files.items():
        (root / path).write_text(text)


def _origin(root, fed_commits, files):
    """root holding tests/ and .tdd/, `files` committed as "base", which origin/main (default main) names."""
    (root / "tests").mkdir(parents=True)
    (root / ".tdd").mkdir()
    _write(root, files)
    repo = fed_commits(root=root, default="main")
    repo.add("tests")
    base = repo.commit("base")
    repo.ref("origin/main")
    return repo, base


def _commit(root, repo, subject, files):
    """As writing `files`, git add of each, and git commit -m <subject>."""
    _write(root, files)
    repo.add(*files)
    return repo.commit(subject)


def _rebase(root, repo, base, upstream, rebased):
    """As git checkout main, the `upstream` commits, git push origin main, git checkout work and git rebase
    origin/main, the branch's commits left as `rebased` states them; returns the pre-rebase head."""
    before = repo.head
    repo.checkout(base)
    for subject, files in upstream:
        _commit(root, repo, subject, files)
    repo.ref("origin/main")
    for subject, files in rebased:
        _commit(root, repo, subject, files)
    return before


def _upstream_only(root, run_cli, tests_frozen, fed_commits, steps=(EARLIER, CURRENT), lib=True):
    """Step one pins CASE % 2 and, when `lib`, step two adds lib.py; upstream sets the case to 2, then 3, so the rebase
    drops step one (upstream holds its patch) and the case at HEAD is upstream's."""
    repo, base = _origin(root, fed_commits, {SUITE: CASE % 1})
    (root / SUITE).write_text(CASE % 2)
    run_cli(tests_frozen, ["record", "--step", EARLIER, SUITE], cwd=root)
    _commit(root, repo, "step one", {SUITE: CASE % 2})
    if lib:
        _commit(root, repo, "step two", {"lib.py": "one\n"})
    (root / LEDGER).write_text("".join("- [x] %s\n" % step for step in steps[:-1]) + "- [ ] %s\n" % steps[-1])
    before = _rebase(root, repo, base, [("upstream 2", {SUITE: CASE % 2}), ("upstream 3", {SUITE: CASE % 3})],
                     [("step two", {"lib.py": "one\n"})] if lib else [])
    return repo, before


def test_rerecord_rebased_re_records_an_earlier_case_changed_only_upstream_so_check_earlier_exits_0_2552(
        tmp_path, run_cli, tests_frozen, fed_commits):
    repo = tmp_path / "repo"
    _, before = _upstream_only(repo, run_cli, tests_frozen, fed_commits)
    ledger = repo / LEDGER
    stale = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", CURRENT], cwd=repo)[0]

    code, _, _ = run_cli(tests_frozen, ["rerecord-rebased", str(ledger), before], cwd=repo)
    after = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", CURRENT], cwd=repo)[0]
    usage = run_cli(tests_frozen, [], cwd=repo)[2]

    assert (stale, code, after) == (1, 0, 0)
    assert "rerecord-rebased" in usage


def test_rerecord_rebased_run_from_a_subdirectory_re_records_the_same_upstream_only_case_2552(
        tmp_path, run_cli, tests_frozen, fed_commits):
    repo = tmp_path / "repo"
    _, before = _upstream_only(repo, run_cli, tests_frozen, fed_commits)
    ledger = repo / LEDGER
    stale = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", CURRENT], cwd=repo)[0]

    code, _, _ = run_cli(tests_frozen, ["rerecord-rebased", "../" + LEDGER, before], cwd=repo / "tests")
    after = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", CURRENT], cwd=repo)[0]

    assert (stale, code, after) == (1, 0, 0)


def _refused(root, run_cli, tests_frozen, fed_commits, step_two, rebased):
    """Step one pins WIDE % (5, 1); `step_two` is the second branch commit's files; upstream sets WIDE % (1, 3)."""
    repo, base = _origin(root, fed_commits, {SUITE: WIDE % (1, 1)})
    (root / SUITE).write_text(WIDE % (5, 1))
    run_cli(tests_frozen, ["record", "--step", EARLIER, SUITE], cwd=root)
    _commit(root, repo, "step one", {SUITE: WIDE % (5, 1)})
    _commit(root, repo, "step two", step_two)
    (root / LEDGER).write_text("- [x] %s\n- [ ] %s\n" % (EARLIER, CURRENT))
    return _rebase(root, repo, base, [("upstream", {SUITE: WIDE % (1, 3)})], rebased)


def test_rerecord_rebased_refuses_a_stale_case_the_branch_changed_since_its_record_and_names_it_2552(
        tmp_path, run_cli, tests_frozen, fed_commits):
    repo = tmp_path / "repo"
    before = _refused(repo, run_cli, tests_frozen, fed_commits, {SUITE: WIDE % (9, 1)},
                      [("step one", {SUITE: WIDE % (5, 3)}), ("step two", {SUITE: WIDE % (9, 3)})])
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(repo / LEDGER), before], cwd=repo)

    assert (code, record.read_bytes()) == (1, old)
    assert out.splitlines() == ["test_config_2552 (%s)" % EARLIER]


def test_rerecord_rebased_refuses_a_stale_case_the_branch_and_origin_both_edited_identically_since_its_record_because_its_pre_rebase_body_no_longer_matches_2552(
        tmp_path, run_cli, tests_frozen, fed_commits):
    repo = tmp_path / "repo"
    before = _refused(repo, run_cli, tests_frozen, fed_commits, {SUITE: WIDE % (1, 3), "lib.py": "one\n"},
                      [("step one", {SUITE: WIDE % (5, 3)}),
                       ("step two edits the frozen case as origin will", {SUITE: WIDE % (1, 3), "lib.py": "one\n"})])
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(repo / LEDGER), before], cwd=repo)

    assert (code, record.read_bytes()) == (1, old)
    assert out.splitlines() == ["test_config_2552 (%s)" % EARLIER]


def test_rerecord_rebased_refuses_a_stale_case_whose_head_body_differs_from_origins_though_the_record_matched_before_the_rebase_2552(
        tmp_path, run_cli, tests_frozen, fed_commits):
    repo = tmp_path / "repo"
    before = _refused(repo, run_cli, tests_frozen, fed_commits, {"lib.py": "one\n"},
                      [("step one", {SUITE: WIDE % (5, 3)}), ("step two", {"lib.py": "one\n"})])
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(repo / LEDGER), before], cwd=repo)

    assert (code, record.read_bytes()) == (1, old)
    assert out.splitlines() == ["test_config_2552 (%s)" % EARLIER]


def test_rerecord_rebased_exits_1_naming_only_the_refused_case_while_re_recording_the_other_stale_one_2552(
        tmp_path, run_cli, tests_frozen, fed_commits):
    repo = tmp_path / "repo"
    case = "def test_%s_2552():\n    a = %d\n    b = 0\n    c = 0\n    d = 0\n    assert f() == %d\n"
    suites = {name: "tests/test_%s.py" % name for name in ("kept", "refused")}
    fed, base = _origin(repo, fed_commits, {suite: case % (name, 1, 1) for name, suite in suites.items()})
    steps = {"kept": "step one pins the kept case", "refused": "step two pins the refused case"}
    current = "step three adds another"
    for name, suite in suites.items():
        (repo / suite).write_text(case % (name, 5 if name == "refused" else 1, 2 if name == "kept" else 1))
        run_cli(tests_frozen, ["record", "--step", steps[name], suite], cwd=repo)
        fed.add("tests")
        fed.commit("step " + name)
    _commit(repo, fed, "step three edits the refused case", {suites["refused"]: case % ("refused", 9, 1)})
    (repo / LEDGER).write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (steps["kept"], steps["refused"], current))
    before = _rebase(repo, fed, base, [
        ("upstream 2", {suites["kept"]: case % ("kept", 1, 2)}),
        ("upstream 3", {suite: case % (name, 1, 3) for name, suite in suites.items()})], [
        ("step refused", {suites["refused"]: case % ("refused", 5, 3)}),
        ("step three edits the refused case", {suites["refused"]: case % ("refused", 9, 3)})])
    records = sorted((repo / ".tdd").glob("tests-frozen-*.record"))
    old = {path: path.read_bytes() for path in records}

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(repo / LEDGER), before], cwd=repo)

    changed = [path for path in records if path.read_bytes() != old[path]]
    kept_check = run_cli(tests_frozen, ["check-earlier", str(repo / LEDGER), "--step", current], cwd=repo)[1]
    assert (code, len(changed)) == (1, 1)
    assert out.splitlines() == ["test_refused_2552 (%s)" % steps["refused"]]
    assert "test_kept_2552" not in kept_check


def test_rerecord_rebased_exits_3_and_rewrites_no_record_when_no_earlier_recorded_case_is_stale_2552(
        tmp_path, run_cli, tests_frozen, fed_commits):
    repo = tmp_path / "repo"
    case = "def test_config_2552():\n    a = 1\n    b = 0\n    c = 0\n    d = 0\n    assert f() == %d\n"
    fed, base = _origin(repo, fed_commits, {SUITE: case % 1})
    (repo / SUITE).write_text(case % 2)
    run_cli(tests_frozen, ["record", "--step", EARLIER, SUITE], cwd=repo)
    _commit(repo, fed, "step one", {SUITE: case % 2})
    (repo / LEDGER).write_text("- [x] %s\n- [ ] %s\n" % (EARLIER, CURRENT))
    before = _rebase(repo, fed, base, [("upstream", {"README.md": "upstream\n"})], [("step one", {SUITE: case % 2})])
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(repo / LEDGER), before], cwd=repo)

    assert (code, out, record.read_bytes()) == (3, "", old)


CASE_3150 = "def test_config_3150():\n    a = 1\n    b = 0\n    c = 0\n    d = 0\n    assert f() == %d\n"
OLDER, LATER, CURRENT_3150 = "step one pins the config", "step two repins the config", "step three adds another"


def _two_owners(root, run_cli, tests_frozen, fed_commits):
    """Step one records CASE_3150 % 2 and step two % 3, committed together at % 3; returns (fed log, base, the
    older step's record, the later step's record)."""
    repo, base = _origin(root, fed_commits, {SUITE: CASE_3150 % 1})
    (root / SUITE).write_text(CASE_3150 % 2)
    run_cli(tests_frozen, ["record", "--step", OLDER, SUITE], cwd=root)
    (older_record,) = (root / ".tdd").glob("tests-frozen-*.record")
    (root / SUITE).write_text(CASE_3150 % 3)
    run_cli(tests_frozen, ["record", "--step", LATER, SUITE], cwd=root)
    (later_record,) = set((root / ".tdd").glob("tests-frozen-*.record")) - {older_record}
    _commit(root, repo, "steps one and two", {SUITE: CASE_3150 % 3})
    (root / LEDGER).write_text("- [x] %s\n- [x] %s\n- [ ] %s\n" % (OLDER, LATER, CURRENT_3150))
    return repo, base, older_record, later_record


def test_rerecord_rebased_exits_3_printing_nothing_for_a_case_whose_older_owners_superseded_record_is_stale_and_check_earlier_passes_3150(
        tmp_path, run_cli, tests_frozen, fed_commits):
    repo = tmp_path / "repo"
    fed, base, _, _ = _two_owners(repo, run_cli, tests_frozen, fed_commits)
    before = _rebase(repo, fed, base, [("upstream", {"README.md": "upstream\n"})],
                     [("steps one and two", {SUITE: CASE_3150 % 3})])
    ledger = repo / LEDGER

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(ledger), before], cwd=repo)
    earlier_code, earlier_out, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", CURRENT_3150],
                                           cwd=repo)

    assert (code, out, earlier_code, earlier_out) == (3, "", 0, "")


def test_rerecord_rebased_exits_1_naming_the_latest_owning_step_and_not_the_older_one_when_the_branch_changed_the_body_3150(
        tmp_path, run_cli, tests_frozen, fed_commits):
    repo = tmp_path / "repo"
    fed, base, _, _ = _two_owners(repo, run_cli, tests_frozen, fed_commits)
    _commit(repo, fed, "step three edits the case", {SUITE: CASE_3150 % 4})
    before = _rebase(repo, fed, base, [("upstream", {"README.md": "upstream\n"})],
                     [("steps one and two", {SUITE: CASE_3150 % 3}), ("step three edits the case", {SUITE: CASE_3150 % 4})])
    ledger = repo / LEDGER

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(ledger), before], cwd=repo)

    assert (code, out.splitlines()) == (1, ["test_config_3150 (%s)" % LATER])


def test_rerecord_rebased_re_records_the_latest_owners_record_and_leaves_the_older_steps_record_untouched_when_the_default_branch_changed_the_body_3150(
        tmp_path, run_cli, tests_frozen, fed_commits):
    repo = tmp_path / "repo"
    fed, base, older_record, later_record = _two_owners(repo, run_cli, tests_frozen, fed_commits)
    # Upstream already holds the branch's one change, so the rebase leaves no commit of the branch.
    before = _rebase(repo, fed, base, [("upstream changes the body", {SUITE: (CASE_3150 % 3).replace("a = 1", "a = 9")})],
                     [])
    ledger = repo / LEDGER
    older_bytes, later_bytes = older_record.read_bytes(), later_record.read_bytes()

    code, _, _ = run_cli(tests_frozen, ["rerecord-rebased", str(ledger), before], cwd=repo)
    earlier_code, _, _ = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", CURRENT_3150], cwd=repo)

    assert (code, older_record.read_bytes() == older_bytes, later_record.read_bytes() != later_bytes,
            earlier_code) == (0, True, True, 0)


def test_rerecord_rebased_skips_a_ticked_earlier_step_with_no_record_file_and_still_re_records_the_stale_one_2552(
        tmp_path, run_cli, tests_frozen, fed_commits):
    repo = tmp_path / "repo"
    _, before = _upstream_only(repo, run_cli, tests_frozen, fed_commits,
                               steps=("step zero recorded nothing", EARLIER, CURRENT), lib=False)
    ledger = repo / LEDGER

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(ledger), before], cwd=repo)
    after = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", CURRENT], cwd=repo)[0]

    assert (code, out, after) == (0, "", 0)


def test_rerecord_rebased_exits_2_naming_an_unreadable_ledger_on_stderr_and_writes_no_record_2552(
        tmp_path, run_cli, tests_frozen, fed_commits):
    repo = tmp_path / "repo"
    fed, _ = _origin(repo, fed_commits, {SUITE: "def test_config_2552():\n    assert f() == 1\n"})
    run_cli(tests_frozen, ["record", "--step", "step one pins the config", SUITE], cwd=repo)
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()
    ledger = repo / ".tdd/unreadable-ledger.md"
    ledger.mkdir()

    code, out, err = run_cli(tests_frozen, ["rerecord-rebased", str(ledger), fed.head], cwd=repo)

    assert (code, out, record.read_bytes()) == (2, "", old)
    assert str(ledger) in err


def test_rerecord_rebased_with_no_ledger_file_exits_3_with_no_output_and_rewrites_no_record_2718(
        tmp_path, run_cli, tests_frozen, fed_commits):
    repo = tmp_path / "repo"
    fed, _ = _origin(repo, fed_commits, {SUITE: "def test_config_2718():\n    assert f() == 1\n"})
    run_cli(tests_frozen, ["record", "--step", "step one pins the config", SUITE], cwd=repo)
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(repo / ".tdd/no-ledger-yet.md"), fed.head], cwd=repo)

    assert (code, out, record.read_bytes()) == (3, "", old)


def test_rerecord_rebased_exits_2_and_rewrites_no_record_when_the_pre_rebase_sha_names_no_commit_2552(
        tmp_path, run_cli, tests_frozen, fed_commits):
    repo = tmp_path / "repo"
    _upstream_only(repo, run_cli, tests_frozen, fed_commits, lib=False)
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()

    code, out, _ = run_cli(tests_frozen, ["rerecord-rebased", str(repo / LEDGER), "0" * 40], cwd=repo)

    assert (code, out, record.read_bytes()) == (2, "", old)


def test_rerecord_rebased_exits_2_naming_the_record_when_an_earlier_steps_record_exists_but_cannot_be_read_2552(
        tmp_path, run_cli, tests_frozen, fed_commits):
    repo = tmp_path / "repo"
    fed, _ = _origin(repo, fed_commits, {SUITE: "def test_config_2552():\n    assert f() == 1\n"})
    run_cli(tests_frozen, ["record", "--step", EARLIER, SUITE], cwd=repo)
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    record.unlink()
    record.mkdir()
    (repo / LEDGER).write_text("- [x] %s\n- [ ] %s\n" % (EARLIER, CURRENT))

    code, out, err = run_cli(tests_frozen, ["rerecord-rebased", str(repo / LEDGER), fed.head], cwd=repo)

    assert (code, out, record.name in err) == (2, "", True)


def test_rerecord_rebased_exits_2_naming_the_record_when_writing_a_stale_cases_re_record_raises_2552(
        tmp_path, run_cli, tests_frozen, fed_commits, monkeypatch, capfd):
    repo = tmp_path / "repo"
    _, before = _upstream_only(repo, run_cli, tests_frozen, fed_commits, lib=False)
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()

    def refusing_open(name, mode="r", *rest, **kwargs):
        if "w" in mode and str(name).endswith(record.name):
            raise OSError(28, "No space left on device", str(name))
        return open(name, mode, *rest, **kwargs)

    monkeypatch.setattr(tests_frozen, "open", refusing_open, raising=False)
    monkeypatch.chdir(repo)

    code = tests_frozen.rerecord_rebased(str(repo / LEDGER), before)

    assert (code, record.name in capfd.readouterr().err, record.read_bytes() == old) == (2, True, True)


def test_rerecord_rebased_exits_2_naming_the_record_when_writing_a_stale_cases_re_record_raises_file_not_found_so_it_is_not_read_as_a_missing_ledger_2718(
        tmp_path, run_cli, tests_frozen, fed_commits, monkeypatch, capfd):
    repo = tmp_path / "repo"
    _, before = _upstream_only(repo, run_cli, tests_frozen, fed_commits, lib=False)
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    old = record.read_bytes()

    def refusing_open(name, mode="r", *rest, **kwargs):
        if "w" in mode and str(name).endswith(record.name):
            raise FileNotFoundError(2, "No such file or directory", str(name))
        return open(name, mode, *rest, **kwargs)

    monkeypatch.setattr(tests_frozen, "open", refusing_open, raising=False)
    monkeypatch.chdir(repo)

    code = tests_frozen.rerecord_rebased(str(repo / LEDGER), before)

    assert (code, record.name in capfd.readouterr().err, record.read_bytes() == old) == (2, True, True)


def test_rerecord_rebased_exits_2_naming_the_record_and_the_title_when_an_earlier_steps_recorded_case_is_missing_at_head_2825(
        tmp_path, run_cli, tests_frozen, fed_commits):
    repo = tmp_path / "repo"
    other = "def test_other_2825():\n    assert f() == 0\n"
    fed, _ = _origin(repo, fed_commits, {SUITE: other})
    (repo / SUITE).write_text(other + "\n\ndef test_config_before_rename_2825():\n    assert f() == 1\n")
    run_cli(tests_frozen, ["record", "--step", EARLIER, SUITE], cwd=repo)
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
    pre = fed.commit("step one", all=True)
    (repo / SUITE).write_text(other + "\n\ndef test_config_after_rename_2825():\n    assert f() == 1\n")
    fed.commit("rename", all=True)
    (repo / LEDGER).write_text("- [x] %s\n- [ ] %s\n" % (EARLIER, CURRENT))

    code, _, err = run_cli(tests_frozen, ["rerecord-rebased", str(repo / LEDGER), pre], cwd=repo)

    assert (code, record.name in err, "test_config_before_rename_2825" in err, "KeyError" in err) == (
        2, True, True, False)


KEPT_2994 = "def test_kept_2994():\n    a = 1\n    b = 0\n    c = 0\n    d = 0\n    assert f() == 1\n"
GHOST_2994 = "\n\ndef test_ghost_2994():\n    assert f() == 2\n"


def _ghost(root, run_cli, tests_frozen, fed_commits, suite, base_text, kept, ghost, step, edit_record=None):
    """Step one records `kept` and `ghost` in `suite` but commits `kept` only; upstream adds README.md, which the
    rebased step one sits on. Returns the pre-rebase head."""
    repo, base = _origin(root, fed_commits, {suite: base_text})
    (root / suite).write_text(kept + ghost)
    run_cli(tests_frozen, ["record", "--step", step, suite], cwd=root)
    if edit_record:
        edit_record()
    _commit(root, repo, "step one", {suite: kept})
    (root / LEDGER).write_text("- [x] %s\n- [ ] %s\n" % (step, CURRENT))
    return _rebase(root, repo, base, [("upstream", {"README.md": "upstream\n"})], [("step one", {suite: kept})])


def test_rerecord_rebased_drops_a_recorded_case_never_committed_on_the_branch_instead_of_exiting_2_2994(
        tmp_path, run_cli, tests_frozen, fed_commits):
    repo = tmp_path / "repo"
    before = _ghost(repo, run_cli, tests_frozen, fed_commits, SUITE, "", KEPT_2994, GHOST_2994,
                    "step one pins the kept case")
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")

    code, _, _ = run_cli(tests_frozen, ["rerecord-rebased", str(repo / LEDGER), before], cwd=repo)

    assert (code in (0, 3), "test_ghost_2994" in record.read_text()) == (True, False)


def test_rerecord_rebased_drops_the_helpers_line_of_a_recorded_go_case_never_committed_on_the_branch_2994(
        tmp_path, run_cli, tests_frozen, fed_commits):
    repo = tmp_path / "repo"
    kept = "func TestKept(t *testing.T) {\n\tx := 1\n\tif x != 1 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n"
    ghost = "\nfunc TestGhost(t *testing.T) {\n\tx := 2\n\tif x != 2 {\n\t\tt.Fatal(\"bad\")\n\t}\n}\n"

    def stale_helpers_line():
        (record,) = (repo / ".tdd").glob("tests-frozen-*.record")
        lines = record.read_text().splitlines(keepends=True)
        at = next(i for i, line in enumerate(lines) if line.startswith("case: TestGhost")) + 1
        record.write_text("".join(lines[:at + 1] + ["helpers: tests/suite_test.go\tTestGhost\t%s\n" % ("a" * 64)]
                                  + lines[at + 1:]))

    before = _ghost(repo, run_cli, tests_frozen, fed_commits, GO_SUITE, "", kept, ghost,
                    "step one pins the kept case", edit_record=stale_helpers_line)
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")

    code, _, _ = run_cli(tests_frozen, ["rerecord-rebased", str(repo / LEDGER), before], cwd=repo)

    assert (code in (0, 3), "TestGhost" in record.read_text(), "a" * 64 in record.read_text()) == (
        True, False, False)


def test_rerecord_rebased_drops_only_the_never_committed_case_and_still_re_records_the_upstream_only_changed_one_2994(
        tmp_path, run_cli, tests_frozen, fed_commits):
    repo = tmp_path / "repo"
    case = "def test_config_2994():\n    assert f() == %d\n"
    fed, base = _origin(repo, fed_commits, {SUITE: case % 1})
    (repo / SUITE).write_text(case % 2 + "\n\ndef test_ghost_2994():\n    assert f() == 9\n")
    run_cli(tests_frozen, ["record", "--step", EARLIER, SUITE], cwd=repo)
    _commit(repo, fed, "step one", {SUITE: case % 2})
    (repo / LEDGER).write_text("- [x] %s\n- [ ] %s\n" % (EARLIER, CURRENT))
    # Upstream 2 holds step one's patch, so the rebase leaves no commit of the branch.
    before = _rebase(repo, fed, base, [("upstream 2", {SUITE: case % 2}), ("upstream 3", {SUITE: case % 3})], [])
    ledger = repo / LEDGER
    (record,) = (repo / ".tdd").glob("tests-frozen-*.record")

    code, _, _ = run_cli(tests_frozen, ["rerecord-rebased", str(ledger), before], cwd=repo)
    after = run_cli(tests_frozen, ["check-earlier", str(ledger), "--step", CURRENT], cwd=repo)[0]

    text = record.read_text()
    assert (code, "test_config_2994" in text, "test_ghost_2994" in text, after) == (0, True, False, 0)


def test_rerecord_rebased_still_exits_2_for_a_recorded_case_committed_at_the_pre_rebase_sha_and_gone_at_head_2994(
        tmp_path, run_cli, tests_frozen, fed_commits):
    repo = tmp_path / "repo"
    fed, base = _origin(repo, fed_commits, {SUITE: KEPT_2994})
    step = "step one pins the kept case"
    (repo / SUITE).write_text(KEPT_2994 + GHOST_2994)
    run_cli(tests_frozen, ["record", "--step", step, SUITE], cwd=repo)
    with_ghost = fed.commit("step one adds the ghost", all=True)
    (repo / SUITE).write_text(KEPT_2994)
    fed.commit("a later commit removes the ghost", all=True)
    (repo / LEDGER).write_text("- [x] %s\n- [ ] %s\n" % (step, CURRENT))
    _rebase(repo, fed, base, [("upstream", {"README.md": "upstream\n"})],
            [("step one adds the ghost", {SUITE: KEPT_2994 + GHOST_2994}),
             ("a later commit removes the ghost", {SUITE: KEPT_2994})])

    code, _, err = run_cli(tests_frozen, ["rerecord-rebased", str(repo / LEDGER), with_ghost], cwd=repo)

    assert (code, "names case test_ghost_2994, which tests/test_suite.py does not hold at HEAD" in err) == (2, True)
