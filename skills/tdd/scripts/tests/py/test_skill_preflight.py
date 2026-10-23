"""How skills/tdd/SKILL.md's preflight checks launchability, budgets, GitHub, the worktree baseline and the conductor.pid lock, read as text."""
import functools
import pathlib
import re
import subprocess
import sys
import warnings

import pytest

import skill_sections

SKILL = pathlib.Path(__file__).resolve().parents[2].parent / "SKILL.md"

PREFLIGHT = "### 0. Preflight — baseline checks (bail before any cycle)"
RESUME = "## Resume"

FAST_CALL = "detect-test-command.sh --tier fast"
FULL_CALL = "detect-test-command.sh --tier all"
ITEM_RE = r"^[0-9]+\."


def all_lines():
    return SKILL.read_text().splitlines()


def lines_of(heading):
    return skill_sections.section(SKILL.with_name("RESUME.md") if heading == RESUME else SKILL, heading).splitlines()


def first(lines, want):
    return next((i for i, line in enumerate(lines) if want in line), None)


def first_all(lines, *wants, start=0):
    return next((i for i in range(start, len(lines)) if all(w in lines[i] for w in wants)), None)


def paragraph_around(lines, at):
    begin = at
    while begin > 0 and lines[begin - 1].strip() and not re.match(ITEM_RE, lines[begin]):
        begin -= 1
    end = at + 1
    while end < len(lines) and lines[end].strip() and not re.match(ITEM_RE, lines[end]):
        end += 1
    return lines[begin:end]


def sentences(lines):
    return re.sub(r"[.] ", ".\n", re.sub(r"  +", " ", " ".join(lines))).split("\n")


def test_skill_md_takes_the_full_tier_measurement_in_the_worktree_on_the_fast_tier_baseline_s_commit_and_sizes_leaf_timeout_sh_full_only_after_it():
    lines = lines_of(PREFLIGHT)
    fast_in, full_in = first(lines, FAST_CALL), first(lines, FULL_CALL)
    timeout_in = first_all(lines, "leaf-timeout.sh", "--full")
    assert fast_in is not None and full_in is not None, (fast_in, full_in)
    assert full_in >= fast_in, "the full tier is measured before the fast-tier baseline"
    moves = [line for line in lines[fast_in:full_in + 1]
             if re.search(r"(^|[^A-Za-z0-9_-])cd |git (checkout|switch|pull|fetch|reset|rebase)|issue-worktree\.sh", line)]
    assert moves == []
    assert timeout_in is not None, "no leaf-timeout.sh call with --full"
    assert timeout_in >= full_in, "the timeout is sized before the full-tier measurement"


def test_skill_md_says_a_resumed_run_s_baseline_runs_on_the_branch_head_in_its_existing_worktree_before_any_cycle():
    text = re.sub(r"  +", " ", " ".join(lines_of(RESUME)))
    says = [s for s in re.split(r"[.] ", text)
            if all(w in s.lower() for w in ("baseline", "branch head", "worktree", "cycle"))]
    assert says, "no sentence in Resume says the baseline runs on the branch head in its worktree before any cycle"


def test_skill_md_s_worktree_guard_prose_says_the_lock_is_taken_in_preflight_step_3_before_the_baseline_and_never_in_step_1_2():
    lines = all_lines()
    guard_at = first(lines, "**worktree guard**")
    assert guard_at is not None, "SKILL.md never names the worktree guard"
    says = [s for s in sentences(paragraph_around(lines, guard_at))
            if all(w in s.lower() for w in ("lock", "preflight step 3", "before the baseline"))]
    assert says, "the guard paragraph has no sentence naming the lock, 'preflight step 3' and 'before the baseline'"
    elsewhere = [s for s in sentences(lines)
                 if re.search(r"step 1\.2 (takes|writes|locks)|(taken|written|took|wrote) in step 1\.2", s, re.I)]
    assert elsewhere == []


DRAFT = "### 4. Draft PR"
REBASE_CALL = "rebase-onto-default.sh"


def test_1297_skill_md_s_draft_pr_step_does_not_write_the_resume_rebase_event():
    draft = lines_of(DRAFT)
    assert not [line for line in draft if re.search(r"event\.sh resume-rebase( |$|`)", line)], \
        "the Draft PR section also writes event.sh resume-rebase"


SCRIPTS = SKILL.parent / "scripts"


def git(cwd, *args):
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True)


def new_repo(path, *args):
    subprocess.run(["git", "init", "-q", "-b", "main", *args, str(path)], cwd=path.parent, check=True, capture_output=True)
    if "--bare" not in args:
        git(path, "config", "user.name", "Test")
        git(path, "config", "user.email", "test@example.com")


def commit_all(path, message):
    git(path, "add", "-A")
    git(path, "commit", "-q", "-m", message)


def run_discard(wt):
    return subprocess.run([str(SCRIPTS / "resume-clean.sh")], cwd=wt, capture_output=True, text=True)


def discard_stray(wt):
    return run_discard(wt).stdout


@pytest.mark.process("git: a bash-run discard block in a clone, then rebase-onto-default.sh over the default branch's new file")
def test_1420_skill_md_s_preflight_discard_removes_a_killed_leaf_s_untracked_file_at_a_path_the_default_branch_has_since_added_so_the_resume_rebase_onto_default_sh_exits_0_not_2(tmp_path):
    origin, seed, wt = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "wt"
    new_repo(origin, "--bare")
    new_repo(seed)
    (seed / "file.txt").write_text("base\n")
    commit_all(seed, "initial")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["git", "clone", "-q", str(origin), str(wt)], cwd=tmp_path, check=True, capture_output=True)
    git(wt, "config", "user.name", "veri")
    git(wt, "config", "user.email", "veri@example.test")
    git(wt, "checkout", "-q", "-b", "tdd/1-a-run")
    (wt / "work.txt").write_text("the run's work\n")
    commit_all(wt, "feat: a step's green commit (#1)")
    (seed / "other.txt").write_text("another run's work\n")
    commit_all(seed, "feat: another run merged (#2)")
    git(seed, "push", "-q", str(origin), "main")
    git(wt, "fetch", "-q", "origin")
    (wt / "other.txt").write_text("a killed leaf's half-written file\n")
    run_discard(wt)
    rebase = subprocess.run(["bash", str(SCRIPTS / REBASE_CALL)], cwd=wt, capture_output=True, text=True)
    assert rebase.returncode == 0, f"{REBASE_CALL} after the discard block, exit: want 0, got {rebase.returncode} - stderr: {rebase.stderr}"


@pytest.mark.process("git: a bash-run discard block in a repository holding an untracked file")
def test_1420_skill_md_s_preflight_discard_captures_a_killed_leaf_s_untracked_file_in_stray_before_removing_it_so_the_resuming_comment_names_it(tmp_path):
    wt = tmp_path / "wt"
    new_repo(wt)
    (wt / "file.txt").write_text("base\n")
    commit_all(wt, "initial")
    (wt / "other.txt").write_text("a killed leaf's half-written file\n")
    got = discard_stray(wt)
    assert "?? other.txt" in got.splitlines(), f"$stray does not list the untracked file: want a line '?? other.txt', got: {got}"


@pytest.mark.process("git: a bash-run discard block in a repository whose .gitignore names .tdd/")
def test_1420_skill_md_s_preflight_discard_never_removes_a_file_gitignore_ignores_so_a_tdd_leaf_log_survives_it(tmp_path):
    wt = tmp_path / "wt"
    new_repo(wt)
    (wt / ".gitignore").write_text(".tdd/\n")
    commit_all(wt, "initial")
    (wt / ".tdd").mkdir()
    (wt / ".tdd" / "issue-1-leaf.log").write_text("a leaf's log\n")
    run_discard(wt)
    assert (wt / ".tdd" / "issue-1-leaf.log").is_file(), "the discard block removed the ignored run-state file .tdd/issue-1-leaf.log"


@pytest.mark.process("git: a bash-run discard block under the repository's own .tdd ignore patterns")
def test_1420_skill_md_s_preflight_discard_never_loses_an_untracked_tdd_run_state_file_the_real_gitignore_un_ignores_the_refactor_owed_file_survives_uncaptured(tmp_path):
    wt = tmp_path / "wt"
    new_repo(wt)
    (wt / ".gitignore").write_text(".tdd/*\n!.tdd/issue-*.md\n.tdd/issue-*-spec.md\n")
    (wt / ".tdd").mkdir()
    (wt / ".tdd" / "issue-1.md").write_text("- [x] step one\n")
    commit_all(wt, "initial")
    (wt / ".tdd" / "issue-1-refactor-owed.md").write_text("a refactor the run owes\n")
    got = discard_stray(wt)
    assert (wt / ".tdd" / "issue-1-refactor-owed.md").is_file(), "the discard block removed the untracked run-state file .tdd/issue-1-refactor-owed.md"
    assert "issue-1-refactor-owed.md" not in got, f"$stray captures the run-state file as a stray: {got}"


TESTS_DIR = pathlib.Path(__file__).resolve().parent
MECHANICAL_READERS = (
    "full_tier_measurement_in_the_worktree",
    "test_1420_skill_md_s_preflight_discard",
    "test_1967_preflight_step_3_resumed_run_block_is_one_resume_clean_sh_call",
    "skill_md_preflight_leaf_model_calls_name_a_leaf",
    "test_skill_preflight_writes_the_long_lived_ppid_not_the_shells_pid",
    "test_987_preflight_step_3_runs_stop_requested_clear_beside_the_tdd_conductor_pid_write",
    "structural_pass_ends_with_one_event_sh_structural_pass_mark",
    "test_954_skill_md_makes_the_leaf_timeout_sh_call_that_records_tdd_issue_n_timeout",
    "test_1297_skill_md_s_draft_pr_step_does_not_write_the_resume_rebase_event",
    "test_a_gh_auth_status_call_planted_in_skill_md_is_named_as_file_line",
    "test_every_remaining_case_that_reads_skill_md_s_preflight_section",
    "test_2220_sweep_flags_a_case_reading_the_preflight_section",
    "test_2220_sweep_flags_a_case_reading_a_phrase_only_the_preflight_section",
)
NAMES_PREFLIGHT = re.compile(r"^PREFLIGHT$|#+ .*[Pp]reflight|#+ 0\.|Preflight —")


def plain(text):
    return "\n".join(" ".join(line.replace("`", "").replace("*", "").split()).lower() for line in text.splitlines())


def preflight_and_rest():
    lines = SKILL.read_text().splitlines()
    start = next(i for i, line in enumerate(lines) if line == PREFLIGHT)
    end = next(i for i in range(start + 1, len(lines)) if re.match(r"#{1,3} ", lines[i]))
    preflight, rest = plain("\n".join(lines[start:end])), plain("\n".join(lines[:start] + lines[end:]))
    flat = lambda text: " " + " ".join(text.split()) + " "  # padded, so ^ and $ never match a section edge
    return (preflight, flat(preflight)), (rest, flat(rest))


@functools.cache
def only_in_preflight(value, preflight, rest):
    """preflight and rest are each (line by line, all whitespace flattened): a phrase that wraps a line in SKILL.md
    matches only the flattened form, a ^-anchored item pattern only the line-by-line one."""
    if NAMES_PREFLIGHT.search(value):
        return True
    probe = " ".join(value.split())
    if len(probe.split(" ")) < 3:
        return False
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            pattern = re.compile(probe, re.I | re.M)
    except re.error:
        pattern = None
    for inside, outside in zip(preflight, rest):
        if plain(probe) in inside and plain(probe) not in outside:
            return True
        if pattern and pattern.search(inside) and not pattern.search(outside):
            return True
    return False


STRING_ASSIGNMENT = re.compile(r"\w+\s*=\s*[rRbBuU]*['\"]")


def preflight_readers(walk, preflight, rest):
    defs = {d.name: d for d in walk.definitions if d.segment.startswith("def ")}
    consts = {d.name: d.literals[0] for d in walk.definitions
              if not d.names and len(d.literals) == 1 and STRING_ASSIGNMENT.match(d.segment)}

    def reads(fn, seen):
        if fn.name in seen:
            return False
        seen.add(fn.name)
        for name in fn.names:
            if NAMES_PREFLIGHT.search(name):
                return True
            if name in consts and only_in_preflight(consts[name], preflight, rest):
                return True
            if name in defs and reads(defs[name], seen):
                return True
        return any(only_in_preflight(value, preflight, rest) for value in fn.constants)

    return [name for name, fn in defs.items() if name.startswith("test_") and reads(fn, set())]


def stray_cases(entries, allowed):
    preflight, rest = preflight_and_rest()
    strays = []
    for entry in entries:
        path = entry.path
        if "SKILL" not in entry.text:
            continue
        for name in preflight_readers(entry.walk, preflight, rest):
            if not any(key in name for key in allowed):
                strays.append(f"{path.relative_to(TESTS_DIR)}::{name}")
    return strays


@pytest.mark.tree_audit("every test module under tests/py, parsed for the cases that read SKILL.md's Preflight section")
def test_every_remaining_case_that_reads_skill_md_s_preflight_section_is_a_named_mechanical_fact_case(tests_py_index):
    strays = stray_cases(tests_py_index, MECHANICAL_READERS)
    assert strays == [], f"cases read the Preflight section but are not on the mechanical-fact allow-list: {strays}"


def test_2220_sweep_flags_a_case_reading_the_preflight_section_until_it_is_on_the_allow_list(tmp_path, monkeypatch):
    from conftest import TestFile
    module = tmp_path / "test_synthetic_reader.py"
    module.write_text(
        'SKILL_MD = "SKILL.md"\n\n\n'
        'def test_reads_the_preflight_section():\n'
        '    assert PREFLIGHT in SKILL_MD\n',
        encoding="utf-8")
    monkeypatch.setattr(sys.modules[__name__], "TESTS_DIR", tmp_path)
    entries = [TestFile(module)]
    key = "test_synthetic_reader.py::test_reads_the_preflight_section"

    assert stray_cases(entries, []) == [key]
    assert stray_cases(entries, ["test_reads_the_preflight_section"]) == []


def test_2220_sweep_flags_a_case_reading_a_phrase_only_the_preflight_section_holds_until_it_is_on_the_allow_list(
        tmp_path, monkeypatch):
    from conftest import TestFile
    (preflight, _), (rest, _) = preflight_and_rest()
    phrase = next(
        line for line in preflight.splitlines()
        if len(line.split()) >= 4 and not re.search(r"['\"\\{}]", line) and line not in rest
        and not NAMES_PREFLIGHT.search(line))
    module = tmp_path / "test_synthetic_reader.py"
    module.write_text(
        'SKILL_MD = "SKILL.md"\n\n\n'
        'def test_reads_a_preflight_phrase():\n'
        '    assert "%s" in SKILL_MD\n' % phrase,
        encoding="utf-8")
    monkeypatch.setattr(sys.modules[__name__], "TESTS_DIR", tmp_path)
    entries = [TestFile(module)]
    key = "test_synthetic_reader.py::test_reads_a_preflight_phrase"

    assert stray_cases(entries, []) == [key]
    assert stray_cases(entries, ["test_reads_a_preflight_phrase"]) == []
